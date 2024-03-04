#!/usr/bin/env python3

""" Robot functions. """

from abc import ABC
import typing as tp
import logging


from . import controllers, types, cia402, command_receiver, commands

_logger = logging.getLogger(__name__)


class RobotFunction(ABC):
    """ RobotFunction Interface used to implement different functions fo the robot. """
    pass


class MachineFunctions(RobotFunction):
    """ Enable connection with GBC. """

    def __init__(self,
                 machine_controller: controllers.MachineController,
                 receiver: command_receiver.CommandReceiver,
                 ) -> None:
        self._machine_controller = machine_controller
        self._receiver = receiver

    # not yet ready
    # def reset(self) -> None:
    #     """ Reset faults with GBC, commanding to go to SWITCHED_ON state. """
    #     cmd = commands.MachineStateCommad(self._receiver,
    #                                       desired_state=cia402.CIA402MachineState.SWITCHED_ON)
    #     self._machine_commander.add_command(cmd)

    def reset(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state. """
        self.tloop.post_wait(self.reset_async())
        _logger.debug('Robot is reset!')

    async def reset_async(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state async"""
        self._machine_controller.schedule_first(
            commands.HeartbeatCommad(self._receiver, frequency=1))
        # self._machine_controller.schedule_last(
        #     commands.MachineStateCommad(self._receiver,
        #                                 desired_state=cia402.CIA402MachineState.FAULT))
        # self._machine_controller.schedule_last(
        #     commands.IoutCommad(self._receiver, 10878720, override=True))
        switch_on_disabled = self._machine_controller.schedule_last(
            commands.MachineStateCommad(self._receiver,
                                        desired_state=cia402.CIA402MachineState.SWITCH_ON_DISABLED))
        return await switch_on_disabled

    def enable(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state. """
        self.tloop.post_wait(self.enable_async())
        _logger.debug('Robot is enabled!')

    async def enable_async(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state async"""
        # self._machine_controller.schedule_first(
        #     commands.HeartbeatCommad(self._receiver, frequency=1))
        cia402_task_wrapper = self._machine_controller.schedule_last(
            commands.MachineStateCommad(self._receiver,
                                        desired_state=cia402.CIA402MachineState.OPERATION_ENABLED))
        return await cia402_task_wrapper


class StreamCommandFunction(RobotFunction):
    """
        Stream functions, enable, stop, pause and run.
        Stop and pause force the feedrate to 0.
    """

    def __init__(self,
                 stream_controller: controllers.StreamController,
                 receiver: command_receiver.CommandReceiver) -> None:
        self._stream_controller = stream_controller
        self._receiver = receiver

    def __cmd(self, command: types.StreamCommandType):
        cmd = commands.StreamCommand(self._receiver,
                                     command=command)
        self._stream_controller.schedule_first(cmd)

    def stop_stream(self) -> None:
        """ Stop stream. """
        self.__cmd(types.StreamCommandType.STOP)

    def pause_stream(self) -> None:
        """ Pause stream. """
        self.__cmd(types.StreamCommandType.PAUSE)

    def run_stream(self) -> None:
        """ Run stream. Used after pausing."""
        self.__cmd(types.StreamCommandType.RUN)


class MoveJointsInterpolatedFunction(RobotFunction):
    """ Robot function to move robot with a trajectory, where GBC interpolates intermediate points. """

    def __init__(self,
                 stream_controller: controllers.StreamController,
                 receiver: command_receiver.CommandReceiver,
                 ) -> None:
        self._stream_commander = stream_controller
        self._receiver = receiver

    def move_joints_interpolated(self, points) -> None:
        """ Send a moveLine command to a command_receiver.CommandReceiver. """
        self.tloop.post_wait(self.move_joints_interpolated_async(points))

    async def move_joints_interpolated_async(self, points) -> None:
        """ Send a moveLine command. """
        cmds = [commands.MoveJointsInterpolatedCommand(
                receiver=self._receiver,
                joint_positions=pt.positions,
                joint_velocities=pt.velocities) for pt in points]

        return await self._stream_controller.schedule_last(cmds)


class MoveLineFunction(RobotFunction):
    def __init__(self,
                 stream_controller: controllers.StreamController,
                 receiver: command_receiver.CommandReceiver,
                 ) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stream_controller = stream_controller
        self._receiver = receiver

    def move_line(self,
                  translation: tp.Dict[str, float],
                  rotation: tp.Dict[str, float]) -> None:
        """ Send a moveLine command to a command_receiver.CommandReceiver, but a blocking call.

        Args:
            translation (tp.Dict[str, float]): {'x', 'y', 'z'}
            rotation (tp.Dict[str, float]): Quaternion {'x', 'y', 'z', 'w'}
        """
        self.tloop.post_wait(self.move_line_async(translation,
                                                  rotation))
        self._logger.debug('moveLine done')

    async def move_line_async(self,
                              translation: tp.Dict[str, float],
                              rotation: tp.Dict[str, float]) -> types.FunctionResult:
        """ Send a moveLine command to a command_receiver.CommandReceiver.

        Args:
            translation (tp.Dict[str, float]): {'x', 'y', 'z'}
            rotation (tp.Dict[str, float]): Quaternion {'x', 'y', 'z', 'w'}
        """
        cmd = commands.MoveLineCommand(
            self._receiver, translation, rotation)
        task = self._stream_controller.schedule_last(cmd)
        return await task


# class MoveToPositioinFunction(RobotFunction):
#     """ Send moveToPosition command. """

#     def __init__(self, stream_commander: StreamCommander, receiver: command_receiver.CommandReceiver) -> None:
#         self._stream_commander = stream_commander
#         self._receiver = receiver

#     async def move_to_position(self,
#                                translation: tp.Dict[str, float],
#                                rotation: tp.Dict[str, float],
#                                tag: int = 0) -> None:
#         """ Send a moveLine command to a command_receiver.CommandReceiver.

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
