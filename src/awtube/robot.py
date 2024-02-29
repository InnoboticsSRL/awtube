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
import asyncio
import logging
import concurrent.futures
import threading

from awtube.command_receiver import CommandReceiver, WebsocketThread
from awtube.commanders import StreamCommander, MachineCommander
from awtube.observers import StreamObserver, TelemetryObserver, StatusObserver
import awtube.robot_functions as robot_functions
from awtube.types import MachineTarget

import awtube.commands as commands

import awtube.controllers as controllers

import awtube.logging_config

from awtube.threadloop import ThreadLoop


class Robot(
        # threading.Thread,
        robot_functions.MoveJointsInterpolatedFunction,
        robot_functions.MoveLineFunction,
        robot_functions.EnableFunction,
        robot_functions.MoveToPositioinFunction,
        robot_functions.StreamCommandFunction
):
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
        # thread
        # threading.Thread.__init__(self)
        # self.daemon = True

        # loop
        # self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        # asyncio.set_event_loop(self.loop)

        self.tloop = ThreadLoop()
        self.tloop.start()

        self.killed: bool = False

        # self.executor = concurrent.futures.ThreadPoolExecutor()

        # robot properties
        self._name = name
        self._robot_ip = robot_ip
        self._port = port

        # logging
        # to do fix logging level
        self._log_level = log_level
        self._logger = logging.getLogger(
            self.__class__.__name__) if logger is None else logger
        self._logger.setLevel(self._log_level)

        # Command receiver
        self.receiver: CommandReceiver = WebsocketThread(
            f"ws://{self._robot_ip}:{self._port}/ws")

        # Observers
        self.stream_observer = StreamObserver()
        self.telemetry_observer = TelemetryObserver()
        self.status_observer = StatusObserver()

        # Commanders
        self.stream_commander = StreamCommander(self.stream_observer)
        # self.machine_commander = MachineCommander(self.status_observer)
        self.machine_controller = controllers.MachineController(
            self.status_observer)
        # TODO: fix, all same type commanders should have the same interface
        self.machine_controller.receiver = self.receiver

        # Register observers
        self.receiver.attach_observer(self.telemetry_observer)
        self.receiver.attach_observer(self.stream_observer)
        self.receiver.attach_observer(self.status_observer)

        # Define robot functions api
        robot_functions.MoveJointsInterpolatedFunction.__init__(self,
                                                                self.stream_commander,
                                                                self.receiver
                                                                )
        robot_functions.MoveLineFunction.__init__(self,
                                                  self.stream_commander,
                                                  self.receiver
                                                  )
        robot_functions.MoveToPositioinFunction.__init__(self,
                                                         self.stream_commander,
                                                         self.receiver
                                                         )
        robot_functions.EnableFunction.__init__(self,
                                                self.machine_controller,
                                                self.receiver
                                                )
        robot_functions.StreamCommandFunction.__init__(self,
                                                       self.stream_commander,
                                                       self.receiver
                                                       )

        # test
        # self.machine_commander.limits_disabled = True
        # self.machine_commander.velocity = 2
        # self.machine_commander.target = MachineTarget.SIMULATION

    # def __enter__(self):
    #     """ Context manager for running the websocket """
    #     self.start()
    #     return self

    # def __exit__(self, *_):
    #     """ Context manager for cleaning up event loop and thread """
    #     if not self.killed:
    #         self.kill()
    #     self.join()

    def run(self):
        """ Main execution of the thread. Is called when entering context """
        # self.loop.create_task(self.receiver.listen())
        # self.loop.create_task(self.machine_controller.start())
        # self.loop.run_forever()

        self.tloop.post(self.receiver.listen())
        self.tloop.post(self.machine_controller.start())

    def kill(self):
        """ Cancel tasks and stop loop from sync, threadsafe """
        self._logger.debug('Killing robot.')
        self.killed = True
        # asyncio.run_coroutine_threadsafe(self.stop_loop(), self.loop)
        self.tloop.stop()

    # async def stop_loop(self):
        # """ Cancel tasks and stop loop, must be called threadsafe """
        # tasks = [
        #     task
        #     for task in asyncio.all_tasks()
        #     if task is not asyncio.current_task()
        # ]
        # for task in tasks:
        #     task.cancel()

        # await asyncio.gather(*tasks, return_exceptions=True)
        # self.loop.stop()
        # self.join()

    # async def startup_async(self) -> None:
    #     """ Start the whole process of listening and commanding. """
    #     await asyncio.gather(self.receiver.listen())

    def startup(self) -> bool:
        """
            The startup procedure for the sync API.
            Run the procedure and return when the 
            robot is ready to take new commands.
        """
        # self.start()
        # self.loop.call_soon_threadsafe(self.run())
        self.run()
        return True
