#!/usr/bin/env python3

""" Command Interface used to implement command pattern.  """

from __future__ import annotations
from abc import ABC, abstractmethod


class Command(ABC):
    """
    The Command interface declares a coroutine for executing a command.
    """
    tag = 0
    receiver = None

    @abstractmethod
    def execute(self) -> None:
        """ Execute command

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError
