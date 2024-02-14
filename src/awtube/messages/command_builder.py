#!/usr/bin/env python3

""" Defines the StreamBuilder implementation of the Builder interface. """

from __future__ import annotations

from awtube.messages.builder import Builder

from awtube.types.gbc import MachineTarget
from awtube.types.aw import Pose, Position


class CommandBuilder(Builder):
    """
    Builder for Stream Activity
    """
    # protected auto non-serialized
    _kc: int = 0
    _machine: int = 0
    _machine_target: int = int(MachineTarget.SIMULATION)
    _fro: float = 1.0

    command: dict = None

    def machine(self, val: int) -> CommandBuilder:
        self._machine = val
        return self

    def reset(self) -> CommandBuilder:
        """ Reset all fields of model to default values. """
        self.command = None
        self._kc = 0
        self._machine = 0
        self._machine_target: int = int(MachineTarget.SIMULATION)
        self._fro: float = 1.0
        return self

    def build(self) -> str:
        """ Return Stream model serialized in json. """
        return self.model_dump_json(
            warnings=self._build_warnings
        )

    def kinematics_configuration(self, value: int) -> CommandBuilder:
        """ Set kinematics configuration id for message. """
        self._kc = value
        return self

    def disable_limits(self, value: bool = False) -> CommandBuilder:
        """ Add kinematics configuration command with disableLimits flag. """
        self.command = {
            "kinematicsConfiguration": {
                f"{self._kc}": {
                    "command": {
                        "disableLimits": value
                    }
                }}}
        return self

    def heartbeat(self, value: int) -> CommandBuilder:
        """ Add heartbeat command. """
        self.command = {
            "machine": {
                f"{self._machine}": {
                    "command": {
                        "heartbeat": value
                    }
                }}}
        return self

    def desired_feedrate(self, value: float) -> CommandBuilder:
        """ Add feedrate command. """
        self.command = {
            "kinematicsConfiguration": {
                f"{self._kc}": {
                    "command": {
                        "fro": value
                    }
                }}}
        return self

    def machine_target(self, value: int) -> CommandBuilder:
        """ Add machine target command. """
        self.command = {
            "kinematicsConfiguration": {
                f"{self._machine}": {
                    "command": {
                        "target": int(value)
                    }
                }}}
        return self

    def control_word(self, value: int) -> CommandBuilder:
        """ Add control word command. """
        self.command = {
            "machine": {
                f"{self._machine}": {
                    "command": {
                        "controlWord": int(value)
                    }
                }}}
        return self
