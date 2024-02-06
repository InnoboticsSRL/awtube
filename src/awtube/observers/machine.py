#!/usr/bin/env python3

""" Defines the machine observer which implements Observer Interface. """

import logging
import json
import time

from awtube.gbc_types import MachineStatus
from awtube.observers.observer import Observer
from awtube.cia402_machine import device_state

from awtube.logging import config


class MachineObserver(Observer):
    """
    Observes the 'machine' field in the ws stream and keeps a MachineStatus object as payload
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._current_state = None
        self._state_changed = False

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

        except KeyError as ke:
            # this means message doesn't contain status
            pass
        except Exception as e:
            self._logger.warn(e)
            # print(e)
