#!/usr/bin/env python3

from awtube.robot import Robot
from awtube.types import MachineTarget

r = Robot('192.168.3.191')
r.start()
r.set_machine_target(MachineTarget.SIMULATION)
r.enable()
try:
    for i in range(100):
        print(f'Iteration: {i}')
        r.move_line(
            {"x": 400,
            "y": -50,
            "z": 650},
            {"x": 0.8660254037844387,
            "y": 3.0616169978683824e-17,
            "z": 0.49999999999999994,
            "w": 5.3028761936245346e-17})
        r.set_speed(2)
        r.move_line(
            {"x": 400,
            "y": 50,
            "z": 650},
            {"x": 0.8660254037844387,
            "y": 3.0616169978683824e-17,
            "z": 0.49999999999999994,
            "w": 5.3028761936245346e-17})
        r.set_speed(0.5)
        r.move_line(
            {"x": 550,
            "y": 50,
            "z": 650},
            {"x": 0.8660254037844387,
            "y": 3.0616169978683824e-17,
            "z": 0.49999999999999994,
            "w": 5.3028761936245346e-17})
        r.set_speed(1)
        r.move_line(
            {"x": 550,
            "y": -50,
            "z": 650},
            {"x": 0.8660254037844387,
            "y": 3.0616169978683824e-17,
            "z": 0.49999999999999994,
            "w": 5.3028761936245346e-17})
        r.set_speed(2)
        r.move_line(
            {"x": 400,
            "y": -50,
            "z": 650},
            {"x": 0.8660254037844387,
            "y": 3.0616169978683824e-17,
            "z": 0.49999999999999994,
            "w": 5.3028761936245346e-17})
finally:
    r.kill()
    print('Finished')