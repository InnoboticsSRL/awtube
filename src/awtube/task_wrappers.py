#!/usr/bin/env python3

""" 
Task wrappers, they wrap coroutines with tasks and control the how they are executed
using TaskWrapperResult, also they chain these running tasks with futures which can 
be used to await, check running or cancel these tasks.
"""

from abc import ABC, abstractmethod
import asyncio
from enum import IntEnum
from contextlib import suppress

# TODO: test if the stoping functionality for these tasks is working as expected


class TaskWrapperResult(IntEnum):
    """ Result of a TaskWrapper iteration """
    NONE = 0
    RUNNING = 1
    FAILURE = 2
    SUCCESS = 3


class TaskWrapper(ABC):
    """ Asyncio task wrappers. """
    coro = None
    args = None
    is_started = False
    _task = None
    _future = asyncio.Future()

    def is_running(self):
        return not self._future.done()

    def __await__(self):
        return self._future.__await__()

    async def start(self):
        """ Start task to call coro """
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.create_task(self._main())

    async def stop(self):
        """ Stop task and await it stopped """
        if self.is_started:
            self.is_started = False
            self._task.cancel()
            self._future.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
                await self._future

    async def _main(self):
        result = await self._run()
        self._future.set_result(result)

    @abstractmethod
    async def _run(self):
        pass


class OneTimeTask(TaskWrapper):
    """ Task Wrapper for a coroutine that runs only once"""

    def __init__(self, coro, args):
        self.coro = coro
        self.args = args
        self.is_started = False

    async def _run(self):
        return await self.coro(self.args)


class PeriodicTask(TaskWrapper):
    """ Task Wrapper for a coroutine that runs periodically"""

    def __init__(self, coro, args, sleep_time):
        self.coro = coro
        self.args = args
        self.sleep_time = sleep_time
        self._future = asyncio.Future()

    async def _run(self):
        res = TaskWrapperResult.RUNNING
        while res is not TaskWrapperResult.FAILURE:
            res = await self.coro(self.args)
            await asyncio.sleep(self.sleep_time)
        return res


class PeriodicUntilDoneTask(PeriodicTask):
    """ Wrapps task that run periodically until results is success or failure"""

    def __init__(self, coro, args, sleep_time):
        self._future = asyncio.Future()
        super().__init__(coro, args, sleep_time)

    async def _run(self):
        res = TaskWrapperResult.RUNNING
        while res is TaskWrapperResult.RUNNING or res is None:
            res = await self.coro(self.args)
            await asyncio.sleep(self.sleep_time)
        return res
