#!/usr/bin/env python3

""" MoveJointsInterpolated command that implements Command Interface  """

import typing as tp
from awtube.commands.command import Command
from awtube.command_reciever import CommandReciever
from awtube.msg_builders import stream_move_joints_interpolated_cmd
from awtube.types.aw import JointStates


class MoveJointsInterpolatedCommand(Command):
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
