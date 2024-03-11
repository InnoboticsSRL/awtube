Introduction
============

.. warning::
   This project is under active development!

This project offers an API to interact with the AutomationWare cobot AWTube.

It offers basic functions such as:

* move joints (:func:`~awtube.robot.Robot.move_joints`)
* move end effector to a positon (:func:`~awtube.robot.Robot.move_to_position`)
* move end effector to a positon through a straight line (:func:`~awtube.robot.Robot.move_line`)
* send a trajectory for the robot to execute (:func:`~awtube.robot.Robot.move_joints_interpolated`)


Example on how to use the API:

.. code-block:: python
  
  from awtube.robot import Robot
  
  robot = Robot('102.168.0.0', port='9001')
  
  # to start communication with robot
  robot.start()

  # to enable the robot, activate the actuators
  robot.enable()

  # send a move_line command
  robot.move_line(
            {"x": 400,
             "y": -50,
             "z": 650},
            {"x": 0.8660254037844387,
             "y": 3.0616169978683824e-17,
             "z": 0.49999999999999994,
             "w": 5.3028761936245346e-17})

  # to disable the robot, deactivate actuators
  robot.disable()

  # kill connection
  robot.kill()


