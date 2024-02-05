"""
    WebsocketThread client abstract class

    Can be used to create a asynchronous websocket client in a separate thread.
    Once implemented, the thread can handle received messages and allows
    for sending of messages from synchronous Python code.

    See the WebsocketThread docstring for an example implementation and use.
"""
import websockets
import asyncio
import queue
import logging
# import ssl
# import sys
import threading
from typing import Dict
from awtube.command_reciever import CommandReciever
from awtube.observers.observer import Observer

# disable websockets logging
logging.getLogger("websockets.client").addHandler(logging.NullHandler())
logging.getLogger("websockets.client").propagate = False


class WebsocketThread(threading.Thread, CommandReciever):
    """ Client for communicating on websockets

        To implement this class, override the handle_message method, which
        receives string messages from the websocket.
    """

    def __init__(self, url: str, headers: Dict[str, str] = None, freq: int = 100):
        """
        Args:
            url: Websocket url to connect to.
            headers: Any additional headers to supply to the websocket.
        """
        super().__init__()
        self.url = url
        self.headers = headers if headers else dict()

        # frequency of tasks
        self.__freq = freq
        self._rate = 1/self.__freq

        self.loop: asyncio.AbstractEventLoop = None
        self.killed: bool = False
        self.outgoing = queue.Queue()
        # coroutines to be run asynchronously later they get the websocket as argument
        self._tasks = [self.listen_queue, self.listen_socket]
        self._observers = []

    def attach_observer(self, sub: Observer) -> None:
        """ Attach observer. """
        if sub not in self._observers:
            self._observers.append(sub)

    def detach_observer(self, sub: Observer) -> None:
        """ Detach Observer. """
        self._observers.remove(sub)

    def notify(self, msg: str) -> None:
        """ Notify all attached observers. """
        if not self._observers:
            return
        for sub in self._observers:
            sub.update(msg)

    # @abstractmethod
    # async def handle_message(self, message: str):
    #     """ Override this method to handle messages from the websocket

    #     Args:
    #         message: String from the websocket.
    #     """
    #     raise NotImplementedError

    # def __enter__(self):
    #     """ Context manager for running the websocket """
    #     print("__enter__")
    #     self.start()
    #     return self

    # def __exit__(self, *_):
    #     """ Context manager for cleaning up event loop and thread """
    #     if not self.killed:
    #         self.kill()
    #     self.join()

    def kill(self):
        """ Cancel tasks and stop loop from sync, threadsafe """
        self.killed = True
        asyncio.run_coroutine_threadsafe(self.stop_loop(), self.loop)

    async def stop_loop(self):
        """ Cancel tasks and stop loop, must be called threadsafe """
        tasks = [
            task
            for task in asyncio.all_tasks()
            if task is not asyncio.current_task()
        ]
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        self.loop.stop()

    def run(self):
        """ Main execution of the thread. Is called when entering context """
        self.loop = asyncio.new_event_loop()
        # self.ignore_aiohttp_ssl_error()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.listen())
        self.loop.run_forever()

    async def listen(self):
        """ Listen to the websocket and local outgoing queue """
        try:
            async with websockets.connect(self.url, extra_headers=self.headers) as socket:
                # gather all tasks defined in self._tasks
                await asyncio.gather(*(task(socket) for task in self._tasks))
        except ConnectionRefusedError:
            # self.logger
            print('Connection refused!')

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
        """ Put message in the recievers queue. """
        self.outgoing.put(message)
        # print(message)

    # def ignore_aiohttp_ssl_error(self):
    #     """ Ignore aiohttp #3535 / cpython #13548 issue with SSL close. """
    #     if sys.version_info >= (3, 7, 4):
    #         return

    #     orig_handler = self.loop.get_exception_handler()

    #     def ignore_ssl_error(loop, context):
    #         if context.get("message") in {
    #             "SSL error in data received",
    #             "Fatal error on transport",
    #         }:
    #             exception = context.get('exception')
    #             protocol = context.get('protocol')
    #             if (
    #                 isinstance(exception, ssl.SSLError)
    #                 and exception.reason == 'KRB5_S_INIT'
    #                 and isinstance(protocol, asyncio.sslproto.SSLProtocol)
    #             ):
    #                 return
    #         if orig_handler is not None:
    #             orig_handler(loop, context)
    #         else:
    #             loop.default_exception_handler(context)

    #     self.loop.set_exception_handler(ignore_ssl_error)
