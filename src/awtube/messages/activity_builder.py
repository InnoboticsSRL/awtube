#!/usr/bin/env python3

""" Defines the StreamBuilder implementation of the Builder interface. """

from __future__ import annotations

from awtube.messages.builder import Builder

from awtube.types.gbc import ActivityType, PositionReference
from awtube.types.aw import Pose, Position


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
