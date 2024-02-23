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
            return (control_word & 0b11111111) | 0b10000000  # automatic reset
        else:
            return control_word
    else:
        return control_word
