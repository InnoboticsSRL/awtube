#!/usr/bin/env python3

""" Defines the StreamBuilder implementation of the Builder interface. """

from __future__ import annotations

from awtube.messages.builder import Builder

from awtube.types.gbc import ActivityType, PositionReference
from awtube.types.aw import Pose, Position


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


class StreamBuilder(Builder):
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
    def items(self, val) -> None:
        self._items = val

    def reset(self) -> StreamBuilder:
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

    def enable_end_program(self, enable: bool) -> StreamBuilder:
        """ Set enableEndProgram flag. """
        self._enable_end_program = enable
        return self

    def stream_index(self, val: int) -> StreamBuilder:
        """ Set streamIndex flag. """
        self._stream_index = val
        return self

    def move_joints(self,
                    joint_position_array: list,
                    tag: int,
                    kc: int,
                    move_params: dict) -> StreamBuilder:
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
                                move_params: dict) -> StreamBuilder:
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
                                 move_params: dict) -> StreamBuilder:
        """ Add a moveJointsInterpolated item to the stream activity. """
        self._items.append({
            "activityType": int(ActivityType.MOVEJOINTSINTERPOLATED),
            "tag": tag,
            "moveJointsInterpolated": {
                "moveParams": move_params,
                "kinematicsConfigurationIndex": kc,
                "duration": 0.1,
                "jointPositionArray": joint_position_array,
                "jointVelocityArray": joint_velocity_array}
        })
        return self

    def move_line(self,
                  pose: Pose,
                  tag: int,
                  kc: int,
                  move_params: dict) -> StreamBuilder:
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
                         position_reference: PositionReference) -> StreamBuilder:
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
