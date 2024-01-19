import pytest
import json
from awtube.aw_types import *
from awtube.gbc_types import *
from awtube.commands import *

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
        assert json.loads(stream_move_joints_cmd(
            joints=self.j, stream_index=self.s_idx, tag=self.t, kinematics_configuration_index=self.kc)) == correct

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
        assert json.loads(stream_move_joints_interpolated_cmd(
            joints=self.j, stream_index=self.s_idx, tag=self.t, kinematics_configuration_index=self.kc)) == correct

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
        assert json.loads(stream_move_line_cmd(
            pose=self.p, stream_index=self.s_idx, tag=self.t, kinematics_configuration_index=self.kc)) == correct
