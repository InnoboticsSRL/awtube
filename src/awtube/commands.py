#!/usr/bin/env python3

""" Commands of command pattern.  """

from __future__ import annotations
from abc import ABC, abstractmethod
import typing as tp

from . import command_receiver,  cia402,  types,  builders, errors

# builder
stream_activity_builder = builders.StreamActivityBuilder()
stream_command_builder = builders.StreamCommandBuilder()

# TODO: there's confusion between command and stream which also is a command


class Command(ABC):
    """ The Command interface. """
    tag = 0
    receiver = None

    @abstractmethod
    def execute(self):
        """ Put command payload in receiver queue. """
        raise NotImplementedError


class HeartbeatCommad(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 frequency: int = 1,
                 machine: int = 0):
        self._machine = machine
        self._receiver = receiver
        self._frequency = frequency

    def execute(self):
        msg = stream_command_builder.reset().machine(
            self._machine).heartbeat(self._heartbeat).build()
        self._receiver.put(msg)


class IoutCommad(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 position: int,
                 value: int = 1,
                 override: bool = True,
                 machine: int = 0):
        self._machine = machine
        self._receiver = receiver
        self._position = position
        self._value = value
        self._override = override

    def execute(self):
        msg = stream_command_builder.reset().iout(self._position,
                                                  self._value,
                                                  override=self._override).build()
        self._receiver.put(msg)


class DoutCommad(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 position: int,
                 value: int = 1,
                 override: bool = True,
                 machine: int = 0):
        self._machine = machine
        self._receiver = receiver
        self._position = position
        self._value = value
        self._override = override

    def execute(self):
        msg = stream_command_builder.reset().dout(self._position,
                                                  self._value,
                                                  override=self._override).build()
        self._receiver.put(msg)


class SerialCommad(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 data: str,
                 position: int = 0,
                 machine: int = 0):
        self._machine = machine
        self._receiver = receiver
        self._data = data
        self._position = position

    def execute(self):
        data_l = self._data.replace(' ', '')
        data_l = [int(data_l[i:i+2], 16) for i in range(0, len(data_l), 2)]
        msg = stream_command_builder.reset().serial(self._position,
                                                    data_l,
                                                    control_word=1).build()
        self._receiver.put(msg)


class AoutCommad(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 position: int,
                 value: int = 1,
                 override: bool = True,
                 machine: int = 0):
        self._machine = machine
        self._receiver = receiver
        self._position = position
        self._value = value
        self._override = override

    def execute(self):
        msg = stream_command_builder.reset().aout(self._position,
                                                  self._value,
                                                  override=self._override).build()
        self._receiver.put(msg)


class KinematicsConfigurationCommad(Command):
    def __init__(self,
                 receiver: command_receiver.WebsocketThread,
                 safe_limits: bool = None,
                 target_feed_rate=None,
                 kc_config: int = 0):
        self._safe_limits = safe_limits
        self._target_feed_rate = target_feed_rate
        self._receiver = receiver
        self._kc_config = kc_config

    @property
    def safe_limits(self) -> bool:
        return self._safe_limits

    @safe_limits.setter
    def safe_limits(self, value: bool):
        if not isinstance(value, bool):
            raise errors.AWTubeErrorException(
                errors.AwtubeError.BAD_ARGUMENT, 'Limits disabled flag should be a bool type.')
        self._safe_limits = value

    @property
    def target_feed_rate(self) -> bool:
        return self._target_feed_rate

    @target_feed_rate.setter
    def target_feed_rate(self, value: (float, int)):
        if not isinstance(value, (float, int)):
            raise errors.AWTubeErrorException(
                errors.AwtubeError.BAD_ARGUMENT, 'Feed rate should be a float or int type.')
        self._target_feed_rate = value

    def execute(self):
        msg = None

        if self._target_feed_rate:
            msg = stream_command_builder.reset().desired_feedrate(
                self._target_feed_rate).build()
            self._receiver.put(msg)
            return
        else:
            msg = stream_command_builder.reset().safe_limits(self._safe_limits).build()
            self._receiver.put(msg)
            return


class MachineStateCommad(Command):
    def __init__(self,
                 receiver: command_receiver.AWTubeErrorException,
                 desired_state: cia402.DesiredState,
                 machine: int = 0):
        self._desired_state = desired_state
        self._control_word = 0
        self._machine = machine
        self._receiver = receiver

    @property
    def desired_state(self) -> cia402.CIA402MachineState:
        return self._desired_state

    @property
    def control_word(self) -> cia402.CIA402MachineState:
        return self._control_word

    @control_word.setter
    def control_word(self, cw: int):
        self._control_word = cw

    @property
    def receiver(self) -> cia402.CIA402MachineState:
        return self._receiver

    @receiver.setter
    def receiver(self, cw: int):
        self._receiver = cw

    @property
    def machine(self) -> cia402.CIA402MachineState:
        return self.machine

    def execute(self):
        msg = stream_command_builder.reset().machine(self._machine).control_word(
            self._control_word).build()
        self._receiver.put(msg)


class MachineTargetCommad(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 target: types.MachineTarget,
                 machine: int = 0):
        self._receiver = receiver
        self._machine = machine
        self._target = target

    @property
    def target(self) -> types.MachineTarget:
        return self._target

    @target.setter
    def target(self, value: int):
        self._target = value

    def execute(self):
        msg = stream_command_builder.reset().machine(
            self._machine).machine_target(self._target).build()
        self._receiver.put(msg)


class MoveJointsInterpolatedCommand(Command):
    def __init__(self,
                 receiver: command_receiver.AWTubeErrorException,
                 joint_positions: tp.List[float],
                 joint_velocities: tp.List[float],
                 tag: int = 0,
                 kc: int = 0):
        self.joints = types.JointStates(positions=joint_positions,
                                        velocities=joint_velocities)
        self._receiver = receiver
        self.tag = tag
        self.kc = kc

    def execute(self):
        msg = stream_activity_builder.reset().move_joints_interpolated(joint_position_array=self.joints.positions,
                                                                       joint_velocity_array=self.joints.velocities,
                                                                       tag=self.tag,
                                                                       kc=self.kc,
                                                                       move_params={}
                                                                       ).build()
        self._receiver.put(msg)


class MoveJointsCommand(Command):
    def __init__(self,
                 receiver: command_receiver.AWTubeErrorException,
                 joint_positions: tp.List[float],
                 tag: int = 0,
                 kc: int = 0):
        self.joints = joint_positions
        self._receiver = receiver
        self.tag = tag
        self.kc = kc

    def execute(self):
        msg = stream_activity_builder.reset().move_joints(joint_position_array=self.joints,
                                                          tag=self.tag,
                                                          kc=self.kc,
                                                          move_params={}
                                                          ).build()
        self._receiver.put(msg)


class MoveLineCommand(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 translation: tp.Dict[str, float],
                 rotation: tp.Dict[str, float],
                 tag: int = 0,
                 kc: int = 0):
        self.pose = types.Pose(position=types.Position(**translation),
                               orientation=types.Quaternion(**rotation))
        self._translation = translation
        self._rotation = rotation
        self._receiver = receiver
        self.tag = tag
        self.kc = kc

    def execute(self):
        msg = stream_activity_builder.reset().move_line(translation=self._translation,
                                                        rotation=self._rotation,
                                                        tag=self.tag,
                                                        kc=self.kc,
                                                        move_params={}
                                                        ).build()
        self._receiver.put(msg)


class MoveToPositionCommand(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 translation: dict,
                 rotation: dict,
                 tag: int = 0,
                 kc: int = 0,
                 position_reference: types.PositionReference = types.PositionReference.ABSOLUTE):
        self._receiver = receiver
        self._translation = translation
        self._rotation=rotation
        self.tag = tag
        self.kc = kc
        self.position_reference = position_reference

    def execute(self):
        msg = stream_activity_builder.reset().move_to_position(translation=self._translation,
                                                               rotation=self._rotation,
                                                               tag=self.tag,
                                                               kc=self.kc,
                                                               move_params={},
                                                               position_reference=self.position_reference).build()
        self._receiver.put(msg)


class StreamCommand(Command):
    def __init__(self,
                 receiver: command_receiver.CommandReceiver,
                 command: types.StreamCommandType):
        self._cmd = command
        self._receiver = receiver

    @property
    def command_type(self) -> types.StreamCommandType:
        return self._cmd

    @command_type.setter
    def command_type(self, value: types.StreamCommandType):
        self._cmd = value

    def execute(self):
        msg = stream_command_builder.reset().stream_command(self._cmd).build()
        self._receiver.put(msg)
