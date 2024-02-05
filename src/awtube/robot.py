from __future__ import annotations
import logging as lg
import asyncio

from awtube.aw_types import *
from awtube.gbc_types import *
from awtube.commands import *
from awtube.exceptions import *
from awtube.websocket_thread import WebsocketThread

# Commands and Commanders
from awtube.command_reciever import CommandReciever
from awtube.commanders.stream_commander import StreamCommander
from awtube.commanders.machine_commander import MachineCommander

# Observers
from awtube.observers.stream_observer import StreamObserver
from awtube.observers.telemetry_observer import TelemetryObserver
from awtube.observers.machine_observer import MachineObserver

# Robot functions
from awtube.api.move_joints_interpolated_function import MoveJointsInterpolatedFunction
from awtube.api.move_line_function import MoveLineFunction
from awtube.api.enable_function import EnableFunction


class Robot(MoveJointsInterpolatedFunction,
            MoveLineFunction,
            EnableFunction):
    """
        Class which puts everything together, commanders, observers and robot functions.
    """

    def __init__(self,
                 robot_ip: str = "0.0.0.0",
                 port: str = "9001",
                 config_path: str = None,
                 name: str = "AWTube",
                 log_level: int | str = lg.DEBUG,
                 logger: lg.Logger | None = None):
        self._name = name
        self._robot_ip = robot_ip
        self._port = port

        # logging
        if logger:
            self._logger = logger
        else:
            self._logger = lg.getLogger(self._name)
            self._logger.setLevel(lg.DEBUG)

        # Command reciever
        self.receiver: CommandReciever = WebsocketThread(
            f"ws://{self._robot_ip}:{self._port}/ws")

        # Observers
        self.stream_observer = StreamObserver()
        self.telemetry_observer = TelemetryObserver()
        self.machine_observer = MachineObserver()

        # Commanders
        self.stream_commander = StreamCommander(self.stream_observer)
        self.machine_commander = MachineCommander(self.machine_observer)
        # TODO: fix, all commanders should have the same interface
        self.machine_commander.reciever = self.receiver

        # Register observers
        self.receiver.attach_observer(self.stream_observer)
        self.receiver.attach_observer(self.telemetry_observer)
        self.receiver.attach_observer(self.machine_observer)

        # Define robot functions
        MoveJointsInterpolatedFunction.__init__(self,
                                                self.stream_commander,
                                                self.receiver)
        MoveLineFunction.__init__(self,
                                  self.stream_commander,
                                  self.receiver)
        EnableFunction.__init__(self,
                                self.machine_commander,
                                self.receiver)

    async def startup(self) -> None:
        """ Start the whole process of listening and commanding. """
        await asyncio.gather(self.receiver.listen(),
                             self.machine_commander.execute_commands())
