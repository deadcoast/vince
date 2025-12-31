"""Default state machine for vince CLI.

This module defines the state machine for default entries, which represent
associations between applications and file extensions.

States:
- none: No default exists for the extension
- pending: Default identified but not yet active
- active: Default is set and operational
- removed: Default was removed but record retained
"""

from enum import Enum
from typing import Set

from vince.errors import DefaultExistsError, NoDefaultError


class DefaultState(Enum):
    """States for default entries."""
    NONE = "none"
    PENDING = "pending"
    ACTIVE = "active"
    REMOVED = "removed"


# Valid transitions: from_state -> set of valid to_states
VALID_TRANSITIONS: dict[DefaultState, Set[DefaultState]] = {
    DefaultState.NONE: {DefaultState.PENDING, DefaultState.ACTIVE},
    DefaultState.PENDING: {DefaultState.ACTIVE, DefaultState.NONE},
    DefaultState.ACTIVE: {DefaultState.REMOVED},
    DefaultState.REMOVED: {DefaultState.ACTIVE},
}


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    
    def __init__(self, current: DefaultState, target: DefaultState, extension: str):
        self.current = current
        self.target = target
        self.extension = extension
        super().__init__(
            f"Invalid transition: {current.value} -> {target.value} for {extension}"
        )


def validate_transition(
    current: DefaultState, target: DefaultState, extension: str
) -> None:
    """Validate that a state transition is allowed.
    
    Args:
        current: The current state of the default
        target: The target state to transition to
        extension: The file extension (for error messages)
        
    Raises:
        NoDefaultError: If trying to remove/forget when no default exists
        DefaultExistsError: If trying to create when active default exists
        InvalidTransitionError: For other invalid transitions
    """
    # Check if transition is valid
    valid_targets = VALID_TRANSITIONS.get(current, set())
    
    if target in valid_targets:
        return  # Transition is valid
    
    # Handle specific error cases
    if current == DefaultState.NONE and target == DefaultState.REMOVED:
        # Trying to remove when nothing exists
        raise NoDefaultError(extension)
    
    if current == DefaultState.ACTIVE and target in {
        DefaultState.PENDING, DefaultState.ACTIVE
    }:
        # Trying to create when active exists
        raise DefaultExistsError(extension)
    
    if current == DefaultState.PENDING and target == DefaultState.REMOVED:
        # Pending should go to NONE, not REMOVED (just delete the entry)
        raise InvalidTransitionError(current, target, extension)
    
    # Generic invalid transition
    raise InvalidTransitionError(current, target, extension)


def get_state_from_string(state_str: str) -> DefaultState:
    """Convert a string to a DefaultState enum value.
    
    Args:
        state_str: The state string (e.g., "pending", "active")
        
    Returns:
        The corresponding DefaultState enum value
        
    Raises:
        ValueError: If the string doesn't match any state
    """
    try:
        return DefaultState(state_str.lower())
    except ValueError:
        valid_states = [s.value for s in DefaultState]
        raise ValueError(
            f"Invalid state '{state_str}'. Valid states: {valid_states}"
        )
