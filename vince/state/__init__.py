"""Vince CLI state machines.

This module provides state machine implementations for managing the lifecycle
of defaults and offers in the vince CLI.
"""

from vince.state.default_state import \
    VALID_TRANSITIONS as DEFAULT_VALID_TRANSITIONS
from vince.state.default_state import DefaultState, InvalidTransitionError
from vince.state.default_state import \
    get_state_from_string as get_default_state_from_string
from vince.state.default_state import \
    validate_transition as validate_default_transition
from vince.state.offer_state import \
    VALID_TRANSITIONS as OFFER_VALID_TRANSITIONS
from vince.state.offer_state import InvalidOfferTransitionError, OfferState
from vince.state.offer_state import \
    get_state_from_string as get_offer_state_from_string
from vince.state.offer_state import \
    validate_transition as validate_offer_transition

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
