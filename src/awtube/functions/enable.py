#!/usr/bin/env python3

""" Defines the EnableFunction. """

from awtube.functions.robot_function import RobotFunction
from awtube.commanders.machine import MachineCommander
from awtube.recievers.command_receiver import CommandReceiver
from awtube.commands.machine_state import MachineStateCommad
from awtube.cia402.cia402_machine import CIA402MachineState


class EnableFunction(RobotFunction):
    """ Enable connection with GBC. """

    def __init__(self, machine_commander: MachineCommander, receiver: CommandReceiver) -> None:
        self._machine_commander = machine_commander
        self._receiver = receiver

    # not yet ready, because currently reset
    # def reset(self) -> None:
    #     """ Reset faults with GBC, commanding to go to SWITCHED_ON state. """
    #     cmd = MachineStateCommad(self._receiver,
    #                              desired_state=CIA402MachineState.SWITCHED_ON)
    #     self._machine_commander.add_command(cmd)

    def enable(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state. """
        cmd = MachineStateCommad(self._receiver,
                                 desired_state=CIA402MachineState.OPERATION_ENABLED)
        self._machine_commander.add_command(cmd)
