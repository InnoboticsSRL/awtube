#!/usr/bin/env python3

""" MachineState command that implements Command Interface  """

import typing as tp
from awtube.commands.command import Command
from awtube.command_reciever import CommandReciever
from awtube.msg_builders import *
from awtube.aw_types import *
from awtube.gbc_types import *
from enum import Enum
from awtube.cia402_machine import CIA402MachineState


class MachineStateCommad(Command):
    """
        machine command.
    """

    def __init__(self,
                 receiver: CommandReciever,
                 desired_state: CIA402MachineState,
                 machine: int = 0) -> None:
        self._desired_state = desired_state
        self._control_word = 0
        self._machine = machine
        self._receiver = receiver

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
        """ Put command payload in reciever queue. """
        self._receiver.put(get_machine_command(self._control_word,
                                               machine=self._machine))
