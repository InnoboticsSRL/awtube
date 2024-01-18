import typing as tp
from enum import Enum
from pydantic import BaseModel, Field

""" Here are utility types used in the context of the robot, their
    scope is to aid working with the class awtube.
"""


class JointStates(tp.NamedTuple):
    positions: tp.List[float] = None
    velocities: tp.List[float] = None
    accelerations: tp.List[float] = None
    torques: tp.List[float] = None


class Position(tp.NamedTuple):
    x: float = None
    y: float = None
    z: float = None


class Quaternion(tp.NamedTuple):
    x: float = None
    y: float = None
    z: float = None
    w: float = None


class Pose(tp.NamedTuple):
    position: Position = None
    orientation: Quaternion = None
