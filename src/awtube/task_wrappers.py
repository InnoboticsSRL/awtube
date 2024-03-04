#!/usr/bin/env python3

""" 
Task wrappers, they wrap coroutines with tasks and control the how they are executed
using TWrapperResult, also they chain these running tasks with futures which can 
be used to await, check running or cancel these tasks.
"""

from abc import ABC, abstractmethod
import asyncio
from enum import IntEnum
from contextlib import suppress

from awtube.threadloop import threadloop


# TODO: test if the stoping functionality for these tasks is working as expected


class TWrapperResult(IntEnum):
    """ Result of a TWrapper iteration """
    NONE = 0
    RUNNING = 1
    FAILURE = 2
    SUCCESS = 3


class TWrapper(ABC):
    """ 
    Asyncio task wrapper interface.
    Controls how a coroutine is run,
    which constitutes the logic.
    """
    coro_callback = None
    args = None
    is_started = False
    _task = None
    _future = asyncio.Future(loop=threadloop.loop)

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


class OneTimeTask(TWrapper):
    """ Runs only once"""

    def __init__(self, coro_callback, args):
        self.coro_callback = coro_callback
        self.args = args
        self.is_started = False

    async def _run(self):
        return await self.coro_callback(self.args)


class PeriodicTask(TWrapper):
    """ Run periodically """

    def __init__(self, coro_callback, args, sleep_time):
        self.coro_callback = coro_callback
        self.args = args
        self.sleep_time = sleep_time
        self._future = asyncio.Future(loop=threadloop.loop)

    async def _run(self):
        res = TWrapperResult.RUNNING
        while res is not TWrapperResult.FAILURE:
            res = await self.coro_callback(self.args)
            await asyncio.sleep(self.sleep_time)
        return res


class PeriodicUntilDoneTask(PeriodicTask):
    """ Runs until result is success or failure"""

    def __init__(self, coro_callback, args, sleep_time):
        self._future = asyncio.Future(loop=threadloop.loop)
        super().__init__(coro_callback, args, sleep_time)

    async def _run(self):
        res = TWrapperResult.RUNNING
        while res is TWrapperResult.RUNNING or res is None:
            await asyncio.sleep(self.sleep_time)
            res = await self.coro_callback(self.args)
        return res
