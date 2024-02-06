#!/usr/bin/env python3

""" Defines the MoveLineFunction. """

from awtube.functions.robot_function import RobotFunction
from awtube.commands.move_joints_interpolated import MoveJointsInterpolatedCommand
from awtube.commanders.stream import StreamCommander
from awtube.command_receiver import CommandReceiver
import typing as tp
from awtube.commands import move_line


class MoveLineFunction(RobotFunction):
    def __init__(self, stream_commander: StreamCommander, receiver: CommandReceiver) -> None:
        self._stream_commander = stream_commander
        self._receiver = receiver

    async def move_line(self,
                        translation: tp.Dict[str, float],
                        rotation: tp.Dict[str, float],
                        tag: int = 0) -> None:
        """ Send a moveLine command to a CommandReceiver.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        cmd = move_line.MoveLineCommand(
            self._receiver, translation, rotation, tag)
        self._stream_commander.add_command(cmd)
        await self._stream_commander.execute_commands()
