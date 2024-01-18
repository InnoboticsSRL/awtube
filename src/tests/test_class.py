# import pytest
# from tests import awtube


# def test_create_class():
#     assert awtube

# path = './gbc_ros2_driver/gbc_ros2_driver/awtube.json'

# awtube = AWTube("192.168.12.58", "9001", config_path=path, blocking=False)


# def test_private_attributes():
#     with pytest.raises(AttributeError):
#         awtube.__blocking
#     assert True


# def test_move_line():
#     awtube.move_line(
#         {"x": 800,
#          "y": -50,
#          "z": 650},
#         {"x": 0.8660254037844387,
#          "y": 3.0616169978683824e-17,
#          "z": 0.49999999999999994,
#          "w": 5.3028761936245346e-17})


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
#            "y": -50,
#            "z": 650}
#     quat = {"x": 0.8660254037844387,
#             "y": 3.0616169978683824e-17,
#             "z": 0.49999999999999994,
#             "w": 5.3028761936245346e-17}
#     awtube.move_line(pos, quat).move_line(pos, quat)
