#!/usr/bin/env python3

""" Defines the MoveJointsInterpolatedFunction. """

import asyncio
from asyncio import AbstractEventLoop

from awtube.functions.robot_function import RobotFunction
from awtube.commands.move_joints_interpolated import MoveJointsInterpolatedCommand
from awtube.commanders.stream import StreamCommander
from awtube.command_receiver import CommandReceiver


class MoveJointsInterpolatedFunction(RobotFunction):
    def __init__(self,
                 stream_commander: StreamCommander,
                 receiver: CommandReceiver,
                 loop: AbstractEventLoop) -> None:
        self._stream_commander = stream_commander
        self._receiver = receiver
        self._loop = loop

    def move_joints_interpolated(self, points) -> None:
        """ Send a moveLine command to a CommandReceiver
        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        self._loop.run_until_complete(
            self.move_joints_interpolated_async(points))

    async def move_joints_interpolated_async(self, points) -> None:
        """ Send a moveLine command to a CommandReceiver
        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        for pt in points:
            cmd = MoveJointsInterpolatedCommand(
                receiver=self._receiver,
                joint_positions=pt.positions,
                joint_velocities=pt.velocities)
            self._stream_commander.add_command(cmd)
        await self._stream_commander.execute_commands(wait_done=True)
