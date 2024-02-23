#!/usr/bin/env python3

""" Commanders for commander pattern. """

from __future__ import annotations
from abc import ABC, abstractmethod
import time
import copy
import asyncio
import queue
import logging
from typing import AsyncGenerator
from queue import Queue

import awtube.logging_config

from awtube.commands import Command, MachineStateCommad, HeartbeatCommad, \
    KinematicsConfigurationCommad, MachineTargetCommad

from awtube.observers import StreamObserver, StatusObserver
from awtube.types import StreamState
from awtube.types import FunctionResult


from awtube.command_receiver import CommandReceiver
from awtube.types import MachineTarget

from awtube.cia402 import transition, device_state
# errors
from awtube.errors import AwtubeError, AWTubeErrorException


class Commander(ABC):
    """
    The Commander is associated with one or several commands. It sends a request
    to the command reciever.
    """

    @abstractmethod
    def add_command(self, command: Command) -> None:
        """ Add commands to be sent """
        raise NotImplementedError

    @abstractmethod
    async def execute_commands(self) -> None:
        """ Execute all commands """
        raise NotImplementedError


class StreamCommander(Commander):
    """
    The StreamCommander is associated with one or several commands. It manages
    the logic of executing commands based on the stream capacity.
    """

    def __init__(self, stream_observer: StreamObserver, capacity_min: int = 15) -> None:
        """
        Initialize commands.
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        self._stream_observer: StreamObserver = stream_observer
        self._command_queue: queue.Queue[Command] = queue.Queue()
        self._capacity_min: int = capacity_min
        self.__tag = None

        # stream observer None count
        self._stream_observer_tentatives = 0
        self._stream_observer_max_tentatives = 10

    def add_command(self, command: Command) -> None:
        """ Add commands to be sent """
        self._command_queue.put(command)

    async def wait_for_cmd_execution(self, command: Command) -> FunctionResult:
        command.execute()

        while True:
            # if self._stream_observer.payload.tag > command.tag:
            #     # means we finished task too fast to recieve feedback
            #     return FunctionResult.SUCCESS

            if self._stream_observer.payload.tag == command.tag and self._stream_observer.payload.state == StreamState.IDLE:
                # if no feedback for jobs with smaller tag finish them too
                # if
                # print(
                #     f'done movement!!!!!!!: {self._stream_observer.payload.tag}')
                # returning we finish the task
                return FunctionResult.SUCCESS
            await asyncio.sleep(0.2)

    async def execute_commands(self) -> AsyncGenerator[asyncio.Task]:
        """ Asyncio Generator which takes messages from object's queue and executes them, 
            respecting the capacity of the stream, which in the meantime yields asyncio.Task 
            objects that represent the stream activities requested to GBC. 
        """

        self._logger.debug('Started execution of stream commands.')

        while True:
            if self._command_queue.empty():
                break

            if self._stream_observer_tentatives >= self._stream_observer_max_tentatives:
                raise Exception("Couldn't update StreamObserver.")

            if not self._stream_observer.payload:
                self._stream_observer_tentatives += 1
                await asyncio.sleep(0.1)
                print('StreamObserver is None')
                continue
            else:
                # get last tag from motion controller
                if not self.__tag:
                    self.__tag = self._stream_observer.payload.tag
                self._stream_observer_tentatives = 0

            if self._stream_observer.payload.capacity >= self._capacity_min:
                cmd: Command = self._command_queue.get(block=False)

                cmd.tag = copy.copy(self.__tag)
                task: asyncio.Task = asyncio.create_task(
                    self.wait_for_cmd_execution(cmd))
                self.__tag += 1
                yield task
                await asyncio.sleep(0.02)
            else:
                await asyncio.sleep(0.1)


class MachineCommander(Commander):
    """
    The MachineCommander is associated with one or several commands. 
    It sends a command to the receiver.
    """

    def __init__(self, status_observer: StatusObserver,  heartbeat_freq: int = 1) -> None:
        """
            Initialize MachineCommander: Sends commands related to the functioning of the machine.
            send_commands() is a loop which continuosly checks the queue for new commands and sends
            them. Also maintains the heartbeat and checks the operation state of the machine, velocity
            , physical limits and target(simulation or real) machine.

        Args:
            status_observer (StatusObserver):
            heartbeat_freq (int, optional): The freq in Hz used to maintain the heartbeat. 
            Defaults to 1.
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        self._status_observer: StatusObserver = status_observer
        self._command_queue: Queue[Command] = Queue()
        self._heartbeat_freq: int = heartbeat_freq
        self._last_cmd_timestamp = time.time()
        self._receiver = None

        # attributes concerning the state machine
        self._current_cmd = None
        self._executing_cia402_command = False
        self._current_cw = 128

        # robot settables
        self._limits_disabled = False
        self._target_feed_rate = 1
        self._target = MachineTarget.SIMULATION

        # target set procedure vars
        self._target_done = False
        self._target_set_max_attempts = 5
        self._target_set_attempts = 0

    # receiver property
    @property
    def receiver(self) -> CommandReceiver:
        return self._receiver

    @receiver.setter
    def receiver(self, value) -> None:
        self._receiver = value

    # limits_disabled property
    @property
    def limits_disabled(self) -> bool:
        """ Get limits disabled flag. """
        return self._limits_disabled

    @limits_disabled.setter
    def limits_disabled(self, value: bool) -> None:
        """ Set limits disabled flag. """
        if not isinstance(value, bool):
            raise AWTubeErrorException(
                AwtubeError.BAD_ARGUMENT, 'Limits disabled flag should be a bool type.')
        self._limits_disabled = value

    # velocity property
    @property
    def velocity(self) -> bool:
        """ Get physical limits flag. """
        return self._target_feed_rate

    @velocity.setter
    def velocity(self, value: (float, int)) -> None:
        """ Set physical limits flag. Takes values from 0.0 to 2.2"""
        if not isinstance(value, (float, int)):
            raise AWTubeErrorException(
                AwtubeError.BAD_ARGUMENT, 'Velocity limits should be a float or int type.')
        self._target_feed_rate = value

    @property
    def target(self) -> MachineTarget:
        """ Get physical limits flag. """
        return self._target

    # target property
    @target.setter
    def target(self, value: (float, int, MachineTarget)) -> None:
        """ Set physical limits flag. Takes values from 0.0 to 2.2"""
        if not isinstance(value, (float, int, MachineTarget)):
            raise AWTubeErrorException(
                AwtubeError.BAD_ARGUMENT, 'Velocity limits should be a float, int or MachineTarget type.')
        self._target = MachineTarget(value)
        self._target_done = False
        self._target_set_attempts = 0

    def add_command(self, command: Command) -> None:
        """ Add commands to be sent and update the receiver 
            to which we'll send the heartbeat command"""
        self._command_queue.put(command)

    async def __resend_heartbeat(self) -> None:
        """ Resend last hearbeat back """
        if (time.time() - self._last_cmd_timestamp) > (1/self._heartbeat_freq):
            cmd: HeartbeatCommad = HeartbeatCommad(
                receiver=self._receiver,
                heartbeat=self._status_observer.payload.machine.heartbeat)
            cmd.execute()
            self._last_cmd_timestamp = time.time()
            self._logger.debug('Sent heartbeat.')
            await asyncio.sleep(0.2)

    async def __get_command(self) -> None:
        """ Get next command from queue if not already executing one. """
        if not self._command_queue.empty() and not self._executing_cia402_command:
            # get new command to process
            self._current_cmd: MachineStateCommad = self._command_queue.get(
                block=False)
            self._executing_cia402_command = True
            self._logger.debug('Got new command from queue.')
            return

    async def __execute_next_cia402_transition(self) -> None:
        """ Execute next step to take the state machine at the desired state. """
        if self._executing_cia402_command:
            await asyncio.sleep(0.1)
            # reset flags and return to accept new command from queue
            cia402_state = device_state(
                self._status_observer.payload.machine.status_word)
            if cia402_state == self._current_cmd.desired_state:
                self._logger.debug('New CIA402 state: %s.', cia402_state.value)
                self._executing_cia402_command = False
                return

            # every iteration send command
            next_cw = transition(
                cia402_state,
                self._current_cw,
                fault_reset=True)
            self._current_cmd.control_word = next_cw
            self._current_cw = next_cw
            self._current_cmd.execute()
            return

    async def __ensure_target_velocity_and_limits(self) -> None:
        """ Ensure velocity and limits have the sames value as those set here. """

        if self._status_observer.payload.kc[0].limits_disabled != self._limits_disabled:
            self._logger.debug('Resetting limits_disabled.')
            cmd = KinematicsConfigurationCommad(self._receiver)
            cmd.disable_limits = self._limits_disabled
            cmd.execute()

        if self._status_observer.payload.kc[0].fro_target != self._target_feed_rate:
            self._logger.debug('Resetting target velocity.')
            cmd = KinematicsConfigurationCommad(self._receiver)
            cmd.target_feed_rate = self._target_feed_rate
            cmd.execute()
        # check again after approximately 1 sec
        await asyncio.sleep(1.0)

    async def __ensure_target(self) -> None:
        """ 
            Ensure target has the same value as set here.
            It loops here until the target is reached.
        """
        if self._status_observer.payload.machine.target != self._target and self._target_set_attempts < self._target_set_max_attempts:
            self._logger.debug('Resetting target.')
            cmd = MachineTargetCommad(self.receiver, target=self._target)
            cmd.execute()
            self._target_done = False
            self._target_set_attempts += 1
            # check again after approximately 1 sec
            await asyncio.sleep(1.0)
        else:
            self._target_done = True

    async def execute_commands(self) -> None:
        self._logger.debug('Started executing commands.')
        while True:
            await self.__internal_loop()

    async def __internal_loop(self) -> None:
        # the steps here are quasi cumulative

        # step 1
        # if observer not updated keep exiting
        if not self._status_observer.payload:
            await asyncio.sleep(0.1)
            return

        # step 2
        # if reciever not set keep exiting
        if not self._receiver:
            self._logger.error('No receiver!')
            await asyncio.sleep(0.1)
            return

        # step 3
        # send heartbeat
        await self.__resend_heartbeat()

        # step 4
        # Keep looping until we change target.
        if not self._target_done:
            await self.__ensure_target()

        # step 5
        await self.__get_command()

        # step 6
        await self.__execute_next_cia402_transition()

        # step 7
        await self.__ensure_target_velocity_and_limits()

        await asyncio.sleep(0.01)
