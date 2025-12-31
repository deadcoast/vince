"""Offer state machine for vince CLI.

This module defines the state machine for offer entries, which represent
custom shortcuts or aliases for quick access to defaults.

States:
- none: No offer exists with the given ID
- created: Offer created but not yet used
- active: Offer has been used at least once
- rejected: Offer was rejected/removed
"""

from enum import Enum
from typing import Set

from vince.errors import OfferExistsError, OfferInUseError, OfferNotFoundError


class OfferState(Enum):
    """States for offer entries."""

    NONE = "none"
    CREATED = "created"
    ACTIVE = "active"
    REJECTED = "rejected"


# Valid transitions: from_state -> set of valid to_states
VALID_TRANSITIONS: dict[OfferState, Set[OfferState]] = {
    OfferState.NONE: {OfferState.CREATED},
    OfferState.CREATED: {OfferState.ACTIVE, OfferState.REJECTED},
    OfferState.ACTIVE: {OfferState.REJECTED},
    OfferState.REJECTED: set(),  # Terminal state - no valid transitions
}


class InvalidOfferTransitionError(Exception):
    """Raised when an invalid offer state transition is attempted."""

    def __init__(self, current: OfferState, target: OfferState, offer_id: str):
        self.current = current
        self.target = target
        self.offer_id = offer_id
        super().__init__(
            f"Invalid transition: {current.value} -> {target.value} for offer {offer_id}"
        )


def validate_transition(
    current: OfferState, target: OfferState, offer_id: str, in_use: bool = False
) -> None:
    """Validate that an offer state transition is allowed.

    Args:
        current: The current state of the offer
        target: The target state to transition to
        offer_id: The offer ID (for error messages)
        in_use: Whether the offer is currently in use (for active→rejected)

    Raises:
        OfferNotFoundError: If trying to reject when no offer exists
        OfferExistsError: If trying to create when offer already exists
        OfferInUseError: If trying to reject an active offer that is in use
        InvalidOfferTransitionError: For other invalid transitions
    """
    # Check if transition is valid
    valid_targets = VALID_TRANSITIONS.get(current, set())

    if target in valid_targets:
        # Special case: active → rejected requires offer not to be in use
        if current == OfferState.ACTIVE and target == OfferState.REJECTED and in_use:
            raise OfferInUseError(offer_id)
        return  # Transition is valid

    # Handle specific error cases
    if current == OfferState.NONE and target == OfferState.REJECTED:
        # Trying to reject when nothing exists
        raise OfferNotFoundError(offer_id)

    if (
        current in {OfferState.CREATED, OfferState.ACTIVE}
        and target == OfferState.CREATED
    ):
        # Trying to create when offer already exists
        raise OfferExistsError(offer_id)

    if current == OfferState.REJECTED:
        # Rejected is a terminal state - no transitions allowed
        raise InvalidOfferTransitionError(current, target, offer_id)

    # Generic invalid transition
    raise InvalidOfferTransitionError(current, target, offer_id)


def get_state_from_string(state_str: str) -> OfferState:
    """Convert a string to an OfferState enum value.

    Args:
        state_str: The state string (e.g., "created", "active")

    Returns:
        The corresponding OfferState enum value

    Raises:
        ValueError: If the string doesn't match any state
    """
    try:
        return OfferState(state_str.lower())
    except ValueError:
        valid_states = [s.value for s in OfferState]
        raise ValueError(f"Invalid state '{state_str}'. Valid states: {valid_states}")
