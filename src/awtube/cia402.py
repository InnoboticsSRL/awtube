#!/usr/bin/env python3

"""
    Utils to work with the CIA402 state machine.
"""

from enum import Enum


class CIA402MachineState(Enum):
    """ States of the CIA402 Machine """
    UNKNOWN = "UNKNOWN"
    FAULT_REACTION_ACTIVE = "FAULT_REACTION_ACTIVE"
    FAULT = "FAULT"
    NOT_READY_TO_SWITCH_ON = "NOT_READY_TO_SWITCH_ON"
    SWITCH_ON_DISABLED = "SWITCH_ON_DISABLED"
    READY_TO_SWITCH_ON = "READY_TO_SWITCH_ON"
    SWITCHED_ON = "SWITCHED_ON"
    OPERATION_ENABLED = "OPERATION_ENABLED"
    QUICK_STOP = "QUICK_STOP"


def device_state(status_word) -> CIA402MachineState:
    """ Convert a status word into a CIA402MachineState. """
    if (status_word & 0b01001111) == 0b00000000:
        return CIA402MachineState.NOT_READY_TO_SWITCH_ON
    elif (status_word & 0b01001111) == 0b01000000:
        return CIA402MachineState.SWITCH_ON_DISABLED
    elif (status_word & 0b01101111) == 0b00100001:
        return CIA402MachineState.READY_TO_SWITCH_ON
    elif (status_word & 0b01101111) == 0b00100011:
        return CIA402MachineState.SWITCHED_ON
    elif (status_word & 0b01101111) == 0b00100111:
        return CIA402MachineState.OPERATION_ENABLED
    elif (status_word & 0b01101111) == 0b00000111:
        return CIA402MachineState.QUICK_STOP
    elif (status_word & 0b01001111) == 0b00001111:
        return CIA402MachineState.FAULT_REACTION_ACTIVE
    elif (status_word & 0b01001111) == 0b00001000:
        return CIA402MachineState.FAULT
    else:
        return CIA402MachineState.UNKNOWN


def transition(state, control_word, fault_reset=True) -> int:
    """ Return next step used to go to operational """
    if state == CIA402MachineState.UNKNOWN:
        return control_word
    elif state == CIA402MachineState.NOT_READY_TO_SWITCH_ON:
        return control_word
    elif state == CIA402MachineState.SWITCH_ON_DISABLED:
        return (control_word & 0b01111110) | 0b00000110
    elif state == CIA402MachineState.READY_TO_SWITCH_ON:
        return (control_word & 0b01110111) | 0b00000111
    elif state == CIA402MachineState.SWITCHED_ON:
        return (control_word & 0b01111111) | 0b00001111
    elif state == CIA402MachineState.OPERATION_ENABLED:
        return control_word
    elif state == CIA402MachineState.QUICK_STOP:
        return (control_word & 0b01111111) | 0b00001111
    elif state == CIA402MachineState.FAULT_REACTION_ACTIVE:
        return control_word
    elif state == CIA402MachineState.FAULT:
        if fault_reset:
            fault_reset = False
            return 0b10000000
        else:
            return control_word
    else:
        return control_word


###################################################################


class MachineState(Enum):
    UNKNOWN = "UNKNOWN"
    FAULT_REACTION_ACTIVE = "FAULT_REACTION_ACTIVE"
    FAULT = "FAULT"
    NOT_READY_TO_SWITCH_ON = "NOT_READY_TO_SWITCH_ON"
    SWITCH_ON_DISABLED = "SWITCH_ON_DISABLED"
    READY_TO_SWITCH_ON = "READY_TO_SWITCH_ON"
    SWITCHED_ON = "SWITCHED_ON"
    OPERATION_ENABLED = "OPERATION_ENABLED"
    QUICK_STOP = "QUICK_STOP"


class DesiredState(Enum):
    NONE = "NONE"
    OPERATIONAL = "OPERATIONAL"
    STANDBY = "STANDBY"


# def device_state(status: int) -> MachineState:
#     if status & 0b1000:
#         return MachineState.FAULT_REACTION_ACTIVE if (status & 0b1111) == 0b1111 else MachineState.FAULT

#     if (status & 0b01001111) == 0b01000000:
#         return MachineState.SWITCH_ON_DISABLED

#     status &= 0b100111
#     if status == 0b100001:
#         return MachineState.READY_TO_SWITCH_ON
#     elif status == 0b100011:
#         return MachineState.SWITCHED_ON
#     elif status == 0b100111:
#         return MachineState.OPERATION_ENABLED
#     elif status == 0b000111:
#         return MachineState.QUICK_STOP
#     return MachineState.UNKNOWN


class PossibleTransitions:
    @staticmethod
    def fault_set() -> int:
        return 0b10000000000000000

    @staticmethod
    def fault_clear(control_word: int) -> int:
        return control_word & 0b10111111

    @staticmethod
    def fault_reset() -> int:
        return 0b10000000

    @staticmethod
    def shutdown() -> int:
        return 0b00000110

    @staticmethod
    def disable_voltage() -> int:
        return 0b00000000

    @staticmethod
    def switch_on() -> int:
        return 0b00000111

    @staticmethod
    def enable_operation() -> int:
        return 0b00001111

    @staticmethod
    def quick_stop() -> int:
        return 0b00000010


# def transition(current_state: MachineState, control_word: int, desired_state: DesiredState) -> int:
#     state = current_state

#     if desired_state == DesiredState.OPERATIONAL:
#         if state in {MachineState.UNKNOWN, MachineState.FAULT_REACTION_ACTIVE, MachineState.FAULT,
#                      MachineState.NOT_READY_TO_SWITCH_ON, MachineState.OPERATION_ENABLED, MachineState.QUICK_STOP}:
#             pass
#         elif state == MachineState.SWITCH_ON_DISABLED:
#             return PossibleTransitions.shutdown()
#         elif state == MachineState.READY_TO_SWITCH_ON:
#             return PossibleTransitions.switch_on()
#         elif state == MachineState.SWITCHED_ON:
#             return PossibleTransitions.enable_operation()

#     elif desired_state == DesiredState.STANDBY:
#         if state == MachineState.SWITCH_ON_DISABLED:
#             if control_word == PossibleTransitions.fault_reset():
#                 return PossibleTransitions.disable_voltage()
#         elif state == MachineState.OPERATION_ENABLED:
#             return PossibleTransitions.disable_voltage()
#         elif state == MachineState.READY_TO_SWITCH_ON:
#             return PossibleTransitions.disable_voltage()

#     elif desired_state == DesiredState.NONE:
#         if state == MachineState.SWITCH_ON_DISABLED and control_word == PossibleTransitions.fault_reset():
#             return PossibleTransitions.disable_voltage()

#     return None
