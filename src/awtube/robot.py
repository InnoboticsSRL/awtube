#!/usr/bin/env python3

"""                                        
    Class which puts everything together, commanders, observers and robot functions.
    This class defines the API of the robot, the user interfaces with this class.
    
    This API basically is divided into two subprocesses where the primary subprocess is 
    a sort of frontend where new commands are queued and the secondary subprocess does 
    the looping needed to maintain alive the connection with the motion controller and 
    execute those queued commands.
"""

from __future__ import annotations
import logging
import typing as tp

from . import command_receiver, observers, threadloop, controllers, errors, commands, types, cia402


class Robot:
    """
        Class which puts everything together, commanders, observers and robot functions.
    """

    def __init__(self,
                 robot_ip: str = "0.0.0.0",
                 port: str = "9001",
                 config_path: str = None,
                 name: str = "AWTube",
                 log_level: int | str = logging.INFO,
                 logger: logging.Logger | None = None):
        self._log_level = log_level
        self._logger = logging.getLogger(
            self.__class__.__name__) if logger is None else logger
        # self._logger.setLevel(self._log_level)
        self.tloop = threadloop.threadloop
        self.tloop.start()
        self.killed: bool = False
        self._name = name
        self._robot_ip = robot_ip
        self._port = port
        self.receiver = command_receiver.WebsocketThread(
            f"ws://{self._robot_ip}:{self._port}/ws")
        self.stream_observer = observers.StreamObserver()
        self.telemetry_observer = observers.TelemetryObserver()
        self.status_observer = observers.StatusObserver()
        self.stream_controller = controllers.StreamController(
            self.stream_observer)
        self.machine_controller = controllers.MachineController(
            self.status_observer)
        self.receiver.attach_observer(self.telemetry_observer)
        self.receiver.attach_observer(self.stream_observer)
        self.receiver.attach_observer(self.status_observer)

    def kill(self):
        """ Cancel tasks and stop loop from sync, threadsafe """
        self._logger.debug('Killing robot.')
        self.killed = True
        self.disable()
        if threadloop.threadloop.loop.is_running():
            self.tloop.stop()

    def start(self) -> None:
        """ The startup procedure for the sync API """
        self.tloop.post(self.receiver.listen())
        self.tloop.post(self.stream_controller.start())
        self.tloop.post(self.machine_controller.start())

    # def reset(self) -> None:
    #     """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state. """
    #     self.tloop.post_wait(self.reset_async())
    #     self._logger.debug('Robot is reset!')

    # async def reset_async(self):
    #     """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state async"""
    #     self.machine_controller.schedule_first(
    #         commands.HeartbeatCommad(self.receiver, frequency=1))
    #     # self._machine_controller.schedule_last(
    #     #     commands.MachineStateCommad(self._receiver,
    #     #                                 desired_state=cia402.CIA402MachineState.FAULT))
    #     # self._machine_controller.schedule_last(
    #     #     commands.IoutCommad(self._receiver, 10878720, override=True))
    #     switch_on_disabled = self.machine_controller.schedule_last(
    #         commands.MachineStateCommad(self.receiver,
    #                                     desired_state=cia402.CIA402MachineState.SWITCH_ON_DISABLED))
    #     return await switch_on_disabled

    def enable(self) -> None:
        """ Enable connection with GBC, commanding to go to OPERATION_ENABLED state. """
        self.tloop.post_wait(self.enable_async())
        self._logger.debug('Robot is enabled!')

    async def enable_async(self):
        self.machine_controller.schedule_first(
            commands.HeartbeatCommad(self.receiver, frequency=1))
        operational = self.machine_controller.schedule_last(
            commands.MachineStateCommad(self.receiver,
                                        desired_state=cia402.CIA402MachineState.OPERATION_ENABLED))
        return await operational

    def disable(self) -> None:
        """ Disable connection with GBC. """
        self.tloop.post_wait(self.disable_async())
        self._logger.debug('Robot is disabled!')

    async def disable_async(self):
        disabled = self.machine_controller.schedule_last(
            commands.MachineStateCommad(self.receiver,
                                        desired_state=cia402.CIA402MachineState.SWITCH_ON_DISABLED))
        return await disabled

    def set_dout(self, position: int, value: int, override: bool = True) -> None:
        self.tloop.post_wait(self.set_dout_async(
            position=position,
            value=value,
            override=override))
        self._logger.debug(
            'Set dout value:%s with override%s!', value, override)

    async def set_dout_async(self, position: int, value: int, override: bool) -> None:
        return await self.machine_controller.schedule_last(
            commands.DoutCommad(self.receiver,
                                position=position,
                                value=value,
                                override=override))

    def set_speed(self, value: float) -> None:
        """ Set speed (0-2). """
        self.tloop.post_wait(self.set_speed_async(value))
        self._logger.debug('Velocity is set to %.2f.', value)

    def disable_limits(self, value: bool = True) -> None:
        """ Disable internal safe limits of motion controller. """
        self.tloop.post_wait(self.disable_limits_async(value))
        self._logger.debug('Safe limits is set to %s.', value)

    async def disable_limits_async(self, value: bool):
        task = self.machine_controller.schedule_first(
            commands.KinematicsConfigurationCommad(
                self.receiver, disable_limits=value)
        )
        return await task

    async def set_speed_async(self, value: float):
        task = self.machine_controller.schedule_first(
            commands.KinematicsConfigurationCommad(
                self.receiver, target_feed_rate=value)
        )
        return await task

    def __cmd(self, command: types.StreamCommandType):
        cmd = commands.StreamCommand(self.receiver,
                                     command=command)
        self.stream_controller.schedule_first(cmd)

    def stop_stream(self) -> None:
        """ Stop stream. Sets velocity to zero, to restart increase velocity and call run() """
        self.__cmd(types.StreamCommandType.STOP)

    def pause_stream(self) -> None:
        """ Pause stream. Sets velocity to zero, to restart increase velocity and call run() """
        self.__cmd(types.StreamCommandType.PAUSE)

    def run_stream(self) -> None:
        """ Run stream. Used after stopping or pausing."""
        self.__cmd(types.StreamCommandType.RUN)

    def move_joints_interpolated(self, points) -> None:
        """ Send a trajectory. """
        self.tloop.post_wait(self.move_joints_interpolated_async(points))

    async def move_joints_interpolated_async(self, points) -> None:
        """ Send a moveLine command to be executed by the controller. """
        cmds = [commands.MoveJointsInterpolatedCommand(
                receiver=self.receiver,
                joint_positions=pt.positions,
                joint_velocities=pt.velocities) for pt in points]

        return await self.stream_controller.schedule_last(cmds)

    def move_line(self,
                  translation: tp.Dict[str, float],
                  rotation: tp.Dict[str, float]) -> None:
        """ Send a moveLine command.

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
        cmd = commands.MoveLineCommand(
            self.receiver, translation, rotation)
        task = self.stream_controller.schedule_last(cmd)
        return await task

    def move_to_position(self,
                         translation: tp.Dict[str, float],
                         rotation: tp.Dict[str, float],
                         tag: int = 0) -> None:
        """ Send a moveToPosition command.

        Args:
            translation (tp.Dict[str, float]): dict of translation x, y, z
            rotation (tp.Dict[str, float]): Dict of rotation, a quaternion: x, y, z, w
            tag (int, optional): tag(id) with which to send the command to the robot. Defaults to 0.
        """
        self.tloop.post_wait(self.move_to_position_async(translation,
                                                         rotation))
        self._logger.debug('moveLine done')

    async def move_to_position_async(self,
                                     translation: tp.Dict[str, float],
                                     rotation: tp.Dict[str, float]) -> None:
        pose = types.Pose(position=types.Position(**translation),
                          orientation=types.Quaternion(**rotation))
        cmd = commands.MoveToPositionCommand(self.receiver, pose)
        task = self.stream_controller.schedule_last(cmd)
        return await task
