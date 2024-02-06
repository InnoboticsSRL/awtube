#!/usr/bin/env python3

""" Defines the Stream commander which implements Commander Interface. """

from __future__ import annotations
import asyncio
import queue
import logging

from awtube.observers.stream import StreamObserver
from awtube.commanders.commander import Commander
from awtube.commands.command import Command

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
        self.__tag = 0

    def add_command(self, command: Command) -> None:
        """ Add commands to be sent """
        self._command_queue.put(command)

    async def execute_commands(self, wait_done: bool = False) -> None:
        """ Execute all commands, asyncio coroutine which takes messages from txbuffer and puts them in the outter queue,
            respecting the capacity of the stream. It awaits until there is space to add the command payloads. """
        self._logger.debug('Started executing commands.')
        while True:
            if self._command_queue.empty():
                # Finish when no more commands
                break
            if not self._stream_observer.payload:
                # if no feedback recieved yet
                await asyncio.sleep(0.1)
            if self._stream_observer.payload.capacity >= self._capacity_min:
                # get from txbuffer and send
                cmd: Command = self._command_queue.get(block=False)
                cmd.tag = self.__tag
                cmd.execute()
                self.__tag += 1
                self._logger.debug('Got new command from queue.')
                # We wait to give time to server to update capacity
                await asyncio.sleep(0.02)
            else:
                await asyncio.sleep(0.1)

        if wait_done:
            # simulate work using sleep
            await asyncio.sleep(5)