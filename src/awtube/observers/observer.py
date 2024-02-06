#!/usr/bin/env python3

""" Defines the Observer Interface used to implement the observer pattern. """

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

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
