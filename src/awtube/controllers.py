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


class TaskResult(IntEnum):
    """ Result of a Task for one iteration """
    RUNNING = 0
    FAILURE = 1
    SUCCESS = 2


class ControllerTask(ABC):
    """ Task Wrappers used inside Controllers """
    pass


class PeriodicTask(ControllerTask):
    """ Task Wrapper for a coroutine that runs periodically"""

    def __init__(self, coro, args, sleep_time):
        self.coro = coro
        self.args = args
        self.sleep_time = sleep_time
        self.is_started = False
        self.task = asyncio.create_task(self._run())

    async def start(self):
        """ Start task to call coro """
        if not self.is_started:
            self.is_started = True
            # self.task = asyncio.create_task(self._run())

    async def stop(self):
        """ Stop task and await it stopped """
        if self.is_started:
            self.is_started = False
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task

    async def _run(self):
        #
        result = TaskResult.RUNNING
        while result is not TaskResult.FAILURE:
            if self.is_started:
                await asyncio.sleep(self.sleep_time)
                result = await self.coro(self.args)
            else:
                await asyncio.sleep(self.sleep_time)


class OneTimeTask(ControllerTask):
    """ Task Wrapper for a coroutine that runs only once"""

    def __init__(self, coro, args):
        self.coro = coro
        self.args = args
        self.is_started = False
        self.task = None

    async def _run(self):
        await self.coro(self.args)


class PeriodicUntilDoneTask(PeriodicTask):
    """ Task Wrapper for a coroutine that runs periodically until results in success or failure"""

    def __init__(self, coro, args, sleep_time):
        super().__init__(coro, args, sleep_time)

    async def _run(self):
        result = TaskResult.RUNNING
        while result is TaskResult.RUNNING:
            if self.is_started:
                await asyncio.sleep(self.sleep_time)
                result = await self.coro(self.args)
            else:
                await asyncio.sleep(self.sleep_time)


class Controller(ABC):
    """
    The Controller is responsible for executing commands correctly.
        Trigger: A mechanism used to define how and when a command is executed
    """
    _logger = None
    _command_queue = queue.Queue()
    _observer = None
    _reciever = None
    tasks = set()

    @abstractmethod
    def _get_task(self, command) -> None | ControllerTask:
        """ Determine what type of task the controller uses for each command type. """

    def schedule_last(self, command) -> ControllerTask:
        """ Schedule command after others already in queue. """
        task = self._get_task(command=command)
        item = (command, task)
        self._logger.debug(
            'Scheduled %s for %s', type(task).__name__, type(command).__name__)
        self._command_queue.put(item)
        return task

    def schedule_first(self, command) -> ControllerTask:
        """ Schedule command before others already in queue. """
        task = self._get_task(command=command)
        item = (command, task)
        self._logger.debug(
            'Scheduled %s for %s', type(task).__name__, type(command).__name__)
        self._command_queue.queue.appendleft(item)


class MachineController(Controller):
    def __init__(self, status_observer: StatusObserver, capacity_min: int = 15) -> None:
        """
        Initialize commands.
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._observer = status_observer
        self._capacity_min = capacity_min
        self.heartbeat_cmd = None
        self.sending_heartbeat = False
        self.last_heartbeat_time = None

        # attributes concerning the state machine
        self._current_cia402_cmd = None
        self._current_cw = 128

        # TODO get from command
        self._heartbeat_freq = 1
        self.heartbeat_cmd = None

    async def start(self) -> None:
        await self._run()

    def _get_task(self, command) -> None | ControllerTask:
        task = None

        if isinstance(command, commands.HeartbeatCommad):
            task = PeriodicTask(
                coro=self._heartbeat, args=(command), sleep_time=1)
        elif isinstance(command, commands.KinematicsConfigurationCommad):
            task = OneTimeTask(
                coro=self._kc, args=(command))
        elif isinstance(command, commands.MachineStateCommad):
            task = PeriodicUntilDoneTask(
                coro=self._machine_state, args=(command), sleep_time=1)
        else:
            self._logger.error(
                'This controller cannot handle commands of type: %s', type(command))

        return task

    async def _heartbeat(self, cmd: None | commands.HeartbeatCommad) -> None | TaskResult:
        if not self.heartbeat_cmd:
            self.heartbeat_cmd = cmd
        if not self._observer.payload:
            self._logger.debug('Observer not yet updated!')
            return TaskResult.RUNNING

        if not self.last_heartbeat_time:
            self.last_heartbeat_time = time.time()

        self.heartbeat_cmd._heartbeat = self._observer.payload.machine.heartbeat
        self.heartbeat_cmd.execute()
        self.sending_heartbeat = True
        self.last_heartbeat_time = time.time()
        self._logger.debug(
            'Heartbeat: %s in %s secs', self.heartbeat_cmd._heartbeat, (time.time()-self.last_heartbeat_time))

        return TaskResult.RUNNING

    async def _kc(self, cmd: None | commands.KinematicsConfigurationCommad) -> None | TaskResult:
        self._logger.debug('Set limits_disabled to %s', cmd.disable_limits)
        cmd.execute()

    async def _machine_state(self, cmd: None | commands.MachineStateCommad) -> None | TaskResult:
        if not self._current_cia402_cmd:
            self._current_cia402_cmd = cmd

        # if not self._observer.payload:
        #     return TaskResult.RUNNING

        cia402_state = device_state(
            self._observer.payload.machine.status_word)

        if cia402_state == self._current_cia402_cmd.desired_state:
            self._logger.debug('CIA402: %s.', cia402_state.value)
            return TaskResult.SUCCESS

        # every iteration send command
        next_cw = transition(
            cia402_state,
            self._current_cw,
            fault_reset=True)
        self._current_cia402_cmd.control_word = next_cw
        self._current_cw = next_cw
        self._current_cia402_cmd.execute()
        return TaskResult.RUNNING

    async def _run(self) -> None:

        while True:
            if not self._logger:
                self._logger.error('No logger defined for controller!')
                await asyncio.sleep(0.5)
                continue

            if self._observer.payload is None:
                self._logger.error('Status Observer is not updated!')
                await asyncio.sleep(0.5)
                continue

            if self._command_queue.empty():
                await asyncio.sleep(0.5)
            else:
                # TODO: Fix here: not clear orede of tuple elements
                cmd, task = self._command_queue.get(block=False)

                await task.start()

# class StreamController(Controller):
#     """
#     The StreamController is associated with one or several commands. It manages
#     the logic of executing commands based on the stream capacity.
#     """

#     def __init__(self, stream_observer: StreamObserver, capacity_min: int = 15) -> None:
#         """
#         Initialize commands.
#         """
#         self._logger = logging.getLogger(self.__class__.__name__)

#         self._stream_observer: StreamObserver = stream_observer
#         self._command_queue: queue.Queue[Command] = queue.Queue()
#         self._capacity_min: int = capacity_min
#         self.__tag = None

#         # stream observer None count
#         self._stream_observer_tentatives = 0
#         self._stream_observer_max_tentatives = 10

#     async def wait_for_cmd_execution(self, command: Command) -> FunctionResult:
#         command.execute()

#         while True:
#             if self._stream_observer.payload.tag == command.tag and self._stream_observer.payload.state == StreamState.IDLE:
#                 return FunctionResult.SUCCESS
#             await asyncio.sleep(0.2)

#     async def _move_joints_interpolated(self, cmd: None | commands.HeartbeatCommad) -> None | TaskResult:
#         if isinstance(cmd, commands.StreamCommand):
#             if cmd.command_type is types.StreamCommand.STOP:
#                 # remove remaining stream items
#                 self._command_queue.queue.clear()

#         cmd.tag = copy.copy(self.__tag)
#         task: asyncio.Task = asyncio.create_task(
#             self.wait_for_cmd_execution(cmd))
#         self.__tag += 1
#         yield task
#         await asyncio.sleep(0.02)

#     async def _move_line(self, cmd: None | commands.MoveLineCommand) -> None | TaskResult:
#         pass

#     async def _move_joints(self, cmd: None | commands.MoveJointsCommand) -> None | TaskResult:
#         pass

#     # async def execute_commands(self) -> AsyncGenerator[asyncio.Task]:
#     async def execute_commands(self) -> None:
#         """ Asyncio Generator which takes messages from object's queue and executes them,
#             respecting the capacity of the stream, which in the meantime yields asyncio.Task
#             objects that represent the stream activities requested to GBC.
#         """

#         self._logger.debug('Started execution of stream commands.')

#         if self._stream_observer_tentatives >= self._stream_observer_max_tentatives:
#             raise Exception("Couldn't update StreamObserver.")

#         if not self._stream_observer.payload:
#             self._stream_observer_tentatives += 1
#             await asyncio.sleep(0.1)
#             print('StreamObserver is None')

#         else:
#             # get last tag from motion controller
#             if not self.__tag:
#                 self.__tag = self._stream_observer.payload.tag
#             self._stream_observer_tentatives = 0


#         if self._stream_observer.payload.capacity >= self._capacity_min:
#             current_cmd: Command = self._command_queue.get(block=False)

#             if isinstance(current_cmd, commands.MoveJointsInterpolatedCommand):
#                 await PeriodicTask(
#                     coro=self._move_joints_interpolated, args=(current_cmd), sleep_time=1).start()
#                 self._logger.debug(
#                     'PeriodicTask for %s', type(current_cmd))

#             if isinstance(current_cmd, commands.MoveLineCommand):
#                 await OneTimeTask(
#                     coro=self._move_line, args=(current_cmd)).start()
#                 self._logger.debug(
#                     'OneTimeTask for %s', type(current_cmd))

#             if isinstance(current_cmd, commands.MoveJointsCommand):
#                 await OneTimeTask(
#                     coro=self._move_joints, args=(current_cmd)).start()
#                 self._logger.debug(
#                     'OneTimeTask for %s', type(current_cmd))
