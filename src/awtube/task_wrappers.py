#!/usr/bin/env python3

""" Task wrappers. """

from abc import ABC
import logging
import asyncio
from enum import IntEnum
from threading import Thread
from asyncio import Condition
from typing import Optional
from contextlib import suppress


class TaskResult(IntEnum):
    """ Result of a Task for one iteration """
    RUNNING = 0
    FAILURE = 1
    SUCCESS = 2


class TaskWrapper(ABC):
    """ Asyncio task wrappers. """
    pass


class PeriodicTask(TaskWrapper):
    """ Task Wrapper for a coroutine that runs periodically"""

    def __init__(self, coro, args, sleep_time):
        self.coro = coro
        self.args = args
        self.sleep_time = sleep_time
        self.is_started = False
        self.task = asyncio.create_task(self._run())

    async def start(self):
        """ Start task to call coro """
        if not self.is_started:
            self.is_started = True
            # self.task = asyncio.create_task(self._run())

    async def stop(self):
        """ Stop task and await it stopped """
        if self.is_started:
            self.is_started = False
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task

    async def _run(self):
        #
        result = TaskResult.RUNNING
        while result is not TaskResult.FAILURE:
            if self.is_started:
                await asyncio.sleep(self.sleep_time)
                result = await self.coro(self.args)
            else:
                await asyncio.sleep(self.sleep_time)


class OneTimeTask(TaskWrapper):
    """ Task Wrapper for a coroutine that runs only once"""

    def __init__(self, coro, args):
        self.coro = coro
        self.args = args
        self.is_started = False
        self.task = None

    async def _run(self):
        await self.coro(self.args)


class PeriodicUntilDoneTask(PeriodicTask):
    """ Task Wrapper for a coroutine that runs periodically until results in success or failure"""

    def __init__(self, coro, args, sleep_time):
        super().__init__(coro, args, sleep_time)

    async def _run(self):
        result = TaskResult.RUNNING
        while result is TaskResult.RUNNING:
            if self.is_started:
                await asyncio.sleep(self.sleep_time)
                result = await self.coro(self.args)
            else:
                await asyncio.sleep(self.sleep_time)
