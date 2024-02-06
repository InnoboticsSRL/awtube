#!/usr/bin/env python3

""" Defines the kinematics configuration observer which implements Observer Interface. """

import json
import time
import logging

from awtube.gbc_types import KinematicsConfigurationStatus
from awtube.observers.observer import Observer

from awtube.logging import config


class KinematicsConfigurationObserver(Observer):
    """
    The Observer interface declares the update coroutine, used by subjects.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    def update(self, message: str) -> None:
        """
        Recieve update from subject and decode message.

        Raises:
            NotImplementedError:
        """
        try:
            js = json.loads(message)
            # TODO: stream array id ??????
            self._payload = KinematicsConfigurationStatus(
                **js['status']['kc'][0])
            self._timestamp = time.time()
        except KeyError as ke:
            # this means message doesn't contain kc
            pass
        except Exception as e:
            self._logger.error(e)
