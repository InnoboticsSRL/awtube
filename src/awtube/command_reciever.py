from __future__ import annotations
from abc import ABC, abstractmethod


class CommandReciever(ABC):
    """
    The Receiver classes contain some important business logic. They know how to
    perform all kinds of operations, associated with carrying out a request. In
    fact, any class may serve as a Receiver.
    """
    @abstractmethod
    def put(self, message: str) -> None:
        """ Put new command in queue for execution.

        Args:
            message : json str

        Raises:
            NotImplementedError:
        """
        raise NotImplementedError
