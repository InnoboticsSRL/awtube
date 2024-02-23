import json
import pytest
from awtube.types import ActivityType
from tests import awtube

def test_create_class():
    assert awtube

def test_private_attributes():
    with pytest.raises(AttributeError):
        awtube.__blocking
    assert True

def test_send_command():
    awtube.move_line(
        {"x": 800,
         "y": -50,
         "z": 650},
        {"x": 0.8660254037844387,
         "y": 3.0616169978683824e-17,
         "z": 0.49999999999999994,
         "w": 5.3028761936245346e-17})
    assert awtube.outgoing.empty() == False
    assert awtube.outgoing.qsize() == 1
    js = json.loads(awtube.outgoing.get())
    assert js['stream']['items'][0]['activityType'] == ActivityType.MOVELINE
    
def test_send_commands():
    awtube.move_line(
        {"x": 800,
         "y": -50,
         "z": 650},
        {"x": 0.8660254037844387,
         "y": 3.0616169978683824e-17,
         "z": 0.49999999999999994,
         "w": 5.3028761936245346e-17})
    awtube.move_line(
        {"x": 800,
         "y": -50,
         "z": 650},
        {"x": 0.8660254037844387,
         "y": 3.0616169978683824e-17,
         "z": 0.49999999999999994,
         "w": 5.3028761936245346e-17})
    assert awtube.outgoing.empty() == False
    assert awtube.outgoing.qsize() == 2
    while not awtube.outgoing.empty():
        js = json.loads(awtube.outgoing.get())
        assert js['stream']['items'][0]['activityType'] == ActivityType.MOVELINE

def test_send_move_joints_interpolated():
    joint_positions = [0,0,0,0,0,0]
    joint_velocities = [0,0,0,0,0,0]
    with pytest.raises(Exception):
        awtube.move_joints_interpolated(joint_positions=joint_positions, joint_velocities=joint_velocities)
    assert True
    
# def test_move_joints():
#     awtube.move_joints([
#         0,
#         0,
#         0,
#         0,
#         3.14,
#         0
#     ])

# def test_chaining_methods_call():
#     pos = {"x": 800,
#          "y": -50,
#          "z": 650}
#     quat = {"x": 0.8660254037844387,
#          "y": 3.0616169978683824e-17,
#          "z": 0.49999999999999994,
#          "w": 5.3028761936245346e-17}
#     awtube.move_line(pos, quat).move_line(pos,quat)
