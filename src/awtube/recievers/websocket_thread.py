#!/usr/bin/env python3

"""
    WebsocketThread client class which implements the CommandReceiver Interface.

    Can be used to create a asynchronous websocket client in a separate thread.
    The thread sends commands and updates the subscriber Observers asynchronously.
"""
import websockets
import asyncio
import queue
import logging
import threading
from typing import Dict

from awtube.recievers.command_receiver import CommandReceiver
from awtube.observers.observer import Observer

from awtube.logging import config

# disable websockets logging
# TODO: improve, don't just disable
logging.getLogger("websockets.client").propagate = False


class WebsocketThread(threading.Thread, CommandReceiver):
    """ 
        Client for communicating on websockets
    """

    def __init__(self, url: str, headers: Dict[str, str] = None, freq: int = 100, event_loop: asyncio.AbstractEventLoop = None):
        """
        Args:
            url: Websocket url to connect to.
            headers: Any additional headers to supply to the websocket.
        """
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        self.url = url
        self.headers = headers if headers else dict()

        # frequency of tasks
        self.__freq = freq
        self._rate = 1/self.__freq

        self.loop: asyncio.AbstractEventLoop = event_loop
        self.killed: bool = False
        self.outgoing = queue.Queue()
        # coroutines to be run asynchronously later they get the websocket as argument
        self._tasks = [self.listen_queue, self.listen_socket]
        self._observers = []

    def attach_observer(self, sub: Observer) -> None:
        """ Attach Observer. """
        if sub not in self._observers:
            self._observers.append(sub)

    def detach_observer(self, sub: Observer) -> None:
        """ Detach Observer. """
        self._observers.remove(sub)

    def notify(self, msg: str) -> None:
        """ Notify all attached observers. """
        if not self._observers:
            return
        # raise exceptions of observers here
        try:
            for sub in self._observers:
                sub.update(msg)
        except Exception as e:
            raise e

    async def listen(self):
        """ Listen to the websocket and local outgoing queue """
        try:
            async with websockets.connect(self.url, extra_headers=self.headers) as socket:
                # gather all tasks defined in self._tasks
                # await asyncio.gather(*(task(socket) for task in self._tasks), return_exceptions=True)
                await asyncio.gather(*(task(socket) for task in self._tasks))
        except ConnectionRefusedError:
            self._logger.error('Connection refused!')

    async def listen_socket(self, socket):
        """ Listen for messages on the socket, schedule tasks to handle """
        async for msg in socket:
            self.notify(msg)

    async def listen_queue(self, socket):
        """ Poll the outgoing queue for messages, send them to websocket """
        while True:
            if self.outgoing.empty():
                await asyncio.sleep(self._rate)
            else:
                try:
                    msg = self.outgoing.get(block=False)
                    asyncio.create_task(socket.send(msg))
                except queue.Empty:
                    continue

    def put(self, message: str) -> None:
        """ Put message in the receivers queue. """
        self.outgoing.put(message)
