
#!/usr/bin/env python3

""" Heartbeat command that implements Command Interface  """

from awtube.commands.command import Command
from awtube.recievers.command_receiver import CommandReceiver
from awtube.messages.command_builder import CommandBuilder


class HeartbeatCommad(Command):
    """
        machine command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 heartbeat: int,
                 machine: int = 0) -> None:
        self._heartbeat = heartbeat
        self._machine = machine
        self._receiver = receiver
        self.builder = CommandBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().machine(
            self._machine).heartbeat(self._heartbeat).build()
        self._receiver.put(msg)
