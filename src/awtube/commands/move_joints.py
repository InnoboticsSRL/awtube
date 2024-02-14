#!/usr/bin/env python3

""" MoveJoints command that implements Command Interface  """

import typing as tp

from awtube.commands.command import Command
from awtube.recievers.command_receiver import CommandReceiver
from awtube.messages.stream_builder import StreamBuilder


class MoveJointsCommand(Command):
    """
        moveJoints command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 joint_positions: tp.List[float],
                 tag: int = 0,
                 kc: int = 0) -> None:
        self.joints = joint_positions
        self._receiver = receiver
        self.tag = tag
        self.kc = kc
        self.builder = StreamBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().move_joints(joint_position_array=self.joints,
                                               tag=self.tag,
                                               kc=self.kc,
                                               move_params={}
                                               ).build()
        self._receiver.put(msg)
