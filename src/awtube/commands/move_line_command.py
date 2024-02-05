import typing as tp
from awtube.commands.command import Command
from awtube.command_reciever import CommandReciever
from awtube.msg_builders import *
from awtube.aw_types import *
from awtube.gbc_types import *


class MoveLineCommand(Command):
    """
        moveLine command.
    """

    def __init__(self,
                 receiver: CommandReciever,
                 translation: tp.Dict[str, float],
                 rotation: tp.Dict[str, float],
                 tag: int = 0) -> None:
        pose = Pose(position=Position(**translation),
                    orientation=Quaternion(**rotation))
        self._receiver = receiver
        self._payload = stream_move_line_cmd(pose, tag=tag)

    def execute(self) -> None:
        """ Put command payload in reciever queue. """
        self._receiver.put(self._payload)
