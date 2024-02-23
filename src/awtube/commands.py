#!/usr/bin/env python3

""" Commands of command pattern.  """

from __future__ import annotations
from abc import ABC, abstractmethod
import typing as tp

from awtube.types import PositionReference, Pose, Position, Quaternion, MachineTarget
from awtube.builders import StreamBuilder, CommandBuilder
from awtube.types import JointStates
from awtube.cia402 import CIA402MachineState
from awtube.errors import AwtubeError, AWTubeErrorException
from awtube.command_receiver import CommandReceiver


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


class HeartbeatCommad(Command):
    """
        Heartbeat command that implements Command Interface  
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


class MachineStateCommad(Command):
    """
        machine command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 desired_state: CIA402MachineState,
                 machine: int = 0) -> None:
        self._desired_state = desired_state
        self._control_word = 0
        self._machine = machine
        self._receiver = receiver
        self.builder = CommandBuilder()

    @property
    def desired_state(self) -> CIA402MachineState:
        return self._desired_state

    @property
    def control_word(self) -> CIA402MachineState:
        return self._control_word

    @control_word.setter
    def control_word(self, cw: int) -> None:
        self._control_word = cw

    @property
    def receiver(self) -> CIA402MachineState:
        return self._receiver

    @receiver.setter
    def receiver(self, cw: int) -> None:
        self._receiver = cw

    @property
    def machine(self) -> CIA402MachineState:
        return self.machine

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().machine(self._machine).control_word(
            self._control_word).build()
        self._receiver.put(msg)


class MachineTargetCommad(Command):
    """
        Machine target command, basically it is used to use either the real physical machine or the simulation.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 target: MachineTarget,
                 machine: int = 0) -> None:
        self._receiver = receiver
        self._machine = machine
        self._target = target
        self.builder = CommandBuilder()

    @property
    def target(self) -> MachineTarget:
        """ Return target as MachineTarget. """
        return self._target

    @target.setter
    def target(self, cw: int) -> None:
        self._target = cw

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().machine(
            self._machine).machine_target(self._target).build()
        self._receiver.put(msg)


# from awtube.msg_builders import stream_move_joints_interpolated_cmd


class MoveJointsInterpolatedCommand(Command):
    """
        moveJointsInterpolated command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 joint_positions: tp.List[float],
                 joint_velocities: tp.List[float],
                 tag: int = 0,
                 kc: int = 0) -> None:
        self.joints = JointStates(positions=joint_positions,
                                  velocities=joint_velocities)
        self._receiver = receiver
        self.tag = tag
        self.kc = kc
        self.builder = StreamBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().move_joints_interpolated(joint_position_array=self.joints.positions,
                                                            joint_velocity_array=self.joints.velocities,
                                                            tag=self.tag,
                                                            kc=self.kc,
                                                            move_params={}
                                                            ).build()
        self._receiver.put(msg)


class MoveJointsCommand(Command):
    """
        moveJoints command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 joint_positions: tp.List[float],
                 tag: int = 0,
                 kc: int = 0) -> None:
        self.joints = joint_positions
        self._receiver = receiver
        self.tag = tag
        self.kc = kc
        self.builder = StreamBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().move_joints(joint_position_array=self.joints,
                                               tag=self.tag,
                                               kc=self.kc,
                                               move_params={}
                                               ).build()
        self._receiver.put(msg)


class MoveLineCommand(Command):
    """
        moveLine command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 translation: tp.Dict[str, float],
                 rotation: tp.Dict[str, float],
                 tag: int = 0,
                 kc: int = 0) -> None:
        self.pose = Pose(position=Position(**translation),
                         orientation=Quaternion(**rotation))
        self._receiver = receiver
        self.tag = tag
        self.kc = kc
        self.builder = StreamBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().move_line(pose=self.pose,
                                             tag=self.tag,
                                             kc=self.kc,
                                             move_params={}
                                             ).build()
        self._receiver.put(msg)


class MoveToPositionCommand(Command):
    """
        moveToPosition command.
    """

    def __init__(self,
                 receiver: CommandReceiver,
                 pose: Pose,
                 tag: int = 0,
                 kc: int = 0,
                 position_reference: PositionReference = PositionReference.ABSOLUTE) -> None:
        self._receiver = receiver
        self.tag = tag
        self.pose = pose
        self.kc = kc
        self.position_reference = position_reference
        self.builder = StreamBuilder()

    def execute(self) -> None:
        """ Put command payload in receiver queue. """
        msg = self.builder.reset().move_to_position(pose=self.pose,
                                                    tag=self.tag,
                                                    kc=self.kc,
                                                    move_params={},
                                                    position_reference=self.position_reference).build()
        self._receiver.put(msg)
