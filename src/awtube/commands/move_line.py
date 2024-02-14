#!/usr/bin/env python3

""" MoveLine command that implements Command Interface  """

import typing as tp

from awtube.commands.command import Command
from awtube.recievers.command_receiver import CommandReceiver
from awtube.messages.stream_builder import StreamBuilder
from awtube.types.aw import Pose, Position, Quaternion


class MoveLineCommand(Command):
    """
        moveLine command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 translation: tp.Dict[str, float],
                 rotation: tp.Dict[str, float],
                 tag: int = 0,
                 kc: int = 0) -> None:
        self.pose = Pose(position=Position(**translation),
                         orientation=Quaternion(**rotation))
        self._receiver = receiver
        self.tag = tag
        self.kc = kc
        self.builder = StreamBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().move_line(pose=self.pose,
                                             tag=self.tag,
                                             kc=self.kc,
                                             move_params={}
                                             ).build()
        self._receiver.put(msg)
