from awtube.robot import Robot
from awtube.types import MachineTarget
import time

a = Robot()

a.enable()

a.target = MachineTarget.SIMULATION

a.start()

time.sleep(5)

try:
    for i in range(1000):

        print(f'Loop {i}')

        a.move_line(
            {"x": 400,
             "y": -50,
             "z": 650},
            {"x": 0.8660254037844387,
             "y": 3.0616169978683824e-17,
             "z": 0.49999999999999994,
             "w": 5.3028761936245346e-17})

        a.machine_commander.velocity = 2

        a.move_line(
            {"x": 400,
             "y": 50,
             "z": 650},
            {"x": 0.8660254037844387,
             "y": 3.0616169978683824e-17,
             "z": 0.49999999999999994,
             "w": 5.3028761936245346e-17})

        # a.machine_commander.velocity = 0.5

        a.move_line(
            {"x": 550,
             "y": 50,
             "z": 650},
            {"x": 0.8660254037844387,
             "y": 3.0616169978683824e-17,
             "z": 0.49999999999999994,
             "w": 5.3028761936245346e-17})

        # a.machine_commander.velocity = 1

        a.move_line(
            {"x": 550,
             "y": -50,
             "z": 650},
            {"x": 0.8660254037844387,
             "y": 3.0616169978683824e-17,
             "z": 0.49999999999999994,
             "w": 5.3028761936245346e-17})

        # a.machine_commander.velocity = 2

        a.move_line(
            {"x": 400,
             "y": -50,
             "z": 650},
            {"x": 0.8660254037844387,
             "y": 3.0616169978683824e-17,
             "z": 0.49999999999999994,
             "w": 5.3028761936245346e-17})
finally:
    a.kill()

    print('Finish')


# ---------------------------------------

# !/usr/bin/env python

# """ Example File used to show the use of the API """

# from awtube.awtube import AWTube
# import logging

# TIMEOUT = 30000


# def main():
#     # config file path for awtube
#     path = './awtube.json'

#     awtube = AWTube("192.168.12.58", "9001", config_path=path, blocking=False)

#     logger = awtube.get_logger()
#     handler = logging.StreamHandler()
#     logger.addHandler(handler)

#     if awtube:
# awtube.start()

# awtube.reset()

# awtube.move_line(
#     {"x": 800,
#      "y": -50,
#      "z": 650},
#     {"x": 0.8660254037844387,
#      "y": 3.0616169978683824e-17,
#      "z": 0.49999999999999994,
#      "w": 5.3028761936245346e-17}) \
#     .move_to_position(
#     {"x": 400,
#      "y": -50,
#      "z": 650},
#     {"x": 0.8660254037844387,
#      "y": 3.0616169978683824e-17,
#      "z": 0.49999999999999994,
#      "w": 5.3028761936245346e-17}) \
#     .move_line(
#     {"x": 400,
#      "y": 50,
#      "z": 650},
#     {"x": 0.8660254037844387,
#      "y": 3.0616169978683824e-17,
#      "z": 0.49999999999999994,
#      "w": 5.3028761936245346e-17}) \
#     .move_line(
#     {"x": 800,
#      "y": 50,
#      "z": 650},
#     {"x": 0.8660254037844387,
#      "y": 3.0616169978683824e-17,
#      "z": 0.49999999999999994,
#      "w": 5.3028761936245346e-17}) \
#     .move_line(
#     {"x": 800,
#      "y": -50,
#      "z": 650},
#     {"x": 0.8660254037844387,
#      "y": 3.0616169978683824e-17,
#      "z": 0.49999999999999994,
#      "w": 5.3028761936245346e-17}) \
#     .move_joints([
#         0,
#         0,
#         0,
#         0,
#         0,
#         0
#     ]) \
# .move_joints([
#     0,
#     0,
#     0,
#     0,
#     math.pi/3,
#     0
# ])

# awtube.move_joints(
#     joint_positions=[
#         0,
#         0,
#         0,
#         0,
#         math.pi/3,
#         0
#     ],
#     tag=1
# )
# awtube.move_joints(
#     joint_positions=[
#         0,
#         0,
#         0,
#         math.pi/3,
#         math.pi/3,
#         0
#     ],
#     tag=2
# )

# time.sleep(2)

# awtube.move_line(
#     {"x": 400,
#      "y": -50,
#      "z": 650},
#     {"x": 0.8660254037844387,
#      "y": 3.0616169978683824e-17,
#      "z": 0.49999999999999994,
#      "w": 5.3028761936245346e-17},
#     tag=0)

# awtube.pause()

# awtube.move_line(
#     {"x": 400,
#      "y": 50,
#      "z": 650},
#     {"x": 0.8660254037844387,
#      "y": 3.0616169978683824e-17,
#      "z": 0.49999999999999994,
#      "w": 5.3028761936245346e-17},
#     tag=1)

# awtube.run()

# awtube.move_joints(
#     [
#         0,
#         0,
#         0,
#         0,
#         0,
#         0
#     ],
#     tag=3001
# )

# while True:
#     awtube.move_joints_vel([0.1, 0, 0, 0, 0, 0])
#     time.sleep(0.5)

# not working
# awtube.kill()


# if __name__ == '__main__':
#     main()
