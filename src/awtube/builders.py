#!/usr/bin/env python3

""" JSON message builders. """

from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel

from awtube.types import ActivityType, PositionReference, Pose, MachineTarget, StreamCommandType


class Builder(ABC, BaseModel):
    """
    The Builder interface specifies methods for creating the different parts of
    the Message objects, which also is a pydantic BaseModel.
    """

    _build_warnings = False

    @property
    def build_warnings(self) -> bool:
        """ Flag to activate warnings during build of json. """
        return self._build_warnings

    @build_warnings.setter
    def build_warnings(self, val: bool):
        """ Flag to activate warnings during build of json. """
        self._build_warnings = val

    @abstractmethod
    def build(self):
        raise NotImplementedError


class StreamCommandBuilder(Builder):
    """
    Builder for Stream Activity
    """
    # protected auto non-serialized
    _kc: int = 0
    _machine: int = 0
    _machine_target: int = int(MachineTarget.SIMULATION)
    _fro: float = 1.0

    command: dict = None

    def machine(self, val: int) -> StreamCommandBuilder:
        self._machine = val
        return self

    def reset(self) -> StreamCommandBuilder:
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

    def kinematics_configuration(self, value: int) -> StreamCommandBuilder:
        self._kc = value
        return self

    def safe_limits(self, value: bool = False) -> StreamCommandBuilder:
        self.command = {
            "kinematicsConfiguration": {
                f"{self._kc}": {
                    "command": {
                        "disableLimits": not value
                    }
                }}}
        return self

    def heartbeat(self, value: int) -> StreamCommandBuilder:
        self.command = {
            "machine": {
                f"{self._machine}": {
                    "command": {
                        "heartbeat": value
                    }
                }}}
        return self

    def desired_feedrate(self, value: float) -> StreamCommandBuilder:
        self.command = {
            "kinematicsConfiguration": {
                f"{self._kc}": {
                    "command": {
                        "fro": value
                    }
                }}}
        return self

    def stream_command(self, value: StreamCommandType) -> StreamCommandBuilder:
        self.command = {"stream": {
            "0": {
                "command": {
                    "streamCommand": int(value)}}}}
        return self

    def iout(self, position: int, value: int, override: bool = True) -> StreamCommandBuilder:
        self.command = {
            "iout": {
                f"{position}": {
                    "command": {
                        "setValue": value,
                        "override": override
                    }
                }}}
        return self

    def dout(self, position: int, value: int, override: bool = True) -> StreamCommandBuilder:
        self.command = {
            "dout": {
                f"{position}": {
                    "command": {
                        "setValue": value,
                        "override": override
                    }
                }}}
        return self

    def aout(self, position: int, value: int, override: bool = True) -> StreamCommandBuilder:
        self.command = {
            "aout": {
                f"{position}": {
                    "command": {
                        "setValue": value,
                        "override": override
                    }
                }}}
        return self

    def machine_target(self, value: int) -> StreamCommandBuilder:
        self.command = {
            "machine": {
                f"{self._machine}": {
                    "command": {
                        "target": int(value)
                    }
                }}}
        return self

    def control_word(self, value: int) -> StreamCommandBuilder:
        self.command = {
            "machine": {
                f"{self._machine}": {
                    "command": {
                        "controlWord": int(value)
                    }
                }}}
        return self


# TODO: study and implement move_params features
# class MoveParametersConfig(BaseModel):
#     """ Configuration parameters for move parameters. """
#     amax_percentage: float = Field(None, alias='amaxPercentage')
#     blend_time_percentage: float = Field(None, alias='blendTimePercentage')
#     blend_tolerance: float = Field(None, alias='blendTolerance')
#     blend_type: BlendType = Field(None, alias='blendType')
#     jmax_percentage: float = Field(None, alias='jmaxPercentage')
#     # Linear and angular limit profile to use for mov
#     limit_configuration_index: float = Field(
#         None, alias='limitConfigurationIndex')
#     name: str = Field(None)
#     sync_type: SyncType = Field(None, alias='syncType')
#     sync_value: float = Field(None, alias='syncValue')
#     tool_index: int = Field(None, alias='toolIndex')
#     vmax: float = Field(None)
#     vmax_percentage: float = Field(None, alias='vmaxPercentage')


class StreamActivityBuilder(Builder):
    """
    Builder for Stream Activity
    """
    # protected auto non-serialized
    _stream_index: int = 0
    _items: list = []
    _enable_end_program: bool = False

    stream: dict = None

    @property
    def items(self) -> list:
        return self._items

    @items.setter
    def items(self, val):
        self._items = val

    def reset(self) -> StreamActivityBuilder:
        """ Reset all fields of model to default values. """
        self._items = []
        self._stream_index = 0
        self._enable_end_program = False
        return self

    def build(self) -> str:
        """ Return Stream model serialized in json. """
        self.stream = {
            "streamIndex": self._stream_index,
            "items": self._items,
            "name": "default",
            "enableEndProgram": False
        }
        return self.model_dump_json(
            warnings=self._build_warnings
        )

    def enable_end_program(self, enable: bool) -> StreamActivityBuilder:
        """ Set enableEndProgram flag. """
        self._enable_end_program = enable
        return self

    def stream_index(self, val: int) -> StreamActivityBuilder:
        """ Set streamIndex flag. """
        self._stream_index = val
        return self

    def move_joints(self,
                    joint_position_array: list,
                    tag: int,
                    kc: int,
                    move_params: dict) -> StreamActivityBuilder:
        """ Add a move joints item to the stream activity. """
        self._items.append({
            "activityType": int(ActivityType.MOVEJOINTS),
            "tag": tag,
            "moveJoints": {
                "moveParams": move_params,
                "kinematicsConfigurationIndex": kc,
                "jointPositionArray": joint_position_array}
        })
        return self

    def move_joints_at_velocity(self,
                                joint_velocity_array: list,
                                tag: int,
                                kc: int,
                                move_params: dict) -> StreamActivityBuilder:
        """ Add a move joints at velocity item to the stream activity. """
        self._items.append({
            "activityType": int(ActivityType.MOVEJOINTSATVELOCITY),
            "tag": tag,
            "moveJoints": {
                "moveParams": move_params,
                "kinematicsConfigurationIndex": kc,
                "jointVelocityArray": joint_velocity_array}
        })
        return self

    def move_joints_interpolated(self,
                                 joint_position_array: list,
                                 joint_velocity_array: list,
                                 tag: int,
                                 kc: int,
                                 move_params: dict) -> StreamActivityBuilder:
        """ Add a moveJointsInterpolated item to the stream activity. """
        self._items.append({
            "activityType": int(ActivityType.MOVEJOINTSINTERPOLATED),
            "tag": tag,
            "moveJointsInterpolated": {
                "moveParams": move_params,
                "kinematicsConfigurationIndex": kc,
                "duration": 0.1,
                "jointPositionArray": list(joint_position_array),
                "jointVelocityArray": list(joint_velocity_array)}
        })
        return self

    def move_line(self,
                  pose: Pose,
                  tag: int,
                  kc: int,
                  move_params: dict) -> StreamActivityBuilder:
        """ Add a moveLine item to the stream activity. """
        self._items.append({
            "activityType": int(ActivityType.MOVELINE),
            "tag": tag,
            "moveLine": {
                "moveParams": move_params,
                "kinematicsConfigurationIndex": kc,
                "line": {
                    "translation": {
                        "x": pose.position.x,
                        "y": pose.position.y,
                        "z": pose.position.z
                    },
                    "rotation": {
                        "x": pose.orientation.x,
                        "y": pose.orientation.y,
                        "z": pose.orientation.z,
                        "w": pose.orientation.w
                    }
                }}})
        return self

    def move_to_position(self,
                         pose: Pose,
                         tag: int,
                         kc: int,
                         move_params: dict,
                         position_reference: PositionReference) -> StreamActivityBuilder:
        """ Add a moveLine item to the stream activity. """
        self._items.append({
            "activityType": int(ActivityType.MOVETOPOSITION),
            "tag": tag,
            "moveToPosition": {
                "moveParams": move_params,
                "kinematicsConfigurationIndex": kc,
                "cartesianPosition": {
                    "position": {
                        "translation": {
                            "x": pose.position.x,
                            "y": pose.position.y,
                            "z": pose.position.z
                        },
                        "rotation": {
                            "x": pose.orientation.x,
                            "y": pose.orientation.y,
                            "z": pose.orientation.z,
                            "w": pose.orientation.w
                        },
                        "frameIndex": {
                            "x": pose.orientation.x,
                            "y": pose.orientation.y,
                            "z": pose.orientation.z,
                            "w": pose.orientation.w
                        },
                        "positionReference": int(position_reference)},
                    "configuration": 0
                }}})
        return self


# TODO:
class ActivityBuilder(Builder):
    """
    Builder for Stream Activity
    """
    # protected auto non-serialized

# def solo_activity_move_joints_cmd(
#         joints: JointStates,
#         stream_index: int = 0,
#         tag: int = 0,
#         kinematics_configuration_index: int = 0,
#         debug: bool = False) -> str:
#     """ Create activityMoveJoints json command """
#     return json.dumps({
#         "command": {
#             "soloActivity": {
#                 "0": {
#                     "command": {
#                         "tag": tag,
#                         "activityType": 3,
#                         "moveJoints": {
#                             "jointPositionArray": list(joints.positions)
#                         }
#                     }
#                 }
#             }
#         }
#     })


# def get_stream_pause_program(stream_index: int = 0, debug: bool = False) -> str:
#     s = Stream(stream=StreamConfig(
#         streamIndex=stream_index,
#         enable_end_program=False,
#         items=[
#             PauseProgramStreamItem()
#         ]
#     )
#     ).model_dump_json(by_alias=True)
#     # TODO: log
#     if debug:
#         print(s)
#     return s
