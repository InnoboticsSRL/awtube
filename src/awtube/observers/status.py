#!/usr/bin/env python3

""" Defines the status observer which implements Observer Interface. """

import logging
import json
import time

from awtube.types.gbc import Status
from awtube.observers.observer import Observer
from awtube.errors.gbc import OperationError

from awtube.logging import config


class StatusObserver(Observer):
    """
    Observes the 'status' field  in the ws stream and keeps a Status object as payload
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    def update(self, message: str) -> None:
        """
        Recieve message, update payload
        """
        try:
            # update payload
            js = json.loads(message)
            self._payload = Status(**js['status'])
            self._timestamp = time.time()

            # check reported errors and log
            if self._payload.machine.operation_error != OperationError.NONE:
                self._logger.error(self._payload.machine.operation_error)
        except KeyError as ke:
            # this means message doesn't contain status
            pass
        except Exception as e:
            self._logger.error(e)
