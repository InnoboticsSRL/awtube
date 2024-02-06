#!/usr/bin/env python3

""" MoveLine command that implements Command Interface  """

import typing as tp
from awtube.commands.command import Command
from awtube.command_receiver import CommandReceiver
from awtube.msg_builders import *
from awtube.types.aw import *
from awtube.types.gbc import *


class MoveLineCommand(Command):
    """
        moveLine command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 translation: tp.Dict[str, float],
                 rotation: tp.Dict[str, float],
                 tag: int = 0) -> None:
        pose = Pose(position=Position(**translation),
                    orientation=Quaternion(**rotation))
        self._receiver = receiver
        self._payload = stream_move_line_cmd(pose, tag=tag)

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        self._receiver.put(self._payload)
