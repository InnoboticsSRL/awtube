Robot
=====

The class Robot represents the API to interact with the AutomationWare cobot AWTube.


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
  
  # set the target of the system to either be the physical machine or the simulation
  from awtube.types import MachineTarget
  robot.set_machine_target(MachineTarget.SIMULATION)

  # to disable the robot, deactivate actuators
  robot.disable()

  # kill connection
  robot.kill()

Reference of the class awtube.robot
-----------------------------------

.. automodule:: awtube.robot
   :members:
   :undoc-members:
   :show-inheritance:

