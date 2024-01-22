import typing as tp
from enum import IntEnum
from pydantic import BaseModel, Field


class StreamState(IntEnum):
    IDLE = 0
    ACTIVE = 1
    PAUSED = 2
    PAUSED_BY_ACTIVITY = 3
    STOPPING = 4
    STOPPED = 5


class StreamCommand(IntEnum):
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


class OperationError(IntEnum):
    NONE = 0
    HLC_HEARTBEAT_LOST = 1
    OPERATION_NOT_ENABLED = 2
    INVALID_ARC = 3
    TOOL_INDEX_OUT_OF_RANGE = 4
    JOINT_LIMIT_EXCEEDED = 5
    KINEMATICS_FK_INVALID_VALUE = 6
    KINEMATICS_IK_INVALID_VALUE = 7
    KINEMATICS_INVALID_KIN_CHAIN_PARAMS = 8
    JOINT_DISCONTINUITY = 9
    JOINT_OVER_SPEED = 10
    INVALID_ROTATION = 11
    CONFIG_RELOADED = 12
    KINEMATICS_ENVELOPE_VIOLATION = 13
    KINEMATICS_NEAR_SINGULARITY = 14


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
    target: int = Field(None)
    # Number of times we have tried to connect to the target
    target_connect_retry_cnt: int = Field(None, alias='targetConnectRetryCnt')


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


class MoveParametersConfig(BaseModel):
    """ Configuration parameters for move parameters. """
    amax_percentage: float = Field(None, alias='amaxPercentage')
    blend_time_percentage: float = Field(None, alias='blendTimePercentage')
    blend_tolerance: float = Field(None, alias='blendTolerance')
    blend_type: BlendType = Field(None, alias='blendType')
    jmax_percentage: float = Field(None, alias='jmaxPercentage')
    # Linear and angular limit profile to use for mov
    limit_configuration_index: float = Field(
        None, alias='limitConfigurationIndex')
    name: str = Field(None)
    sync_type: SyncType = Field(None, alias='syncType')
    sync_value: float = Field(None, alias='syncValue')
    tool_index: int = Field(None, alias='toolIndex')
    vmax: float = Field(None)
    vmax_percentage: float = Field(None, alias='vmaxPercentage')


class StreamConfig(BaseModel):
    stream_index: int = Field(None, alias='streamIndex')
    items: list = Field(None)
    name: int = Field('default')
    enable_end_program: bool = Field(
        False, serialization_alias='enableEndProgram')


class MoveJointsStreamConfig(BaseModel):
    move_params: MoveParametersConfig | dict = Field(
        {}, serialization_alias='moveParams')
    kinematics_configuration_index: int = Field(
        None, serialization_alias='kinematicsConfigurationIndex')
    joint_position_array: list = Field(
        None, serialization_alias='jointPositionArray')


class MoveJointsStreamItem(BaseModel):
    activity_type: ActivityType = Field(
        ActivityType.MOVEJOINTS, serialization_alias='activityType')
    tag: int = Field(None)
    move_joints: MoveJointsStreamConfig = Field(
        None, serialization_alias='moveJoints')


class MoveJointsInterpolatedStreamConfig(BaseModel):
    move_params: MoveParametersConfig | dict = Field(
        {}, serialization_alias='moveParams')
    kinematics_configuration_index: int = Field(
        None, serialization_alias='kinematicsConfigurationIndex')
    duration: float = Field(
        0.100)
    joint_position_array: list = Field(
        None, serialization_alias='jointPositionArray')
    joint_velocity_array: list = Field(
        None, serialization_alias='jointVelocityArray')


class MoveJointsInterpolatedStreamItem(BaseModel):
    activity_type: ActivityType = Field(
        ActivityType.MOVEJOINTSINTERPOLATED, serialization_alias='activityType')
    tag: int = Field(None)
    move_joints_interpolated: MoveJointsInterpolatedStreamConfig = Field(
        None, serialization_alias='moveJointsInterpolated')


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


class MoveToPositionStreamConfig(BaseModel):
    move_params: MoveParametersConfig | dict = Field(
        {}, serialization_alias='moveParams')
    kinematics_configuration_index: int = Field(
        None, serialization_alias='kinematicsConfigurationIndex')
    cartesian_position: CartesianPositionConfig = Field(
        None, serialization_alias='cartesianPosition')


class MoveToPositionStreamItem(BaseModel):
    activity_type: ActivityType = Field(
        ActivityType.MOVETOPOSITION, serialization_alias='activityType')
    tag: int = Field(None)
    move_to_position: MoveToPositionStreamConfig = Field(
        None, serialization_alias='moveToPosition')


class Line(BaseModel):
    translation: Vector3 = Field(None)
    rotation: Quat = Field(None)


class MoveLineStreamConfig(BaseModel):
    move_params: MoveParametersConfig | dict = Field(
        {}, serialization_alias='moveParams')
    kinematics_configuration_index: int = Field(
        None, serialization_alias='kinematicsConfigurationIndex')
    line: Line = Field(
        None, serialization_alias='line')


class MoveLineStreamItem(BaseModel):
    activity_type: ActivityType = Field(
        ActivityType.MOVELINE, serialization_alias='activityType')
    tag: int = Field(None)
    move_line: MoveLineStreamConfig = Field(
        None, serialization_alias='moveLine')


class PauseProgramStreamItem(BaseModel):
    activity_type: ActivityType = Field(
        ActivityType.PAUSEPROGRAM, serialization_alias='activityType')


# state machine for connection
class MachineCommand(BaseModel):
    machine: int = Field(0)
    control_word: ControlWord = Field(
        None, serialization_alias='controlWord'
    )


class Stream(BaseModel):
    stream: StreamConfig = Field(None)
