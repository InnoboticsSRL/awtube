#!/usr/bin/env python3

""" Defines the MoveToPositioinFunction. """

import typing as tp
from awtube.functions.robot_function import RobotFunction
from awtube.commands.move_to_position import MoveToPositionCommand
from awtube.types.aw import Position, Quaternion
from awtube.commanders.stream import StreamCommander
from awtube.command_reciever import CommandReciever
from awtube.types.aw import Pose


class MoveToPositioinFunction(RobotFunction):
    """ Send moveToPosition command. """

    def __init__(self, stream_commander: StreamCommander, reciever: CommandReciever) -> None:
        self._stream_commander = stream_commander
        self._reciever = reciever

    async def move_to_position(self,
                               translation: tp.Dict[str, float],
                               rotation: tp.Dict[str, float],
                               tag: int = 0) -> None:
        """ Send a moveLine command to a CommandReciever.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        pose = Pose(position=Position(**translation),
                    orientation=Quaternion(**rotation))
        cmd = MoveToPositionCommand(self._reciever, pose, tag)
        self._stream_commander.add_command(cmd)
        await self._stream_commander.execute_commands()
