#!/usr/bin/env python3

""" Defines the Builder interface. """

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class Builder(ABC, BaseModel):
    """
    The Builder interface specifies methods for creating the different parts of
    the Message objects, which also is a pydantic BaseModel.
    """

    _build_warnings = False

    @property
    def build_warnings(self) -> bool:
        """ Flag to activate warnings during build of json. """
        return self._build_warnings

    @build_warnings.setter
    def build_warnings(self, val: bool) -> None:
        """ Flag to activate warnings during build of json. """
        self._build_warnings = val

    @abstractmethod
    def build(self) -> None:
        raise NotImplementedError
