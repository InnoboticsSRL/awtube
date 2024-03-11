#!/usr/bin/env python3

""" Defines Errors and Exceptions on the user(AWTube) side. """

from __future__ import annotations
from enum import IntEnum


class ThreadLoopNotRunningError(Exception):
    pass


class CancelledTask(Exception):
    pass


class AwtubeError(IntEnum):
    NONE = 0
    BAD_ARGUMENT = 1
    DISSCONNECTED = 2


class AWTubeErrorException(Exception):
    """ Raised when there's an error on the library side. """
    __type = AwtubeError.NONE

    @property
    def type(self) -> AwtubeError:
        """ Return OperationError type """
        return self.__type

    def __init__(self, operation_error_type: int = 0, message: str = ''):
        self.__type = AwtubeError(operation_error_type)
        self.__message = f'[{self.__type.name}]:{message}'
        super().__init__(self, self.__message)


class OperationError(IntEnum):
    """ Types of OperationError defined by GBC. """
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


# class OperationErrorException(Exception):
#     """ Raised when there's and operation error signaled by GBC. """
#     __type = OperationError.NONE

#     @property
#     def type(self) -> OperationError:
#         """ Return OperationError type """
#         return self.__type

#     def __init__(self, operation_error_type: int = 0):
#         self.__type = OperationError(operation_error_type)
#         self.__message = self.__type.name
#         super().__init__(self, self.__message)


class HeartbeatFailure(Exception):
    """ Raised when heartbeat is not sent in predefined time slot. """
    pass

    # def __init__(self, message="Heartbeat missed!"):
    #     self.message = message
    #     super().__init__(self.message)


class TelemetryLoss(Exception):
    """ Raised when telemetry is not recieved in predefined time slot. """
    pass

    # def __init__(self, message="Heartbeat missed!"):
    #     self.message = message
    #     super().__init__(self.message)
