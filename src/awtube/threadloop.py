#!/usr/bin/env python3

""" A loop which runs on its own thread """

import logging
import asyncio
from threading import Thread, Condition

from awtube.errors import ThreadLoopNotRunningError


class _ThreadLoop(Thread):
    def __init__(self) -> None:
        Thread.__init__(self)
        self.daemon = True
        self._logger = logging.getLogger(self.__class__.__name__)
        self.loop = None
        self._cond = Condition()

    def start(self):
        with self._cond:
            Thread.start(self)
            self._cond.wait()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self._logger.debug("Threadloop: %s", self.loop)
        self.loop.call_soon_threadsafe(self._notify_start)
        self.loop.run_forever()

    def _notify_start(self):
        with self._cond:
            self._cond.notify_all()

    def stop(self):
        " Stop event loop and join thread. "
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()
        self.loop.close()

    def post(self, coro):
        """ Post asyncio coroutine into the threadloop. """
        if not self.loop or not self.loop.is_running() or not self.is_alive():
            raise ThreadLoopNotRunningError(
                f"could not post {coro} since asyncio loop in thread has not been started or has been stopped")
        futur = asyncio.run_coroutine_threadsafe(coro, loop=self.loop)
        return futur

    def post_wait(self, coro, timeout=120):
        """ Post asyncio coroutine into the threadloop, and wait for it to return result until timeout. """
        futur = self.post(coro)
        return futur.result(timeout)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_t, exc_v, trace):
        self.stop()


# singleton
threadloop = _ThreadLoop()
