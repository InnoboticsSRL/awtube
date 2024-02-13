#!/usr/bin/env python3

""" Contains result types for functions. """

from enum import IntEnum


class FunctionResult(IntEnum):
    NONE = 0
    SUCCESS = 1
    ERROR = 2
    STOPPED = 3
