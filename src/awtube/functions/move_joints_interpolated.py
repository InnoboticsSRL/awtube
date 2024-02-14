#!/usr/bin/env python3

""" Defines the MoveJointsInterpolatedFunction. """

import asyncio
from asyncio import AbstractEventLoop
from typing import Iterator, AsyncIterator

from awtube.functions.robot_function import RobotFunction
from awtube.commands.move_joints_interpolated import MoveJointsInterpolatedCommand
from awtube.commanders.stream import StreamCommander
from awtube.recievers.command_receiver import CommandReceiver
from awtube.types.function_result import FunctionResult


class MoveJointsInterpolatedFunction(RobotFunction):
    """ Robot function to move robot with a trajectory, where GBC interpolates intermediate points."""

    def __init__(self,
                 stream_commander: StreamCommander,
                 receiver: CommandReceiver,
                 loop: AbstractEventLoop) -> None:
        self._stream_commander = stream_commander
        self._receiver = receiver
        self._loop = loop

    def move_joints_interpolated_gen(self, points) -> Iterator[FunctionResult]:
        """ Async generator used to send a moveLine command to a CommandReceiver and recieve feedback on points done.
        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        loop = asyncio.get_event_loop()
        asyncio_generator = self.move_joints_interpolated_async_gen(points)

        async def exec(gen):
            # await next task from generator
            return await anext(gen)

        while True:
            try:
                result = loop.run_until_complete(
                    exec(asyncio_generator))
                yield result
            except StopAsyncIteration:
                break

    def move_joints_interpolated(self, points) -> None:
        """ Send a moveLine command to a CommandReceiver
        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        self._loop.run_until_complete(
            self.move_joints_interpolated_async_gen(points))

    async def move_joints_interpolated_async_gen(self, points) -> AsyncIterator[asyncio.Task]:
        """ Generator used to send a moveLine command to a CommandReceiver and recieve feedback on points done.
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

        async for task in self._stream_commander.execute_commands(wait_done=True):
            yield task
