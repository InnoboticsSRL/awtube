#!/usr/bin/env python3

""" Defines the telemetry observer which implements Observer Interface. """

from __future__ import annotations
from collections import deque
import json
import time
import logging
import asyncio

from awtube.types.gbc import StreamStatus
from awtube.observers.observer import Observer
from awtube.types.aw import JointStates
from awtube.logging import config


class TelemetryObserver(Observer):
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
            self._payload = {
                'set': JointStates(
                    positions=[joint_i['p']
                               for joint_i in js['telemetry'][-1]['set']],
                    velocities=[joint_i['v']
                                for joint_i in js['telemetry'][-1]['set']],
                    accelerations=[joint_i['a']
                                   for joint_i in js['telemetry'][-1]['set']],
                    torques=[joint_i['t'] for joint_i in js['telemetry'][-1]['set']]),
                'actual': JointStates(
                    positions=[joint_i['p']
                               for joint_i in js['telemetry'][-1]['act']],
                    velocities=[joint_i['v']
                                for joint_i in js['telemetry'][-1]['act']],
                    accelerations=[joint_i['a']
                                   for joint_i in js['telemetry'][-1]['act']],
                    torques=[joint_i['t'] for joint_i in js['telemetry'][-1]['act']])
            }

            # record timestamp
            self._timestamp = time.time()

        except KeyError as ke:
            # this means message doesn't contain telemetry
            pass
        except Exception:
            self._logger.warn('No telemetry available.')
            # self._logger.error(e)
            # print(e)
            # print('Not recieving any telemetry!')
