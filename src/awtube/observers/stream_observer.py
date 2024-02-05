from __future__ import annotations
from abc import ABC, abstractmethod
import json
import time
from awtube.gbc_types import StreamStatus
from awtube.observers.observer import Observer


class StreamObserver(Observer):
    """
    Observes the 'stream' field  in the ws stream and keeps a StreamStatus object as payload
    """

    def update(self, message: str) -> None:
        """
        Recieve message, update payload
        """
        try:
            js = json.loads(message)
            # TODO: stream array id ??????
            self._payload = StreamStatus(**js['stream'][0])
            self._timestamp = time.time()

        except Exception as e:
            # self._logger.error(e)
            print(e)
