import typing as tp
from awtube.commands.command import Command
from awtube.command_reciever import CommandReciever
from awtube.command_builders import stream_move_joints_interpolated_cmd
from awtube.aw_types import JointStates


class MoveJointsInterpolated(Command):
    """
        moveJointsInterpolated command.
    """
    def __init__(self,
                 receiver: CommandReciever,
                 joint_positions: tp.List[float],
                 joint_velocities: tp.List[float]) -> None:
        joints = JointStates(positions=joint_positions,
                             velocities=joint_velocities)
        self._receiver = receiver
        self._payload = stream_move_joints_interpolated_cmd(joints)

    def execute(self) -> None:
        """ Put command payload in reciever queue. """
        self._receiver.put(self._payload)
