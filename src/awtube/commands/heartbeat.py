
#!/usr/bin/env python3

""" Heartbeat command that implements Command Interface  """

from awtube.commands.command import Command
from awtube.command_receiver import CommandReceiver
from awtube.msg_builders import get_machine_command_heartbeat


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
        self._payload = get_machine_command_heartbeat(self._heartbeat,
                                                      machine=self._machine)

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        self._receiver.put(self._payload)
