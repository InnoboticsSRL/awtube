#!/usr/bin/env python3

""" MachineTarget command that implements Command Interface  """

from awtube.types.gbc import MachineTarget
from awtube.builders.command_builder import CommandBuilder
from awtube.commands.command import Command
from awtube.recievers.command_receiver import CommandReceiver


class MachineTargetCommad(Command):
    """
        Machine target command, basically it is used to use either the real physical machine or the simulation.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 target: MachineTarget,
                 machine: int = 0) -> None:
        self._receiver = receiver
        self._machine = machine
        self._target = target
        self.builder = CommandBuilder()

    @property
    def target(self) -> MachineTarget:
        """ Return target as MachineTarget. """
        return self._target

    @target.setter
    def target(self, cw: int) -> None:
        self._target = cw

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().machine(
            self._machine).machine_target(self._target).build()
        self._receiver.put(msg)
