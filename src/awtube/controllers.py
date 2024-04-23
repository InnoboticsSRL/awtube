#!/usr/bin/env python3

""" Commanders for commander pattern. """

from __future__ import annotations
from abc import ABC, abstractmethod
import time
import asyncio
import queue
import logging

from . import command_receiver, observers, cia402, task_wrappers, types, commands, observers

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
    def _get_task(self, command) -> task_wrappers.TWrapper:
        """ 
            Here is to be defined how the controller handles commands, by matching each
            command with a certain TWrapper.
        """

    async def start(self):
        """ Start the main loop. """
        self._main_task = asyncio.create_task(self._run())
        await self._main_task

    def pause(self):
        """ Pause the main loop. """
        self._paused_execution = True

    def stop(self):
        """ Stop the main loop of controller. """
        try:
            if self._main_task:
                self._main_task.cancel()
            self._paused_execution = True
        except:
            self._logger.error(
                'Could not stop main loop of %s', self.__class__.__name__)
            raise

    def clear_queue(self):
        """ Clear current queue. """
        self._command_queue.queue.clear()

    def schedule_last(self, command) -> task_wrappers.TWrapper:
        """ Schedule command after others already in queue. """
        task = self._get_task(command=command)
        item = (command, task)
        self._logger.debug(
            'Scheduled %s for %s', type(task).__name__, type(command).__name__)
        self._command_queue.put(item)
        return task

    def schedule_first(self, command) -> task_wrappers.TWrapper:
        """ Schedule command before others already in queue. """
        task = self._get_task(command=command)
        item = (command, task)
        self._logger.debug(
            'Scheduled %s for %s', type(task).__name__, type(command).__name__)
        # TODO: Not safe, implement a lock
        self._command_queue.queue.appendleft(item)
        return task

    async def _run(self):
        while True:

            if not self._logger:
                self._logger.error('No logger defined for controller!')
                await asyncio.sleep(1)
                continue

            # TODO: how many times should it try
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
    def __init__(self, status_observer: observers.StatusObserver):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._observer = status_observer
        self.heartbeat_cmd = None
        self.last_heartbeat_time = None
        self._current_cia402_cmd = None
        self._current_cw = 128

    def _get_task(self, command) -> task_wrappers.TWrapper:
        if isinstance(command, commands.HeartbeatCommad):
            return task_wrappers.PeriodicTask(
                coro_callback=self._heartbeat_callback,
                args=(command),
                sleep_time=1/command._frequency)

        elif isinstance(command, (
                commands.KinematicsConfigurationCommad,
                commands.IoutCommad,
                commands.DoutCommad,
                commands.SerialCommad)):
            return task_wrappers.OneTimeTask(
                coro_callback=self._one_time_callback,
                args=(command))

        elif isinstance(command, commands.MachineTargetCommad):
            return task_wrappers.PeriodicUntilDoneTask(
                coro_callback=self._set_check_callback,
                args=(command),
                sleep_time=0.5
            )

        elif isinstance(command, commands.MachineStateCommad):
            return task_wrappers.PeriodicUntilDoneTask(
                coro_callback=self._machine_state_callback,
                args=(command),
                sleep_time=1)

        else:
            self._logger.error(
                'This controller cannot handle commands of type: %s', type(command))

    async def _heartbeat_callback(self, cmd):
        if not self.heartbeat_cmd:
            self.heartbeat_cmd = cmd
        if not self._observer.payload:
            self._logger.debug('Observer not yet updated!')
            return task_wrappers.TWrapperResult.RUNNING

        if not self.last_heartbeat_time:
            self.last_heartbeat_time = time.time()

        self.heartbeat_cmd._heartbeat = self._observer.payload.machine.heartbeat
        self.heartbeat_cmd.execute()
        delay = time.time()-self.last_heartbeat_time
        self._logger.debug(
            'Heartbeat: %s in %.1f secs', self.heartbeat_cmd._heartbeat, delay)
        self.last_heartbeat_time = time.time()

        return task_wrappers.TWrapperResult.RUNNING

    async def _set_check_callback(self, cmd):
        if self._observer.payload.machine.target == cmd.target:
            self._logger.error('Finished %s', type(cmd).__name__)
            return task_wrappers.TWrapperResult.SUCCESS 
        
        
        cmd.execute()

    async def _one_time_callback(self, cmd):
        self._logger.debug('Executing %s', type(cmd).__name__)
        cmd.execute()

    async def _machine_state_callback(self, cmd):

        if not self._current_cia402_cmd:
            self._current_cia402_cmd = cmd

        # TODO: fix to disable automatically, the transition() logic doesn't go backwards
        if cmd.desired_state == cia402.CIA402MachineState.SWITCH_ON_DISABLED:
            self._current_cia402_cmd.control_word = 0
            self._current_cia402_cmd.execute()
            return task_wrappers.TWrapperResult.SUCCESS

        cia402_state = cia402.device_state(
            self._observer.payload.machine.status_word)

        if cia402_state == self._current_cia402_cmd.desired_state:
            self._logger.debug('CIA402: %s.', cia402_state.value)
            return task_wrappers.TWrapperResult.SUCCESS

        next_cw = cia402.transition(
            cia402_state,
            self._current_cw,
            fault_reset=True)
        self._current_cia402_cmd.control_word = next_cw
        self._current_cw = next_cw
        self._current_cia402_cmd.execute()
        return task_wrappers.TWrapperResult.RUNNING


class StreamController(Controller):
    def __init__(self, stream_observer: observers.StreamObserver):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._buffer_cushion = 35
        self._observer = stream_observer
        self._command_queue: queue.Queue[commands.Command] = queue.Queue()
        self._current_tag = 0
        self._single_cmd_running = False

    def _get_task(self, command) -> task_wrappers.TWrapper:
        if isinstance(command,
                      (
                          commands.MoveLineCommand,
                          commands.MoveJointsCommand,
                          commands.MoveToPositionCommand
                      )):
            return task_wrappers.PeriodicUntilDoneTask(
                coro_callback=self._single_move_cmd_callback,
                args=(command),
                sleep_time=0.5)
        elif isinstance(command,
                        (commands.StreamCommand)):
            return task_wrappers.OneTimeTask(
                coro_callback=self._stream_cmd_callback,
                args=(command))
        elif isinstance(command,
                        list):
            return task_wrappers.OneTimeTask(
                coro_callback=self._multi_move_interpolated_cmd_callback,
                args=(command)
            )
        else:
            self._logger.error(
                'This controller cannot handle commands of type: %s', type(command))

    async def _stream_cmd_callback(self, cmd: None | commands.Command) -> task_wrappers.TWrapperResult:
        if cmd.command_type is types.StreamCommandType.STOP:
            self.clear_queue()
            cmd.execute()
        if cmd.command_type is types.StreamCommandType.PAUSE:
            cmd.execute()
        if cmd.command_type is types.StreamCommandType.RUN:
            cmd.execute()

    def _execute_cmd(self, cmd):
        cmd.tag = self._current_tag + 1
        cmd.execute()
        self._current_tag = cmd.tag

    async def _single_move_cmd_callback(self, cmd: commands.Command) -> task_wrappers.TWrapperResult:
        if not self._single_cmd_running:
            self._logger.debug('Sending single cmd: %s with tag: %d', type(
                cmd).__name__, cmd.tag)

            if self._observer.payload.capacity >= self._buffer_cushion:
                self._execute_cmd(cmd)
                self._single_cmd_running = True
                return task_wrappers.TWrapperResult.RUNNING
            else:
                return task_wrappers.TWrapperResult.RUNNING

        else:
            if self._observer.payload.tag == cmd.tag and self._observer.payload.state == types.StreamState.IDLE:
                self._single_cmd_running = False
                return task_wrappers.TWrapperResult.SUCCESS
            else:
                return task_wrappers.TWrapperResult.RUNNING

    async def _multi_move_interpolated_cmd_callback(self, cmd_list: list[commands.Command]) -> task_wrappers.TWrapperResult:

        sent_all = False
        for e in cmd_list:
            self._command_queue.put(e)

        # TODO: Maybe write it using PeriodicUntilDone task wrapperto remove sleep and while loop
        while True:
            if not sent_all and self._observer.payload.capacity >= self._buffer_cushion:
                how_many = self._observer.payload.capacity - self._buffer_cushion
                for _ in range(how_many):
                    try:
                        cmd = self._command_queue.get(block=False)
                        self._execute_cmd(cmd)
                    except queue.Empty:
                        sent_all = True
                        break
            else:
                if self._observer.payload.tag == cmd_list[-1].tag and self._observer.payload.state == types.StreamState.IDLE:
                    return task_wrappers.TWrapperResult.SUCCESS
                if self._observer.payload.state == types.StreamState.STOPPED:
                    return task_wrappers.TWrapperResult.FAILURE

            await asyncio.sleep(0.2)
