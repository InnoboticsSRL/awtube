#!/usr/bin/env python3

""" Builder methods that give the messages to be sent to GBC. """

from awtube.gbc_types import *
from awtube.aw_types import *
import json


def stream_move_joints_cmd(
        joints: JointStates,
        stream_index: int = 0,
        tag: int = 0,
        kinematics_configuration_index: int = 0,
        debug: bool = False) -> str:
    """ Create moveJoints json command """
    s = Stream(stream=StreamConfig(
        streamIndex=stream_index,
        items=[
            MoveJointsStreamItem(
                tag=tag,
                move_joints=MoveJointsStreamConfig(
                    kinematics_configuration_index=kinematics_configuration_index,
                    joint_position_array=list(joints.positions)
                )
            )
        ]
    )
    ).model_dump_json(by_alias=True)
    # TODO: log
    # if debug:
    #     print(s)
    return s


def stream_move_joints_interpolated_cmd(
        joints: JointStates,
        stream_index: int = 0,
        tag: int = 0,
        kinematics_configuration_index: int = 0,
        debug: bool = False) -> str:
    """ Create moveJointsInterpolated json command """
    s = Stream(stream=StreamConfig(
        streamIndex=stream_index,
        items=[
            MoveJointsInterpolatedStreamItem(
                tag=tag,
                move_joints_interpolated=MoveJointsInterpolatedStreamConfig(
                    kinematics_configuration_index=kinematics_configuration_index,
                    joint_position_array=list(joints.positions),
                    joint_velocity_array=list(joints.velocities)
                )
            )
        ]
    )
    ).model_dump_json(by_alias=True)
    # TODO: log
    return s


def solo_activity_move_joints_cmd(
        joints: JointStates,
        stream_index: int = 0,
        tag: int = 0,
        kinematics_configuration_index: int = 0,
        debug: bool = False) -> str:
    """ Create activityMoveJoints json command """
    return json.dumps({
        "command": {
            "soloActivity": {
                "0": {
                    "command": {
                        "tag": tag,
                        "activityType": 3,
                        "moveJoints": {
                            "jointPositionArray": list(joints.positions)
                        }
                    }
                }
            }
        }
    })


def stream_move_line_cmd(pose: Pose, stream_index: int = 0, tag: int = 0, kinematics_configuration_index: int = 0, debug: bool = False) -> str:
    s = Stream(stream=StreamConfig(
        streamIndex=stream_index,
        enable_end_program=False,
        items=[
            MoveLineStreamItem(
                tag=tag,
                move_line=MoveLineStreamConfig(
                    kinematics_configuration_index=kinematics_configuration_index,
                    line=Line(
                        # TODO: clean up
                        translation=Vector3(
                            x=pose.position.x,
                            y=pose.position.y,
                            z=pose.position.z
                        ),
                        rotation=Quat(
                            x=pose.orientation.x,
                            y=pose.orientation.y,
                            z=pose.orientation.z,
                            w=pose.orientation.w
                        )
                    )

                )
            )

        ]
    )
    ).model_dump_json(by_alias=True)
    # TODO: log
    if debug:
        print(s)
    return s


def get_stream_pause_program(stream_index: int = 0, debug: bool = False) -> str:
    s = Stream(stream=StreamConfig(
        streamIndex=stream_index,
        enable_end_program=False,
        items=[
            PauseProgramStreamItem()
        ]
    )
    ).model_dump_json(by_alias=True)
    # TODO: log
    if debug:
        print(s)
    return s


def get_machine_command(control_word: ControlWord, machine: int = 0) -> str:
    # s = MachineCommand(machine=machine,
    #                    control_word=control_word
    #                    ).model_dump_json(by_alias=True)
    # TODO: fix with builder

    s = {"command": {"machine": {f"{machine}": {
        "command": {"controlWord": int(control_word)}}}}}
    return json.dumps(s)


def get_machine_target_command(target: MachineTarget, machine: int = 0) -> str:
    s = {"command": {"machine": {f"{machine}": {
        "target": int(target)}}}}
    return json.dumps(s)


# TODO: fix
def get_kinematics_configuration_command(limits: bool, kc_config: int = 0) -> str:
    s = {"command": {
        "kinematicsConfiguration": {
            f"{kc_config}": {
                "command": {
                    # Whether soft joint limits should be disabled
                    "disableLimits": str(limits).lower(),
                    # "doStop": "false",
                    # Desired feed rate, with 1 being normal and zero being stopped. A value of 2 would give double normal speed, for example
                    # "fro",
                    # Optional logical rotation applied to all moves
                    # "rotation",
                    # Optional logical translation applied to all moves
                    # "translation",
                }
            }}}}
    return json.dumps(s)


def get_machine_command_heartbeat(heartbeat: int, machine: int = 0) -> str:
    # s = MachineCommand(machine=machine,
    #                    control_word=control_word
    #                    ).model_dump_json(by_alias=True)
    # TODO: fix with builder

    s = {"command": {"machine": {f"{machine}": {
        "command": {"heartbeat": heartbeat}}}}}
    return json.dumps(s)


def get_stream_move_to_position(
        pose: Pose,
        stream_index: int = 0,
        tag: int = 0,
        kinematics_configuration_index: int = 0,
        debug: bool = False) -> str:
    s = Stream(stream=StreamConfig(
        streamIndex=stream_index,
        items=[
            MoveToPositionStreamItem(
                tag=tag,
                move_to_position=MoveToPositionStreamConfig(
                    kinematics_configuration_index=kinematics_configuration_index,
                    cartesian_position=CartesianPositionConfig(
                        position=CartesianPosition(
                            # TODO: clean up
                            translation=Vector3(
                                x=pose.position.x,
                                y=pose.position.y,
                                z=pose.position.z
                            ),
                            rotation=Quat(
                                x=pose.orientation.x,
                                y=pose.orientation.y,
                                z=pose.orientation.z,
                                w=pose.orientation.w
                            )
                        ),
                        # TODO: not sure
                        configuration=kinematics_configuration_index

                    )
                )
            )
        ]
    )
    ).model_dump_json(by_alias=True)
    # TODO: log
    if debug:
        print(s)
    return s


def stream_move_joints_cmd_at_vel(
        joints: JointStates,
        stream_index: int = 0,
        tag: int = 0,
        kinematics_configuration_index: int = 0,
        debug: bool = False) -> str:
    return (json.dumps({
        "stream": {
            "streamIndex": stream_index,
            "items": [
                {
                    "activityType": 4,
                    "tag": tag,
                    "moveJointsAtVelocity": {
                        # TODO
                        "moveParams": {},
                        "kinematicsConfigurationIndex": kinematics_configuration_index,
                        "jointVelocityArray": list(joints.velocities)
                    }
                }
            ]
        }
    }))
