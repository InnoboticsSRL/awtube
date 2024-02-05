from awtube.robot import Robot
import asyncio

a = Robot()


asyncio.run(a.move_line(
    {"x": 400,
     "y": -50,
     "z": 650},
    {"x": 0.8660254037844387,
     "y": 3.0616169978683824e-17,
     "z": 0.49999999999999994,
     "w": 5.3028761936245346e-17})
)
