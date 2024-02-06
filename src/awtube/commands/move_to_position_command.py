#!/usr/bin/env python3

""" MoveToPosition command that implements Command Interface  """

from awtube.commands.command import Command
from awtube.command_reciever import CommandReciever
from awtube.msg_builders import get_stream_move_to_position
from awtube.aw_types import Pose


class MoveToPositionCommand(Command):
    """
        moveToPosition command.
    """

    def __init__(self,
                 receiver: CommandReciever,
                 pose: Pose,
                 tag: int = 0) -> None:
        self._receiver = receiver
        self._payload = get_stream_move_to_position(pose=pose, tag=tag)

    def execute(self) -> None:
        """ Put command payload in reciever queue. """
        self._receiver.put(self._payload)
