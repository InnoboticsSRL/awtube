from __future__ import annotations
from abc import ABC, abstractmethod
import json
import time
from awtube.gbc_types import MachineStatus
from awtube.observers.observer import Observer
from awtube.cia402_machine import CIA402MachineState, device_state


class MachineObserver(Observer):
    """
    Observes the 'machine' field in the ws stream and keeps a MachineStatus object as payload
    """
    _current_state = None
    _state_changed = False

    def update(self, message: str) -> None:
        """
        Recieve message, update payload
        """
        try:
            js = json.loads(message)
            # TODO: stream array id ??????
            # get payload
            self._payload = MachineStatus(**js['status']['machine'])
            # check status word and update cia402 state
            self._current_state = device_state(self.payload.status_word)
            self._timestamp = time.time()
        except Exception as e:
            # self._logger.error(e)
            print(e)
