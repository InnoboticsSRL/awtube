#!/usr/bin/env python3

""" Commanders for commander pattern. """

from __future__ import annotations
from abc import ABC, abstractmethod
import time
import copy
import asyncio
import queue
from queue import Queue
import logging
from contextlib import suppress
from enum import IntEnum
from typing import AsyncGenerator, Callable, NamedTuple

from sympy import false, true
from awtube import command_receiver
from awtube import observers

import awtube.logging_config

import awtube.commands as commands
import awtube.types as types
from awtube.commands import Command, MachineStateCommad, HeartbeatCommad, \
    KinematicsConfigurationCommad, MachineTargetCommad
from awtube.observers import StreamObserver, StatusObserver, Observer
from awtube.types import StreamState
from awtube.types import FunctionResult
from awtube.command_receiver import CommandReceiver
from awtube.types import MachineTarget
from awtube.cia402 import transition, device_state
from awtube.errors import AwtubeError, AWTubeErrorException

import awtube.task_wrappers as task_wrappers
from awtube.task_wrappers import TaskWrapperResult

# TODO: maybe need lock for clear() appendleft() non-threadsafe operations in command queues


class Controller(ABC):
    """
    The Controller is responsible for executing commands correctly.
        Trigger: A mechanism used to define how and when a command is executed
    """
    _logger: logging.Logger = None
    _command_queue: queue.Queue = queue.Queue()
    _observer: observers.Observer = None
    _reciever: command_receiver.CommandReceiver = None
    _paused_execution: bool = False
    _main_task: asyncio.Task = None

    @abstractmethod
    def _get_task(self, command) -> None | task_wrappers.TaskWrapper:
        """ 
            Here is to be defined how the controller handles commands, by matching each
            command with a certain TaskWrapper.
        """

    async def start(self) -> None:
        """ Start the main loop. """
        self._main_task = asyncio.create_task(self._run())
        await self._main_task

    def pause(self) -> None:
        """ Pause the main loop. """
        self._paused_execution = True

    def stop(self) -> None:
        """ Stop the main loop of controller. """
        try:
            if self._main_task:
                self._main_task.cancel()
            self._paused_execution = True
        except:
            self._logger.error(
                'Could not stop main loop of %s', self.__class__.__name__)
            raise

    def schedule_last(self, command) -> task_wrappers.TaskWrapper:
        """ Schedule command after others already in queue. """
        task = self._get_task(command=command)
        item = (command, task)
        self._logger.debug(
            'Scheduled %s for %s', type(task).__name__, type(command).__name__)
        self._command_queue.put(item)
        return task

    def schedule_first(self, command) -> task_wrappers.TaskWrapper:
        """ Schedule command before others already in queue. """
        task = self._get_task(command=command)
        item = (command, task)
        self._logger.debug(
            'Scheduled %s for %s', type(task).__name__, type(command).__name__)
        self._command_queue.queue.appendleft(item)
        return task

    async def _run(self) -> None:
        while True:
            # TODO: how many times should it try
            if not self._logger:
                self._logger.error('No logger defined for controller!')
                await asyncio.sleep(1)
                continue

            if self._observer.payload is None:
                self._logger.error('%s is not updated!',
                                   type(self._observer).__name__)
                await asyncio.sleep(1)
                continue

            if self._command_queue.empty():
                await asyncio.sleep(0.5)
            else:
                _, task = self._command_queue.get(block=False)

                await task.start()


class MachineController(Controller):
    def __init__(self, status_observer: StatusObserver) -> None:
        """
        Initialize commands.
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        # observers
        self._observer = status_observer

        # heartbeat
        self.heartbeat_cmd = None
        self.sending_heartbeat = False
        self.last_heartbeat_time = None

        # cia402
        self._current_cia402_cmd = None
        self._current_cw = 128

        # TODO get from command
        self._heartbeat_freq = 1
        self.heartbeat_cmd = None

    def _get_task(self, command) -> None | task_wrappers.TaskWrapper:
        if isinstance(command, commands.HeartbeatCommad):
            return task_wrappers.PeriodicTask(
                coro=self._heartbeat_callback, args=(command), sleep_time=1/self._heartbeat_freq)

        elif isinstance(command, commands.KinematicsConfigurationCommad):
            return task_wrappers.OneTimeTask(
                coro=self._kc_callback, args=(command))

        elif isinstance(command, commands.MachineStateCommad):
            return task_wrappers.PeriodicUntilDoneTask(
                coro=self._machine_state_callback, args=(command), sleep_time=1)

        else:
            self._logger.error(
                'This controller cannot handle commands of type: %s', type(command))

    # define task coroutines
    async def _heartbeat_callback(self, cmd: None | commands.HeartbeatCommad) -> None | TaskWrapperResult:
        if not self.heartbeat_cmd:
            self.heartbeat_cmd = cmd
        if not self._observer.payload:
            self._logger.debug('Observer not yet updated!')
            return TaskWrapperResult.RUNNING

        if not self.last_heartbeat_time:
            self.last_heartbeat_time = time.time()

        self.heartbeat_cmd._heartbeat = self._observer.payload.machine.heartbeat
        self.heartbeat_cmd.execute()
        self.sending_heartbeat = True

        delay = time.time()-self.last_heartbeat_time
        self._logger.debug(
            'Heartbeat: %s in %s secs', self.heartbeat_cmd._heartbeat, round(delay, 3))
        self.last_heartbeat_time = time.time()

        return TaskWrapperResult.RUNNING

    async def _kc_callback(self, cmd: None | commands.KinematicsConfigurationCommad) -> None | TaskWrapperResult:
        self._logger.debug('Set limits_disabled to %s', cmd.disable_limits)
        cmd.execute()

    async def _machine_state_callback(self, cmd: commands.MachineStateCommad) -> None | TaskWrapperResult:
        if not self._current_cia402_cmd:
            self._current_cia402_cmd = cmd

        cia402_state = device_state(
            self._observer.payload.machine.status_word)

        if cia402_state == self._current_cia402_cmd.desired_state:
            self._logger.debug('CIA402: %s.', cia402_state.value)
            return TaskWrapperResult.SUCCESS

        next_cw = transition(
            cia402_state,
            self._current_cw,
            fault_reset=True)
        self._current_cia402_cmd.control_word = next_cw
        self._current_cw = next_cw
        self._current_cia402_cmd.execute()
        return TaskWrapperResult.RUNNING


class StreamController(Controller):
    def __init__(self, stream_observer: StreamObserver, min_stream_capacity: int = 15) -> None:
        """
        Initialize commands.
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        # stream
        self._min_stream_capacity = min_stream_capacity
        self._observer: StreamObserver = stream_observer
        self._command_queue: queue.Queue[Command] = queue.Queue()

        # single cmd
        self._single_cmd_running = False

    def _get_task(self, command) -> None | task_wrappers.TaskWrapper:
        if isinstance(command,
                      (commands.MoveLineCommand,
                       commands.MoveJointsCommand,
                       commands.MoveToPositionCommand,
                       commands.StreamCommand)):
            return task_wrappers.PeriodicUntilDoneTask(
                coro=self._single_cmd_callback, args=(command), sleep_time=0.5)
        else:
            self._logger.error(
                'This controller cannot handle commands of type: %s', type(command))

    def _current_tag(self) -> None | int:
        """ 
            Returns latest stream tag from stream observer.
            If stream server not updated returns None. 
        """
        if self._observer.payload:
            return self._observer.payload.tag

    async def _single_cmd_callback(self, cmd: None | commands.Command) -> None | TaskWrapperResult:

        if not self._single_cmd_running:
            self._logger.debug('Sending single cmd %s', type(cmd).__name__)

            cmd.tag = self._current_tag() + 1
            if self._observer.payload.capacity >= self._min_stream_capacity:

                if isinstance(cmd, commands.StreamCommand):
                    if cmd.command_type is types.StreamCommandType.STOP:
                        self._command_queue.queue.clear()
                        cmd.execute()
                        return TaskWrapperResult.SUCCESS
                    if cmd.command_type is types.StreamCommandType.PAUSE:
                        cmd.execute()
                        return TaskWrapperResult.SUCCESS
                else:
                    cmd.execute()
                    self._single_cmd_running = True
                    return TaskWrapperResult.RUNNING
            else:
                return TaskWrapperResult.RUNNING

        else:
            # check if execution has finished
            if self._observer.payload.tag == cmd.tag and self._observer.payload.state == StreamState.IDLE:
                self._single_cmd_running = False
                return TaskWrapperResult.SUCCESS
            else:
                return TaskWrapperResult.RUNNING
