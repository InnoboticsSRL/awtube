#!/usr/bin/env python3

""" MachineTarget command that implements Command Interface  """

from awtube.types.gbc import MachineTarget
from awtube.builders.command_builder import CommandBuilder
from awtube.commands.command import Command
from awtube.recievers.command_receiver import CommandReceiver
from awtube.errors.awtube import AwtubeError, AWTubeErrorException


class KinematicsConfigurationCommad(Command):
    """
        Machine target command, basically it is used to use either the real physical machine or the simulation.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 disable_limits: (bool, None) = None,
                 target_feed_rate: (float, int, None) = None,
                 kc_config: int = 0) -> None:
        self._disable_limits = disable_limits
        self._target_feed_rate = target_feed_rate
        self._receiver = receiver
        self._kc_config = kc_config
        self.builder = CommandBuilder()

    @property
    def disable_limits(self) -> bool:
        return self._disable_limits

    @disable_limits.setter
    def disable_limits(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise AWTubeErrorException(
                AwtubeError.BAD_ARGUMENT, 'Limits disabled flag should be a bool type.')
        self._disable_limits = value

    @property
    def target_feed_rate(self) -> bool:
        return self._target_feed_rate

    @target_feed_rate.setter
    def target_feed_rate(self, value: (float, int)) -> None:
        if not isinstance(value, (float, int)):
            raise AWTubeErrorException(
                AwtubeError.BAD_ARGUMENT, 'Feed rate should be a float or int type.')
        self._target_feed_rate = value

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = None
        if self._disable_limits:
            msg = self.builder.reset().disable_limits(self._disable_limits).build()
            self._receiver.put(msg)
            return
        elif self._target_feed_rate:
            msg = self.builder.reset().desired_feedrate(self._target_feed_rate).build()
            self._receiver.put(msg)
            return
