#!/usr/bin/env python3

""" Defines the MoveLineFunction. """

import asyncio
import logging
import typing as tp

from awtube.types.gbc import StreamState

from awtube.functions.robot_function import RobotFunction
from awtube.commanders.stream import StreamCommander
from awtube.recievers.command_receiver import CommandReceiver
from awtube.commands import move_line
from awtube.types.function_result import FunctionResult

from awtube.logging import config


class MoveLineFunction(RobotFunction):
    def __init__(self,
                 stream_commander: StreamCommander,
                 receiver: CommandReceiver,
                 loop: asyncio.AbstractEventLoop = None) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stream_commander = stream_commander
        self._receiver = receiver
        self._loop = loop

    def move_line(self,
                  translation: tp.Dict[str, float],
                  rotation: tp.Dict[str, float],
                  tag: int = 0) -> None:
        """ Send a moveLine command to a CommandReceiver, but a blocking call.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        futur = asyncio.run_coroutine_threadsafe(self.move_line_async(translation,
                                                                      rotation,
                                                                      tag),
                                                 loop=self._loop)
        return futur.result()

    async def move_line_async(self,
                              translation: tp.Dict[str, float],
                              rotation: tp.Dict[str, float],
                              tag: int = 0) -> FunctionResult:
        """ Send a moveLine command to a CommandReceiver.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        self._logger.debug('Started moveLine.')
        # loop = asyncio.get_running_loop()
        cmd = move_line.MoveLineCommand(
            self._receiver, translation, rotation, tag)
        self._stream_commander.add_command(cmd)
        execution = self._stream_commander.execute_commands()
        task = await anext(execution)
        result = await task
        self._logger.debug('moveLine done with result: %s.', result)

        return result
