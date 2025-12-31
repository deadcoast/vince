"""Vince CLI state machines.

This module provides state machine implementations for managing the lifecycle
of defaults and offers in the vince CLI.
"""

from vince.state.default_state import (
    DefaultState,
    VALID_TRANSITIONS as DEFAULT_VALID_TRANSITIONS,
    validate_transition as validate_default_transition,
    get_state_from_string as get_default_state_from_string,
    InvalidTransitionError,
)
from vince.state.offer_state import (
    OfferState,
    VALID_TRANSITIONS as OFFER_VALID_TRANSITIONS,
    validate_transition as validate_offer_transition,
    get_state_from_string as get_offer_state_from_string,
    InvalidOfferTransitionError,
)

__all__ = [
    # Default state machine
    "DefaultState",
    "DEFAULT_VALID_TRANSITIONS",
    "validate_default_transition",
    "get_default_state_from_string",
    "InvalidTransitionError",
    # Offer state machine
    "OfferState",
    "OFFER_VALID_TRANSITIONS",
    "validate_offer_transition",
    "get_offer_state_from_string",
    "InvalidOfferTransitionError",
]
