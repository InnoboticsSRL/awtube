#!/usr/bin/env python3

""" Defines the MoveLineFunction. """

import asyncio
import typing as tp

from awtube.types.gbc import StreamState

from awtube.functions.robot_function import RobotFunction
from awtube.commanders.stream import StreamCommander
from awtube.command_receiver import CommandReceiver
from awtube.commands import move_line


class MoveLineFunction(RobotFunction):
    def __init__(self,
                 stream_commander: StreamCommander,
                 receiver: CommandReceiver,
                 loop: asyncio.AbstractEventLoop = None) -> None:
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
        self._loop.run_until_complete(self.move_line_async(translation,
                                                           rotation,
                                                           tag))

    async def move_line_async(self,
                              translation: tp.Dict[str, float],
                              rotation: tp.Dict[str, float],
                              tag: int = 0) -> None:
        """ Send a moveLine command to a CommandReceiver.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        print('start async move_line')
        # loop = asyncio.get_running_loop()
        cmd = move_line.MoveLineCommand(
            self._receiver, translation, rotation, tag)
        self._stream_commander.add_command(cmd)
        await self._stream_commander.execute_commands()

        print('wait async check')

        # give it 1 sec to update stream_observer
        await asyncio.sleep(1)

        # TODO: really important
        # logic here to improve clear
        while self.stream_observer.payload.state == StreamState.ACTIVE:
            # print('Active !!!')
            await asyncio.sleep(0.2)
        while True:
            if self.stream_observer.payload.tag == tag and self.stream_observer.payload.state == StreamState.IDLE:
                print(f'done movement: {self.stream_observer.payload.state}')
                return True
            print(f'not yet: {self.stream_observer.payload.state}')
            await asyncio.sleep(0.05)
