import typing as tp
from enum import IntEnum
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from awtube.errors.gbc_errors import OperationError


class ActivityBuilder(BaseModel):
    tag: int = Field(None)


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


# class OperationError(IntEnum):
#     NONE = 0
#     OPERATION_NOT_ENABLED = 1
#     INVALID_ARC = 2
#     TOOL_INDEX_OUT_OF_RANGE = 3
#     JOINT_LIMIT_EXCEEDED = 4
#     KINEMATICS_FK_INVALID_VALUE = 5
#     KINEMATICS_IK_INVALID_VALUE = 6
#     KINEMATICS_INVALID_KIN_CHAIN_PARAMS = 7
#     JOINT_DISCONTINUITY = 8
#     JOINT_OVER_SPEED = 9
#     INVALID_ROTATION = 10
#     CONFIG_RELOADED = 11


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
    TOOLOFFSET = 22


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


class Stream(BaseModel):
    stream: StreamConfig = Field(None)


""" Builders pattern """


class ActivityStreamItem(ABC, BaseModel):
    activity_type: ActivityType = Field(serialization_alias='activityType')
    tag: int = Field(0, serialization_alias='activityType')


class ActivityController(ABC):
    """
        Interface for activity controller.
    """
    kinematics_configuration_index: int

    def next_tag(self) -> int:
        pass

    def execute(self, cmd: ActivityStreamItem):
        pass


class RealActivityController(ActivityController):
    kinematics_configuration_index = 0


class ActivityBuilder(ABC):
    tag: int
    controller: ActivityController
    command_name: str
    activity_type: ActivityType
    # triggers

    def __init__(self, controller: ActivityController) -> None:
        # super().__init__()
        self.controller = controller
        self.tag = controller.next_tag()
        # self.promise

    def with_tag(self, tag: int) -> ActivityBuilder:
        self.tag = tag
        return self

    def command() -> ActivityStreamItem:
        pass

    def get_command_name():
        pass

    def get_activity_type():
        pass

    @abstractmethod
    def build():
        pass


class SimpleMoveBuilder(ActivityBuilder):
    _params: MoveParametersConfig = {}

    def params(self, params: MoveParametersConfig):
        if params:
            self._params = params
        return self

    def duration(duration_in_millis: int):
        pass

    def build(self):
        return {
            'moveParams': self._params,
            'kinematicsConfigurationIndex': self.controller.kinematics_configuration_index
        }


class MoveJointsBuilder(SimpleMoveBuilder):
    command_name: str = 'moveJoints'
    activity_type: ActivityType = ActivityType.MOVEJOINTS
    _position_reference: PositionReference
    joint_position_array: list

    def relative(self, is_relative: bool = True):
        self._position_reference = PositionReference.RELATIVE if is_relative else PositionReference.ABSOLUTE
        return self

    def joints(self, values: list):
        self.joint_position_array = values
        return self

    def build(self):
        result = super().build()
        result.joint_position_array = self.joint_position_array
        result.positionReference = self._position_reference
        return


cont = RealActivityController()
a = MoveJointsBuilder(cont).relative().joints([0, 0, 0, 0, 0]).build()
# print(a.__dict__)
