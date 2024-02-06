#!/usr/bin/env python3

""" Defines Errors and Exceptions on the user(AWTube) side. """

from enum import IntEnum


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

    def __init__(self, operation_error_type: int = 0, message: str = '') -> None:
        self.__type = AwtubeError(operation_error_type)
        self.__message = f'[{self.__type.name}]:{message}'
        super().__init__(self, self.__message)
