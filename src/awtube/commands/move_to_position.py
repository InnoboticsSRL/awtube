#!/usr/bin/env python3

""" MoveToPosition command that implements Command Interface  """

from awtube.commands.command import Command
from awtube.recievers.command_receiver import CommandReceiver
from awtube.types.aw import Pose
from awtube.messages.stream_builder import StreamBuilder
from awtube.types.gbc import PositionReference


class MoveToPositionCommand(Command):
    """
        moveToPosition command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 pose: Pose,
                 tag: int = 0,
                 kc: int = 0,
                 position_reference: PositionReference = PositionReference.ABSOLUTE) -> None:
        self._receiver = receiver
        self.tag = tag
        self.pose = pose
        self.kc = kc
        self.position_reference = position_reference
        self.builder = StreamBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().move_to_position(pose=self.pose,
                                                    tag=self.tag,
                                                    kc=self.kc,
                                                    move_params={},
                                                    position_reference=self.position_reference).build()
        self._receiver.put(msg)
