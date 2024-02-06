#!/usr/bin/env python3

""" MoveJoints command that implements Command Interface  """

import typing as tp
from awtube.commands.command import Command
from awtube.command_receiver import CommandReceiver
from awtube.msg_builders import *
from awtube.types.aw import *
from awtube.types.gbc import *


class MoveJointsCommand(Command):
    """
        moveJoints command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 joint_positions: tp.List[float],
                 tag: int = 0) -> None:
        self.joints = JointStates(positions=joint_positions)
        self._receiver = receiver
        self._payload = stream_move_joints_cmd(joints=self.joints, tag=tag)

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        self._receiver.put(self._payload)
