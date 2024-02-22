#!/usr/bin/env python3

""" Defines the Stream commander which implements Commander Interface. """

from __future__ import annotations
import asyncio
import queue
import logging
from typing import AsyncGenerator
import copy

from awtube.observers.stream import StreamObserver
from awtube.commanders.commander import Commander
from awtube.commands.command import Command
from awtube.types.gbc import StreamState
from awtube.types.function_result import FunctionResult

from awtube.logging import config


class StreamCommander(Commander):
    """
    The StreamCommander is associated with one or several commands. It manages
    the logic of executing commands based on the stream capacity.
    """

    def __init__(self, stream_observer: StreamObserver, capacity_min: int = 15) -> None:
        """
        Initialize commands.
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        self._stream_observer: StreamObserver = stream_observer
        self._command_queue: queue.Queue[Command] = queue.Queue()
        self._capacity_min: int = capacity_min
        self.__tag = None

        # stream observer None count
        self._stream_observer_tentatives = 0
        self._stream_observer_max_tentatives = 10

    def add_command(self, command: Command) -> None:
        """ Add commands to be sent """
        self._command_queue.put(command)

    async def wait_for_cmd_execution(self, command: Command) -> FunctionResult:
        command.execute()

        while True:
            # if self._stream_observer.payload.tag > command.tag:
            #     # means we finished task too fast to recieve feedback
            #     return FunctionResult.SUCCESS

            if self._stream_observer.payload.tag == command.tag and self._stream_observer.payload.state == StreamState.IDLE:
                # if no feedback for jobs with smaller tag finish them too
                # if
                # print(
                #     f'done movement!!!!!!!: {self._stream_observer.payload.tag}')
                # returning we finish the task
                return FunctionResult.SUCCESS
            await asyncio.sleep(0.2)

    async def execute_commands(self) -> AsyncGenerator[asyncio.Task]:
        """ Asyncio Generator which takes messages from object's queue and executes them, 
            respecting the capacity of the stream, which in the meantime yields asyncio.Task 
            objects that represent the stream activities requested to GBC. 
        """

        self._logger.debug('Started execution of stream commands.')

        while True:
            if self._command_queue.empty():
                break

            if self._stream_observer_tentatives >= self._stream_observer_max_tentatives:
                raise Exception("Couldn't update StreamObserver.")

            if not self._stream_observer.payload:
                self._stream_observer_tentatives += 1
                await asyncio.sleep(0.1)
                print('StreamObserver is None')
                continue
            else:
                # get last tag from motion controller
                if not self.__tag:
                    self.__tag = self._stream_observer.payload.tag
                self._stream_observer_tentatives = 0

            if self._stream_observer.payload.capacity >= self._capacity_min:
                cmd: Command = self._command_queue.get(block=False)

                cmd.tag = copy.copy(self.__tag)
                task: asyncio.Task = asyncio.create_task(
                    self.wait_for_cmd_execution(cmd))
                self.__tag += 1
                yield task
                await asyncio.sleep(0.02)
            else:
                await asyncio.sleep(0.1)
