#!/usr/bin/env python3

""" MachineTarget command that implements Command Interface  """

from awtube.types.gbc import MachineTarget
from awtube.msg_builders import get_machine_target_command

from awtube.commands.command import Command
from awtube.command_receiver import CommandReceiver


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

    @property
    def target(self) -> MachineTarget:
        """ Return target as MachineTarget. """
        return self._target

    @target.setter
    def target(self, cw: int) -> None:
        self._target = cw

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        self._receiver.put(get_machine_target_command(self._target,
                                                      machine=self._machine))
