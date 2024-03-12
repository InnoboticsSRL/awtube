#!/usr/bin/env python3

from awtube.robot import Robot
from awtube.types import MachineTarget

r = Robot()
r.start()
r.set_machine_target(MachineTarget.SIMULATION)
r.enable()

try:
    for i in range(100):

        print(f'Iteration: {i}')

        r.move_joints([
        0,
        0,
        0,
        0,
        0,
        0
    ])

        r.set_speed(2)

        r.move_joints([
        0,
        0,
        0,
        0,
        0,
        0
    ])

        r.set_speed(0.5)

        r.move_joints([
        0,
        0,
        0,
        0,
        0,
        0
    ])

finally:
    r.kill()
    print('Finished')


     \
# .move_joints([
#     0,
#     0,
#     0,
#     0,
#     math.pi/3,
#     0
# ])