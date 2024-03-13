#!/usr/bin/env python3

""" 
An event loop which runs in a daemon thread.
It also handles exceptions raised all over the system.
"""

from concurrent.futures import CancelledError
import logging
import asyncio
import queue
import time
import typing
import websockets
import signal
from threading import Thread, Condition

from awtube import types

from . import errors


class ThreadLoop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._logger = logging.getLogger(self.__class__.__name__)
        self.daemon = True
        self.loop = None
        self._exception_queue = queue.Queue()
        self._cond = Condition()

    def start(self):
        with self._cond:
            Thread.start(self)
            self._cond.wait()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self._logger.debug("Created %s", self.loop)
        self.loop.call_soon_threadsafe(self._notify_start)
        asyncio.run_coroutine_threadsafe(
            self._handle_exceptions(), loop=self.loop)
        self.loop.run_forever()

    async def _handle_exceptions(self):
        def log_err(e): return self._logger.error('%s: %s', type(e), e)
        while True:
            if not self._exception_queue.empty():
                exc = self._exception_queue.get(block=False)
                if isinstance(exc, ConnectionRefusedError):
                    log_err(exc)
                    self.stop()
                elif isinstance(exc, KeyboardInterrupt):
                    log_err(exc)
                    self.stop()
                elif isinstance(exc, websockets.exceptions.WebSocketException):
                    log_err(exc)
                    self.stop()
                else:
                    log_err(exc)

            await asyncio.sleep(2)

    def register_exception(self, exc):
        self._exception_queue.put(exc)

    async def cancel_tasks(self):
        """ Cancel tasks and stop loop, must be called threadsafe """
        tasks = [
            task
            for task in asyncio.all_tasks()
            if task is not asyncio.current_task()
        ]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=False)

    def _notify_start(self):
        with self._cond:
            self._cond.notify_all()

    def stop(self):
        " Stop event loop and join thread. "
        asyncio.run_coroutine_threadsafe(self.cancel_tasks(), loop=self.loop)
        time.sleep(0.5)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()
        self.loop.close()
        self._logger.debug("Stopped.")

    def post(self, coro):
        """ Post asyncio coroutine into the threadloop. """
        if not self.loop or not self.loop.is_running() or not self.is_alive():
            raise errors.ThreadLoopNotRunningError()
        futur = asyncio.run_coroutine_threadsafe(coro, loop=self.loop)
        return futur

    def post_wait(self, coro, timeout=120) -> typing.Any:
        """ 
        Post asyncio coroutine into the threadloop, 
        and wait for it to return result until timeout. 
        """
        futur = self.post(coro)
        try:
            return futur.result(timeout)
        except Exception as e:
            self.register_exception(e)
            futur.cancel()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_t, exc_v, trace):
        self.stop()


# singleton
threadloop = ThreadLoop()
