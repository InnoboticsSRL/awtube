import typing as tp
from awtube.commands.command import Command
from awtube.command_reciever import CommandReciever
from awtube.msg_builders import *
from awtube.aw_types import *
from awtube.gbc_types import *


class MoveJointsCommand(Command):
    """
        moveJoints command.
    """

    def __init__(self,
                 receiver: CommandReciever,
                 joint_positions: tp.List[float],
                 tag: int = 0) -> None:
        self.joints = JointStates(positions=joint_positions)
        self._receiver = receiver
        self._payload = stream_move_joints_cmd(joints=self.joints, tag=tag)

    def execute(self) -> None:
        """ Put command payload in reciever queue. """
        self._receiver.put(self._payload)
