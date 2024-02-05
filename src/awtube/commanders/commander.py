from __future__ import annotations
from abc import ABC, abstractmethod
from awtube.commands.command import Command


class Commander(ABC):
    """
    The Commander is associated with one or several commands. It sends a request
    to the command.
    """

    @abstractmethod
    def add_command(self, command: Command) -> None:
        """ Add commands to be sent """
        raise NotImplementedError

    @abstractmethod
    async def execute_commands(self) -> None:
        """ Execute all commands """
        raise NotImplementedError
