""" Defines the MachineCommander class"""

from __future__ import annotations
import time
import asyncio
from queue import Queue
import logging

from awtube.commanders.commander import Commander

from awtube.commands.command import Command
from awtube.commands.machine_state_command import MachineStateCommad
from awtube.commands.heartbeat_command import HeartbeatCommad

from awtube.observers.machine import MachineObserver


from awtube.command_reciever import CommandReciever
from awtube.cia402_machine import (CIA402MachineState,
                                   transition,
                                   device_state)
from awtube.logging import config


class MachineCommander(Commander):
    """
    The MachineCommander is associated with one or several commands. 
    It sends a command to the reciever.
    """

    def __init__(self, machine_observer: MachineObserver,  heartbeat_freq: int = 1) -> None:
        """
            Initialize MachineCommander: Sends commands related to the functioning of the machine.
            send_commands() is a loop which continuosly checks the queue for new commands and
            also maintains the heartbeat.

        Args:
            machine_observer (MachineObserver):
            heartbeat_freq (int, optional): The freq in Hz used to maintain the heartbeat. 
            Defaults to 1.
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        self._machine_observer: MachineObserver = machine_observer
        self._command_queue: Queue[Command] = Queue()
        self._heartbeat_freq: int = heartbeat_freq
        self._last_cmd_timestamp = time.time()
        self._connected = False
        self._receiver = None

        # attributes concerning the state machine
        self._current_cmd = None
        self._executing_cia402_command = False
        self._current_cw = 128

    @property
    def reciever(self) -> CommandReciever:
        return self._receiver

    @reciever.setter
    def reciever(self, value) -> None:
        self._receiver = value

    def add_command(self, command: Command) -> None:
        """ Add commands to be sent and update the reciever 
            to which we'll send the heartbeat command"""
        self._command_queue.put(command)

    async def execute_commands(self, wait_done: bool = False) -> None:
        self._logger.debug('Started executing commands.')
        while True:
            await self.__internal_loop()

    async def __internal_loop(self) -> None:
        if not self._machine_observer.payload:
            # if observer not updated keep exiting here
            await asyncio.sleep(0.1)
            return

        if not self._receiver:
            print('No reciever!')
            return

        # resend last hearbeat back
        if (time.time() - self._last_cmd_timestamp) > (1/self._heartbeat_freq):
            cmd: HeartbeatCommad = HeartbeatCommad(
                receiver=self._receiver,
                heartbeat=self._machine_observer.payload.heartbeat)
            cmd.execute()
            self._last_cmd_timestamp = time.time()
            self._logger.debug('Sent heartbeat.')
            await asyncio.sleep(0.2)

        # dequeue only once TODO change
        if not self._command_queue.empty() and not self._executing_cia402_command:
            # get new command to process
            self._current_cmd: MachineStateCommad = self._command_queue.get(
                block=False)
            self._executing_cia402_command = True
            self._logger.debug('Got new command from queue.')
            return

        # if there is a command pending
        if self._executing_cia402_command:
            await asyncio.sleep(0.1)
            # reset flags and return to accept new command from queue
            cia402_state = device_state(
                self._machine_observer.payload.status_word)
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

        await asyncio.sleep(0.01)
