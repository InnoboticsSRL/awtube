#!/usr/bin/env python3

""" Contains types inherent to AW. """

from awtube.errors import OperationError
from enum import IntEnum
import typing as tp
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


""" Contains result types for functions. """


class FunctionResult(IntEnum):
    NONE = 0
    SUCCESS = 1
    ERROR = 2
    STOPPED = 3


""" Contains types inherent to GBC modeled with pydantic. """


class StreamState(IntEnum):
    IDLE = 0
    ACTIVE = 1
    PAUSED = 2
    PAUSED_BY_ACTIVITY = 3
    STOPPING = 4
    STOPPED = 5


class StreamCommandType(IntEnum):
    RUN = 0
    PAUSE = 1
    STOP = 2


class BlendType(IntEnum):
    # No blend used for move
    NONE = 0
    # An overlapped blend to be used for move
    OVERLAPPED = 1


class SyncType(IntEnum):
    # No sync for move
    NONE = 0
    # Ensure move is of specified duration in milliseconds
    DURATION_MS = 1
    # Ensure move ends at the specified clock tick (not currently supported)
    AT_TICK = 2


class ActivityType(IntEnum):
    NONE = 0
    PAUSEPROGRAM = 1
    ENDPROGRAM = 2
    MOVEJOINTS = 3
    MOVEJOINTSATVELOCITY = 4
    MOVELINE = 5
    MOVEVECTORATVELOCITY = 6
    MOVEROTATIONATVELOCITY = 7
    MOVEARC = 8
    MOVETOPOSITION = 10
    SETDOUT = 11
    SETIOUT = 12
    SETAOUT = 13
    DWELL = 14
    SPINDLE = 15
    MOVEJOINTSINTERPOLATED = 16
    TOOLOFFSET = 22


class ControlWord(IntEnum):
    # Startup => Not Ready to Switch ON
    RESET = 0
    # Switched On => Ready to Switch On
    SHUTDOWN = 6
    # Ready to Switch On => Switch On Disabled
    QUICKSTOP = 7
    #  Fault => Switch On Disabled
    FAULTRESET = 15
    FAULTRESET128 = 128


class MachineTarget(IntEnum):
    NONE = 0
    FIELDBUS = 1
    SIMULATION = 2


class MachineStatus(BaseModel):
    # Indicates an operation error in GBC that is recoverable
    operation_error: OperationError = Field(0, alias='operationError')
    # str that explains error
    operation_error_message: str = Field('', alias='operationErrorMessage')
    heartbeat: int = Field(None)
    # CiA 402 status word for the machine as a whole
    status_word: int = Field(None, alias='statusWord')
    # Word containing any active faults the machine may have
    active_fault: int = Field(None, alias='activeFault')
    # Word containing the fault history (faults that were active when the machine entered the fault state)
    fault_history: int = Field(None, alias='faultHistory')
    # CiA 402 control word for the machine as a whole
    control_word: int = Field(None, alias='controlWord')
    # What the current target of the machine is - e.g. is it is simulation mode
    target: MachineTarget = Field(MachineTarget.NONE)
    # Number of times we have tried to connect to the target
    target_connect_retry_cnt: int = Field(None, alias='targetConnectRetryCnt')


class KinematicsConfigurationStatus(BaseModel):
    # Indicates if soft limits (machine extents) are disabled
    limits_disabled: bool = Field(False, alias='limitsDisabled')
    # Feed rate target value
    fro_target: float = Field(0, alias='froTarget')
    # Feed rate actual value
    fro_actual: float = Field(0, alias='froActual')
    # Configuration (for example, shoulder/elbow/wrist) of the kinematics configuration
    configuration: int = Field(0, alias='configuration')
    # Current tool index
    tool_index: int = Field(0, alias='toolIndex')
    # Word containing the fault history (faults that were active when the machine entered the fault state)
    is_near_singularity: int = Field(0, alias='isNearSingularity')
    # Position
    # position: Position = Field(None)
    # Offset
    # offset: Position = Field(None)


class StreamStatus(BaseModel):
    capacity: int = Field(None)
    queued: int = Field(None)
    state: int = Field(None)
    tag: int = Field(None)
    time: int = Field(None)
    read_count: int = Field(None, alias='readCount')
    write_count: int = Field(None, alias='writeCount')


class ActivityStatus(BaseModel):
    tag: int = Field(None)
    state: int = Field(None)


class Vector3(BaseModel):
    x: float = Field(None)
    y: float = Field(None)
    z: float = Field(None)


class Quat(BaseModel):
    x: float = Field(None)
    y: float = Field(None)
    z: float = Field(None)
    w: float = Field(None)


class PositionReference(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    MOVESUPERIMPOSED = 2


class CartesianPosition(BaseModel):
    translation: Vector3 = Field(None)
    rotation: Quat = Field(None)
    frame_index: Quat = Field(None, serialization_alias='frameIndex')
    position_reference: PositionReference = Field(
        None, serialization_alias='positionReference')


class CartesianPositionConfig(BaseModel):
    position: CartesianPosition = Field(None)
    configuration: int = Field(None)


class Line(BaseModel):
    translation: Vector3 = Field(None)
    rotation: Quat = Field(None)


# state machine for connection
class MachineCommand(BaseModel):
    machine: int = Field(0)
    control_word: ControlWord = Field(
        None, serialization_alias='controlWord'
    )


class IntegerOutputElement(BaseModel):
    effectiveValue: int
    setValue: int
    override: bool

class BooleanOutputElement(BaseModel):
    effectiveValue: bool
    setValue: int
    override: bool

class BooleanInputElement(BaseModel):
    actValue: int
    setValue: int
    override: bool

class Serial(BaseModel):
    data: list
    length: int
    statusWord: int


class Status(BaseModel):
    """ Status of the machine given by GBC. """
    machine: MachineStatus = Field(None)
    kc: tp.List[KinematicsConfigurationStatus]
    din: tp.List[BooleanInputElement]
    dout: tp.List[BooleanOutputElement]
    iout: tp.List[IntegerOutputElement]
    # not all versions of GBC have it
    serial: tp.Optional[Serial] = None
