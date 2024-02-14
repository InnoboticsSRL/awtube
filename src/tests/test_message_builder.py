import pytest
import json
from awtube.types.aw import *
from awtube.types.gbc import *
from awtube.commands import *
from awtube.msg_builders import stream_move_joints_cmd, \
    stream_move_joints_interpolated_cmd, \
    stream_move_line_cmd
from awtube.messages.stream_builder import StreamBuilder

"""
  Tests for the module commands, testing the validity of the json commands generated.
  If two jsons are the same but have different ordering of the keys we convert them to
  dicts before asserting if they are equal. """


class TestCommands:
    j = JointStates(positions=[1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7],
                    velocities=[1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7])
    p = Pose(position=Position(1.1, 2.2, 3.3),
             orientation=Quaternion(1.1, 2.2, 3.3, 4.4))
    t = 15
    kc = 2
    s_idx = 0

    builder: StreamBuilder = StreamBuilder()

    def test_stream_move_joints_cmd(self):
        correct = {"stream":
                   {"streamIndex": self.s_idx,
                    "items": [
                        {
                            "activityType": int(ActivityType.MOVEJOINTS),
                            "tag": self.t,
                            "moveJoints": {
                                "moveParams": {},
                                "kinematicsConfigurationIndex": self.kc,
                                "jointPositionArray":
                                self.j.positions}
                        }
                    ],
                    "name": "default",
                    "enableEndProgram": False}}
        self.builder.reset()
        result = self.builder.move_joints(joint_position_array=self.j.positions,
                                          tag=self.t,
                                          kc=self.kc,
                                          move_params={}
                                          ).build()
        assert json.loads(result) == correct

    def test_stream_move_joints_interpolated_cmd(self):
        """ Duration 0.1 always sent the same here"""
        correct = {"stream": {
            "streamIndex": self.s_idx,
            "items": [
                {
                    "activityType": int(ActivityType.MOVEJOINTSINTERPOLATED),
                    "tag": self.t,
                    "moveJointsInterpolated": {
                        "moveParams": {},
                        "kinematicsConfigurationIndex": self.kc,
                        "duration": 0.1,
                        "jointPositionArray": self.j.positions,
                        "jointVelocityArray": self.j.velocities
                    }
                }
            ],
            "name": "default",
            "enableEndProgram": False}}
        self.builder.reset()
        result = self.builder.move_joints_interpolated(joint_position_array=self.j.positions,
                                                       joint_velocity_array=self.j.positions,
                                                       tag=self.t,
                                                       kc=self.kc,
                                                       move_params={}
                                                       ).build()
        assert json.loads(result) == correct

    def test_stream_move_line_cmd(self):
        correct = {"stream":
                   {"streamIndex": self.s_idx,
                    "items": [
                        {"activityType": int(ActivityType.MOVELINE),
                         "tag": self.t,
                         "moveLine": {
                             "moveParams": {},
                             "kinematicsConfigurationIndex": self.kc,
                             "line": {
                                 "translation": {
                                     "x": self.p.position.x,
                                     "y": self.p.position.y,
                                     "z": self.p.position.z
                                 },
                                 "rotation": {
                                     "x": self.p.orientation.x,
                                     "y": self.p.orientation.y,
                                     "z": self.p.orientation.z,
                                     "w": self.p.orientation.w
                                 }

                             }
                        }}],
                    "name": "default",
                    "enableEndProgram": False}}
        self.builder.reset()
        result = self.builder.move_line(pose=self.p,
                                        tag=self.t,
                                        kc=self.kc,
                                        move_params={}
                                        ).build()
        assert json.loads(result) == correct
