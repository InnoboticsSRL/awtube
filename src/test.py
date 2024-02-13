from awtube.robot import Robot
from awtube.types.gbc import MachineTarget
import time

a = Robot()

a.enable()

# a.start()
a.target = MachineTarget.SIMULATION

a.startup()

time.sleep(5)

print('hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')

a.machine_commander.velocity = 0.2

a.move_line(
    {"x": 400,
     "y": -50,
     "z": 650},
    {"x": 0.8660254037844387,
     "y": 3.0616169978683824e-17,
     "z": 0.49999999999999994,
     "w": 5.3028761936245346e-17})

# a.machine_commander.velocity = 0.2


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

a.kill()

print('second hereee')
