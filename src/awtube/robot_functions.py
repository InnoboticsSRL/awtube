#!/usr/bin/env python3

""" Robot functions. """

from abc import ABC
import typing as tp
import logging
import asyncio
import time

import awtube.logging_config

import awtube.types as types
import awtube.commands as commands
from awtube.types import Pose, Position, Quaternion, FunctionResult
from awtube.commanders import StreamCommander, MachineCommander
import awtube.commands as commands
from typing import Iterator, AsyncIterator
from asyncio import AbstractEventLoop
from awtube.cia402 import CIA402MachineState
from awtube.command_receiver import CommandReceiver

import awtube.controllers as controllers
import awtube.commands as commands

import awtube.logging_config

# TODO: improve the logger
_logger = logging.getLogger(__name__)

# TODO: sync wrapper for async functions ?


class RobotFunction(ABC):
    """ RobotFunction Interface used to implement different functions fo the robot. """
    pass


class EnableFunction(RobotFunction):
    """ Enable connection with GBC. """

    def __init__(self,
                 machine_controller: controllers.MachineController,
                 receiver: CommandReceiver,
                 ) -> None:
        self._machine_controller = machine_controller
        self._receiver = receiver

    # not yet ready
    # def reset(self) -> None:
    #     """ Reset faults with GBC, commanding to go to SWITCHED_ON state. """
    #     cmd = commands.MachineStateCommad(self._receiver,
    #                              desired_state=CIA402MachineState.SWITCHED_ON)
    #     self._machine_commander.add_command(cmd)

    def enable(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state. """
        self.tloop.post_wait(self.enable_async())
        _logger.debug('Robot is enabled!')

    async def enable_async(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state. """
        ht_task = self._machine_controller.schedule_first(
            commands.HeartbeatCommad(self._receiver, 0))

        # TODO: We should be able to know that the periodic
        # heartbeat task is running
        # await ht_task.task

        cia402_task_wrapper = self._machine_controller.schedule_last(commands.MachineStateCommad(self._receiver,
                                                                                                 desired_state=CIA402MachineState.OPERATION_ENABLED))
        return await cia402_task_wrapper


# class StreamCommandFunction(RobotFunction):
#     """
#         Stream functions, enable, stop, pause and run.
#         Stop and pause force the feedrate to 0.
#     """

#     def __init__(self,
#                  stream_commander: StreamCommander,
#                  receiver: CommandReceiver) -> None:
#         self._stream_commander = stream_commander
#         self._receiver = receiver

#     def __call_cmd(self, command: types.StreamCommandType):
#         cmd = commands.StreamCommand(self._receiver,
#                                      command=command)
#         self._stream_commander.add_command_at_beginning(cmd)

#     def stop_stream(self) -> None:
#         """ Stop stream. """
#         self.__call_cmd(types.StreamCommandType.STOP)

#     def pause_stream(self) -> None:
#         """ Pause stream. """
#         self.__call_cmd(types.StreamCommandType.PAUSE)

#     def run_stream(self) -> None:
#         """ Run stream. """
#         self.__call_cmd(types.StreamCommandType.RUN)


# class MoveJointsInterpolatedFunction(RobotFunction):
#     """ Robot function to move robot with a trajectory, where GBC interpolates intermediate points."""

#     def __init__(self,
#                  stream_commander: StreamCommander,
#                  receiver: CommandReceiver,
#                  #  loop: AbstractEventLoop
#                  ) -> None:
#         self._stream_commander = stream_commander
#         self._receiver = receiver
#         self._loop = self.tloop.loop

#     def move_joints_interpolated_gen(self, points) -> Iterator[FunctionResult]:
#         """ Async generator used to send a moveLine command to a CommandReceiver and recieve feedback on points done.
#         Args:
#             translation (tp.Dict[str, float]): dict of translation x, y, z
#             rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
#             tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
#         """
#         asyncio_generator = self.move_joints_interpolated_async_gen(points)

#         async def execut():
#             next_task = await anext(asyncio_generator)
#             return await next_task

#         while True:
#             try:
#                 fut = asyncio.run_coroutine_threadsafe(
#                     execut(), loop=self._loop)
#                 yield fut.result()
#             except StopAsyncIteration:
#                 break

#     def move_joints_interpolated(self, points) -> None:
#         """ Send a moveLine command to a CommandReceiver
#         Args:
#             translation (tp.Dict[str, float]): dict of translation x, y, z
#             rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
#             tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
#         """
#         self._loop.run_until_complete(
#             self.move_joints_interpolated_async_gen(points))

#     async def move_joints_interpolated_async_gen(self, points) -> AsyncIterator[asyncio.Task]:
#         """ Generator used to send MoveJointsInterpolatedCommands to the reciever and yield
#             asyncio.Tasks that give feedback on the execution of these commands.
#         Args:
#             translation (tp.Dict[str, float]): dict of translation x, y, z
#             rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
#             tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
#         """
#         for pt in points:
#             cmd = commands.MoveJointsInterpolatedCommand(
#                 receiver=self._receiver,
#                 joint_positions=pt.positions,
#                 joint_velocities=pt.velocities)
#             self._stream_commander.add_command(cmd)

#         async for task in self._stream_commander.execute_commands():
#             yield task


class MoveLineFunction(RobotFunction):
    def __init__(self,
                 stream_controller: controllers.StreamController,
                 receiver: CommandReceiver,
                 ) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stream_controller = stream_controller
        self._receiver = receiver

    def move_line(self,
                  translation: tp.Dict[str, float],
                  rotation: tp.Dict[str, float]) -> None:
        """ Send a moveLine command to a CommandReceiver, but a blocking call.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        self.tloop.post_wait(self.move_line_async(translation,
                                                  rotation))
        self._logger.debug('moveLine done')

    async def move_line_async(self,
                              translation: tp.Dict[str, float],
                              rotation: tp.Dict[str, float]) -> FunctionResult:
        """ Send a moveLine command to a CommandReceiver.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        cmd = commands.MoveLineCommand(
            self._receiver, translation, rotation)
        task = self._stream_controller.schedule_last(cmd)
        return await task


# class MoveToPositioinFunction(RobotFunction):
#     """ Send moveToPosition command. """

#     def __init__(self, stream_commander: StreamCommander, receiver: CommandReceiver) -> None:
#         self._stream_commander = stream_commander
#         self._receiver = receiver

#     async def move_to_position(self,
#                                translation: tp.Dict[str, float],
#                                rotation: tp.Dict[str, float],
#                                tag: int = 0) -> None:
#         """ Send a moveLine command to a CommandReceiver.

#         Args:
#             translation (tp.Dict[str, float]): dict of translation x, y, z
#             rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
#             tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
#         """
#         pose = Pose(position=Position(**translation),
#                     orientation=Quaternion(**rotation))
#         cmd = commands.MoveToPositionCommand(self._receiver, pose, tag)
#         self._stream_commander.add_command(cmd)
#         await self._stream_commander.execute_commands()
