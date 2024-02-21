#!/usr/bin/env python3

""" MachineState command that implements Command Interface  """

from awtube.commands.command import Command
from awtube.recievers.command_receiver import CommandReceiver
from awtube.builders.command_builder import CommandBuilder
from awtube.cia402.cia402_machine import CIA402MachineState


class MachineStateCommad(Command):
    """
        machine command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 desired_state: CIA402MachineState,
                 machine: int = 0) -> None:
        self._desired_state = desired_state
        self._control_word = 0
        self._machine = machine
        self._receiver = receiver
        self.builder = CommandBuilder()

    @property
    def desired_state(self) -> CIA402MachineState:
        return self._desired_state

    @property
    def control_word(self) -> CIA402MachineState:
        return self._control_word

    @control_word.setter
    def control_word(self, cw: int) -> None:
        self._control_word = cw

    @property
    def receiver(self) -> CIA402MachineState:
        return self._receiver

    @receiver.setter
    def receiver(self, cw: int) -> None:
        self._receiver = cw

    @property
    def machine(self) -> CIA402MachineState:
        return self.machine

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().machine(self._machine).control_word(
            self._control_word).build()
        self._receiver.put(msg)
