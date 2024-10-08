#!/usr/bin/env python3

import csv
from awtube.robot import Robot
from awtube.types import MachineTarget

# Define a simple class to hold the positions and velocities
class Point:
    def __init__(self, positions, velocities):
        self.positions = positions
        self.velocities = velocities

    def negate_velocities(self):
        # Negate each velocity
        self.velocities = [-v for v in self.velocities]
        return self

# Function to read CSV and create a list of Point objects
def read_csv_and_create_points(filename):
    points = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
#        slice = list(reader)[:5]
        slice = reader
        for row in slice:
            # Assuming the first column is the timecode, followed by 6 positions and 6 velocities
            positions = list(map(float, row[1:7]))
            velocities = list(map(float, row[7:13]))
            points.append(Point(positions, velocities))
    return points

points_pick_to_zero = read_csv_and_create_points('../../points.csv')
points_zero_to_pick=list(map(lambda pt: pt.negate_velocities(), points_pick_to_zero[::-1]))

r = Robot('10.10.0.2')
r.start()
r.set_machine_target(MachineTarget.SIMULATION)
r.set_safe_limits(False)
r.enable()
try:
    r.move_joints_interpolated(points_zero_to_pick)
    print("DONE ZERO TO PICK")
    r.move_joints_interpolated(points_pick_to_zero)
    print("DONE PICK TO ZERO")
finally:
    print('Finished!')
