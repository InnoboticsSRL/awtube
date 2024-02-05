from awtube.api.robot_function import RobotFunction
from awtube.commanders.machine_commander import MachineCommander
from awtube.command_reciever import CommandReciever
from awtube.commands.machine_state_command import MachineStateCommad
from awtube.cia402_machine import CIA402MachineState


class EnableFunction(RobotFunction):
    """ Enable connection with GBC. """

    def __init__(self, machine_commander: MachineCommander, reciever: CommandReciever) -> None:
        self._machine_commander = machine_commander
        self._reciever = reciever

    # not yet ready, because currently is reset is reduntant
    # def reset(self) -> None:
    #     """ Reset connection with GBC, commanding to go to SWITCHED_ON state. """
    #     cmd = MachineStateCommad(self._receiver,
    #                              desired_state=CIA402MachineState.SWITCHED_ON)
    #     self._machine_commander.add_command(cmd)

    def enable(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state. """
        cmd = MachineStateCommad(self._reciever,
                                 desired_state=CIA402MachineState.OPERATION_ENABLED)
        self._machine_commander.add_command(cmd)
