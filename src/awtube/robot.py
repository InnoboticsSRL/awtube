#!/usr/bin/env python3

"""
    Class which puts everything together, commanders, observers and robot functions.
    This class defines the API of the robot, the user interfaces with this class.
"""

from __future__ import annotations
import asyncio
import logging
from awtube.websocket_thread import WebsocketThread

# Commands and Commanders
from awtube.command_reciever import CommandReciever
from awtube.commanders.stream import StreamCommander
from awtube.commanders.machine import MachineCommander

# Observers
from awtube.observers.stream import StreamObserver
from awtube.observers.telemetry import TelemetryObserver
from awtube.observers.status import StatusObserver

# Robot functions
from awtube.functions.move_joints_interpolated import MoveJointsInterpolatedFunction
from awtube.functions.move_line import MoveLineFunction
from awtube.functions.enable import EnableFunction
from awtube.functions.move_to_position import MoveToPositioinFunction

# logging
from awtube.logging import config


class Robot(MoveJointsInterpolatedFunction,
            MoveLineFunction,
            EnableFunction,
            MoveToPositioinFunction):
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
        self._name = name
        self._robot_ip = robot_ip
        self._port = port

        # logging
        # to do fix logging level
        self._log_level = log_level
        self._logger = logging.getLogger(
            self.__class__.__name__) if logger is None else logger
        self._logger.setLevel(self._log_level)

        # Command reciever
        self.receiver: CommandReciever = WebsocketThread(
            f"ws://{self._robot_ip}:{self._port}/ws")

        # Observers
        self.stream_observer = StreamObserver()
        self.telemetry_observer = TelemetryObserver()
        self.status_observer = StatusObserver()

        # Commanders
        self.stream_commander = StreamCommander(self.stream_observer)
        self.machine_commander = MachineCommander(self.status_observer)
        # TODO: fix, all commanders should have the same interface
        self.machine_commander.reciever = self.receiver

        # Register observers
        self.receiver.attach_observer(self.stream_observer)
        self.receiver.attach_observer(self.telemetry_observer)
        self.receiver.attach_observer(self.status_observer)

        # Define robot functions
        MoveJointsInterpolatedFunction.__init__(self,
                                                self.stream_commander,
                                                self.receiver)
        MoveLineFunction.__init__(self,
                                  self.stream_commander,
                                  self.receiver)
        MoveToPositioinFunction.__init__(self,
                                         self.stream_commander,
                                         self.receiver)
        EnableFunction.__init__(self,
                                self.machine_commander,
                                self.receiver)

    async def startup(self) -> None:
        """ Start the whole process of listening and commanding. """
        await asyncio.gather(self.receiver.listen(),
                             self.machine_commander.execute_commands())
