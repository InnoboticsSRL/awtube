#!/usr/bin/env python3

""" MoveJointsInterpolated command that implements Command Interface  """

import typing as tp

from awtube.commands.command import Command
from awtube.recievers.command_receiver import CommandReceiver
# from awtube.msg_builders import stream_move_joints_interpolated_cmd
from awtube.types.aw import JointStates
from awtube.messages.stream_builder import StreamBuilder


class MoveJointsInterpolatedCommand(Command):
    """
        moveJointsInterpolated command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 joint_positions: tp.List[float],
                 joint_velocities: tp.List[float],
                 tag: int = 0,
                 kc: int = 0) -> None:
        self.joints = JointStates(positions=joint_positions,
                                  velocities=joint_velocities)
        self._receiver = receiver
        self.tag = tag
        self.kc = kc
        self.builder = StreamBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().move_joints_interpolated(joint_position_array=self.joints.positions,
                                                            joint_velocity_array=self.joints.velocities,
                                                            tag=self.tag,
                                                            kc=self.kc,
                                                            move_params={}
                                                            ).build()
        self._receiver.put(msg)
