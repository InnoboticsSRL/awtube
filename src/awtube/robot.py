#!/usr/bin/env python3

""" 
    Robot offers all possible ways to interact with the machine.
    
    Example:

    .. code-block:: python
      
      from awtube.robot import Robot
      
      robot = Robot('192.168.0.0', port='9001')
      
      # to start communication with robot
      robot.start()
      
      # set the target of the system to either be the physical machine or the simulation
      from awtube.types import MachineTarget
      robot.set_machine_target(MachineTarget.SIMULATION)

      # to enable the robot, activate the actuators
      robot.enable()

      # send a move_line command
      robot.move_line(
                {"x": 400,
                "y": -50,
                "z": 650},
                {"x": 0.8660254037844387,
                "y": 3.0616169978683824e-17,
                "z": 0.49999999999999994,
                "w": 5.3028761936245346e-17})
      
      # send a move_joints command
      robot.move_joints([0,0,0,0,0,0])
      
      # set digital out
      robot.set_dout(0,1)
      
      # send serial command through modbus RTU
      robot.send_serial(0,'01 06 01 00 00 A5 48 4D')
      
      # disable the robot, deactivate actuators
      robot.disable()

      # kill connection
      robot.kill()
                               
"""

from __future__ import annotations
import logging
import typing as tp

from . import command_receiver, controllers, observers, threadloop, errors, commands, types, cia402


class Robot:
    """Robot class used to interact with the robot arm."""

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
        """ Stop communication with robot. """
        # Cancel tasks and stop loop from sync, threadsafe
        self._logger.debug('Killing robot.')
        self.disable()
        self.killed = True
        self.disable()
        if threadloop.threadloop.loop.is_running():
            self.tloop.stop()

    def start(self):
        """ Start communication with robot. """
        self.tloop.post(self.receiver.listen())
        self.tloop.post(self.stream_controller.start())
        self.tloop.post(self.machine_controller.start())

    # def reset(self):
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

    def enable(self):
        """Sync wrapper for :func:`~awtube.robot.Robot.enable_async`"""
        self.tloop.post_wait(self.enable_async(), timeout=15)
        self._logger.debug('Robot is enabled!')

    async def enable_async(self):
        """ Enable machine by setting it's state to OPERATION_ENABLED coroutine. """
        self.machine_controller.schedule_first(
            commands.HeartbeatCommad(self.receiver, frequency=1))
        operational = self.machine_controller.schedule_last(
            commands.MachineStateCommad(self.receiver,
                                        desired_state=cia402.CIA402MachineState.OPERATION_ENABLED))
        return await operational

    def disable(self):
        """Sync wrapper for :func:`~awtube.robot.Robot.disable_async`"""
        self.tloop.post_wait(self.disable_async())
        self._logger.debug('Robot is disabled!')

    async def disable_async(self):
        """ Disable robot. """
        disabled = self.machine_controller.schedule_last(
            commands.MachineStateCommad(self.receiver,
                                        desired_state=cia402.CIA402MachineState.SWITCH_ON_DISABLED))
        return await disabled

    def set_dout(self, position: int, value: int, override: bool = True):
        """Sync wrapper for :func:`~awtube.robot.Robot.set_dout_async`"""
        self.tloop.post_wait(self.set_dout_async(
            position=position,
            value=value,
            override=override))
        self._logger.debug(
            'Set dout value:%s with override:%s.', value, override)

    async def set_dout_async(self, position: int, value: int, override: bool):
        """ Send set digital out command. """
        task = self.machine_controller.schedule_last(
            commands.DoutCommad(self.receiver,
                                position=position,
                                value=value,
                                override=override))
        return await task

    def send_serial(self, position: int, hex_string: int):
        """Sync wrapper for :func:`~awtube.robot.Robot.send_serial_async`"""
        self.tloop.post_wait(self.send_serial_async(
            position,
            hex_string))

    async def send_serial_async(self, position: int, hex_string: int):
        """ Send serial command. """
        task = self.machine_controller.schedule_last(
            commands.SerialCommad(self.receiver,
                                  data=hex_string))
        return await task

    def set_machine_target(self, target: types.MachineTarget):
        self.tloop.post_wait(self.set_machine_target_async(target=target))
        self._logger.debug(
            'Set machine target:%s.', target)

    async def set_machine_target_async(self, target: types.MachineTarget):
        return await self.machine_controller.schedule_last(
            commands.MachineTargetCommad(self.receiver, target=target))

    def set_speed(self, value: float):
        """ Set speed (0.0-2.0). """
        self.tloop.post_wait(self.set_speed_async(value))
        self._logger.debug('Velocity is set to %.2f.', value)

    async def set_speed_async(self, value: float):
        task = self.machine_controller.schedule_first(
            commands.KinematicsConfigurationCommad(
                self.receiver, target_feed_rate=value)
        )
        return await task

    def set_safe_limits(self, value: bool = True):
        """ Disable internal safe limits of motion controller. """
        self.tloop.post_wait(self.set_safe_limits_async(value))
        self._logger.debug('Safe limits is set to %s.', value)

    async def set_safe_limits_async(self, value: bool):
        task = self.machine_controller.schedule_first(
            commands.KinematicsConfigurationCommad(
                self.receiver, safe_limits=value)
        )
        return await task

    def __cmd(self, command: types.StreamCommandType):
        cmd = commands.StreamCommand(self.receiver,
                                     command=command)
        self.stream_controller.schedule_first(cmd)

    def stop_stream(self):
        """ Stop stream. Sets velocity to zero, to restart increase velocity and call run() """
        self.__cmd(types.StreamCommandType.STOP)

    def pause_stream(self):
        """ Pause stream. Sets velocity to zero, to restart increase velocity and call run() """
        self.__cmd(types.StreamCommandType.PAUSE)

    def run_stream(self):
        """ Run stream. Used after stopping or pausing."""
        self.__cmd(types.StreamCommandType.RUN)

    def move_joints_interpolated(self, points):
        """ Send a trajectory. """
        self.tloop.post_wait(self.move_joints_interpolated_async(points))

    async def move_joints_interpolated_async(self, points):
        """ Send a moveLine command to be executed by the controller. """
        cmds = [commands.MoveJointsInterpolatedCommand(
                receiver=self.receiver,
                joint_positions=pt.positions,
                joint_velocities=pt.velocities) for pt in points]
        return await self.stream_controller.schedule_last(cmds)

    def move_line(self,
                  translation: tp.Dict[str, float],
                  rotation: tp.Dict[str, float]):
        """Sync wrapper for :func:`~awtube.robot.Robot.move_line_async`"""

        self.tloop.post_wait(self.move_line_async(translation,
                                                  rotation))

    async def move_line_async(self,
                              translation: tp.Dict[str, float],
                              rotation: tp.Dict[str, float]):
        """ Send a moveLine command.
            translation dict with keys {'x', 'y', 'z'}
            rotation dict with keys {'x', 'y', 'z', 'w'}
        """
        cmd = commands.MoveLineCommand(
            self.receiver, translation, rotation)
        task = self.stream_controller.schedule_last(cmd)
        return await task

    def move_joints(self, joints: list):
        """Sync wrapper for :func:`~awtube.robot.Robot.move_joints_async`"""

        self.tloop.post_wait(self.move_joints_async(joints))

    async def move_joints_async(self, joints: list):
        """ Send a moveJoints command. Joint position values are in radians."""
        cmd = commands.MoveJointsCommand(
            self.receiver, joint_positions=joints)
        task = self.stream_controller.schedule_last(cmd)
        return await task

    def move_to_position(self,
                         translation: tp.Dict[str, float],
                         rotation: tp.Dict[str, float],
                         tag: int = 0):
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
                                     rotation: tp.Dict[str, float]):
        cmd = commands.MoveToPositionCommand(self.receiver, translation,rotation)
        task = self.stream_controller.schedule_last(cmd)
        return await task
