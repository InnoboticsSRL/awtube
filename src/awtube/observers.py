#!/usr/bin/env python3

""" Defines the Observer Interface used to implement the observer pattern. """

from __future__ import annotations
import time
import json
from abc import ABC, abstractmethod
from typing import Any
import logging

from awtube.types import JointStates, StreamStatus, Status
import awtube.errors as errors

import awtube.logging_config


class Observer(ABC):
    """
    The Observer interface declares the update coroutine, used by subjects.
    These types of object are used as wrappers of objects that would get 
    updated frequently, thus they hold a timestamp also.
    """
    _payload = None
    _timestamp = None

    @property
    def payload(self) -> Any:
        """ Return last payload stored. """
        return self._payload

    @property
    def timestamp(self) -> Any:
        """ Return timestamp of when payload was last updated. """
        return self._timestamp

    @abstractmethod
    def update(self, message: object) -> None:
        """
        Receive update from subject.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError


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
            # if self._payload.machine.operation_error != errors.OperationError.NONE:
            #     self._logger.error(self._payload.machine.operation_error)

        except KeyError as ke:
            # this means message doesn't contain status
            pass
        except Exception as e:
            self._logger.error(e)


class StreamObserver(Observer):
    """
    Observes the 'stream' field  in the ws stream and keeps a StreamStatus object as payload
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    def update(self, message: str) -> None:
        """
        Recieve message, update payload
        """
        try:
            js = json.loads(message)
            # TODO: stream array id ??????
            self._payload = StreamStatus(**js['stream'][0])
            self._timestamp = time.time()
        except KeyError as ke:
            # this means message doesn't contain stream
            pass
            # self._logger.error(ke)
        except Exception as e:
            self._logger.error(e)


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
            if js['telemetry']:
                self._payload = {
                    'set': JointStates(
                        positions=[joint_i['p']
                                   for joint_i in js['telemetry'][-1]['set']],
                        velocities=[joint_i['v']
                                    for joint_i in js['telemetry'][-1]['set']],
                        # accelerations=[joint_i['a']
                        #                for joint_i in js['telemetry'][-1]['set']],
                        torques=[joint_i['t'] for joint_i in js['telemetry'][-1]['set']]),
                    'actual': JointStates(
                        positions=[joint_i['p']
                                   for joint_i in js['telemetry'][-1]['act']],
                        velocities=[joint_i['v']
                                    for joint_i in js['telemetry'][-1]['act']],
                        # accelerations=[joint_i['a']
                        #                for joint_i in js['telemetry'][-1]['act']],
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
