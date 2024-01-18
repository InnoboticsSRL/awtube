#!/usr/bin/env python3

import asyncio
from awtube.aw_types import *
from awtube.gbc_types import *
from awtube.commands import *
from awtube.exceptions import *
# from awtube.awtube_node import AWTubeNode
import sys
import pytest


# async def spinning(node: AWTubeNode):
#     while rclpy.ok():
#         rclpy.spin_once(node, timeout_sec=0.01)
#         await asyncio.sleep(0.001)
#         sys.exit(0)


# async def run(args, loop: asyncio.AbstractEventLoop):
#     rclpy.init(args=args)
#     awtube_node = AWTubeNode()

#     spin_task = loop.create_task(spinning(awtube_node))
#     connect_task = loop.create_task(awtube_node.listen())
#     try:
#         await asyncio.gather(spin_task, connect_task)
#     except asyncio.exceptions.CancelledError:
#         pass

#     awtube_node.destroy_node()
#     rclpy.shutdown()


# def test_ros2():
#     with pytest.raises(SystemExit) as pytest_wrapped_e:
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(run(None, loop=loop))
#     assert pytest_wrapped_e.type == SystemExit
#     assert pytest_wrapped_e.value.code == 0
