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
    def _get_task(self, command) -> None | task_wrappers.TWrapper:
        """ 
            Here is to be defined how the controller handles commands, by matching each
            command with a certain TWrapper.
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

    def clear_queue(self) -> None:
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
        self._command_queue.queue.appendleft(item)
        return task

    async def _run(self) -> None:
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
    def __init__(self, status_observer: observers.StatusObserver) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._observer = status_observer
        self.heartbeat_cmd = None
        self.last_heartbeat_time = None
        self._current_cia402_cmd = None
        self._current_cw = 128

    def _get_task(self, command) -> None | task_wrappers.TWrapper:
        if isinstance(command, commands.HeartbeatCommad):
            return task_wrappers.PeriodicTask(
                coro_callback=self._heartbeat_callback,
                args=(command),
                sleep_time=1/command._frequency)

        elif isinstance(command, (
                commands.KinematicsConfigurationCommad,
                commands.IoutCommad)):
            return task_wrappers.OneTimeTask(
                coro_callback=self._kc_callback,
                args=(command))

        elif isinstance(command, commands.MachineStateCommad):
            return task_wrappers.PeriodicUntilDoneTask(
                coro_callback=self._machine_state_callback,
                args=(command),
                sleep_time=1)

        else:
            self._logger.error(
                'This controller cannot handle commands of type: %s', type(command))

    async def _heartbeat_callback(self, cmd: None | commands.HeartbeatCommad) -> None | task_wrappers.TWrapperResult:
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
            'Heartbeat: %s in %s secs', self.heartbeat_cmd._heartbeat, round(delay, 3))
        self.last_heartbeat_time = time.time()

        return task_wrappers.TWrapperResult.RUNNING

    async def _kc_callback(self, cmd: None | commands.KinematicsConfigurationCommad) -> None | task_wrappers.TWrapperResult:
        # self._logger.debug('Set limits_disabled to %s', cmd.disable_limits)
        cmd.execute()

    async def _machine_state_callback(self, cmd: commands.MachineStateCommad) -> None | task_wrappers.TWrapperResult:
        if not self._current_cia402_cmd:
            self._current_cia402_cmd = cmd

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
    def __init__(self, stream_observer: observers.StreamObserver, min_stream_capacity: int = 15) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

        # stream
        self._min_stream_capacity = min_stream_capacity
        self._observer = stream_observer
        self._command_queue: queue.Queue[commands.Command] = queue.Queue()
        self._current_tag = 0

        # single cmd
        self._single_cmd_running = False

    def _get_task(self, command) -> None | task_wrappers.TWrapper:
        if isinstance(command,
                      (
                          commands.MoveLineCommand,
                          commands.MoveJointsCommand,
                          commands.MoveToPositionCommand,
                          commands.StreamCommand
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
            return task_wrappers.PeriodicUntilDoneTask(
                coro_callback=self._multi_move_interpolated_cmd_callback,
                args=(command),
                # this task is high priority ! (this task can cause jitter)
                sleep_time=0.05)
        else:
            self._logger.error(
                'This controller cannot handle commands of type: %s', type(command))

    async def _stream_cmd_callback(self, cmd: None | commands.Command) -> None | task_wrappers.TWrapperResult:
        if cmd.command_type is types.StreamCommandType.STOP:
            self.clear_queue()
            cmd.execute()
        if cmd.command_type is types.StreamCommandType.PAUSE:
            cmd.execute()
        if cmd.command_type is types.StreamCommandType.RUN:
            cmd.execute()

    async def _single_move_cmd_callback(self, cmd: None | commands.Command) -> None | task_wrappers.TWrapperResult:
        if not self._single_cmd_running:
            cmd.tag = self._current_tag + 1
            self._logger.debug('Sending single cmd: %s with tag: %d', type(
                cmd).__name__, cmd.tag)

            if self._observer.payload.capacity >= self._min_stream_capacity:
                cmd.execute()
                self._current_tag = cmd.tag
                self._single_cmd_running = True
                return task_wrappers.TWrapperResult.RUNNING
            else:
                return task_wrappers.TWrapperResult.RUNNING

        else:
            # check if execution has finished
            if self._observer.payload.tag == cmd.tag and self._observer.payload.state == types.StreamState.IDLE:
                self._single_cmd_running = False
                return task_wrappers.TWrapperResult.SUCCESS
            else:
                return task_wrappers.TWrapperResult.RUNNING

    async def _multi_move_interpolated_cmd_callback(self, cmd_list: None | list[commands.Command]) -> None | task_wrappers.TWrapperResult:
        if self._observer.payload.capacity >= self._min_stream_capacity:
            self._logger.info('Capacity: %d', self._observer.payload.capacity)
            try:
                cmd = cmd_list.pop(0)
            except IndexError:
                # check if execution has finished
                return task_wrappers.TWrapperResult.SUCCESS
                # if self._observer.payload.tag == cmd.tag and self._observer.payload.state == StreamState.IDLE:
                #     return task_wrappers.TWrapperResult.SUCCESS
                # else:
                #     return task_wrappers.TWrapperResult.RUNNING

            cmd.tag = self._current_tag + 1
            self._logger.debug('Sending single moveJointsInterpolated cmd: %s with tag: %d', type(
                cmd).__name__, cmd.tag)
            cmd.execute()
            self._current_tag = cmd.tag

        return task_wrappers.TWrapperResult.RUNNING
