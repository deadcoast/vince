"""
Property-Based Tests for Vince CLI State Machines

Feature: vince-cli-implementation
Each test validates a specific correctness property from the design document.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vince.errors import DefaultExistsError, NoDefaultError
from vince.state.default_state import (VALID_TRANSITIONS, DefaultState,
                                       InvalidTransitionError,
                                       get_state_from_string,
                                       validate_transition)

# =============================================================================
# Strategies for Default State Machine
# =============================================================================


@st.composite
def valid_default_transitions(draw):
    """Generate valid (current_state, target_state) pairs from VALID_TRANSITIONS."""
    # Build list of all valid transitions
    valid_pairs = []
    for from_state, to_states in VALID_TRANSITIONS.items():
        for to_state in to_states:
            valid_pairs.append((from_state, to_state))

    return draw(st.sampled_from(valid_pairs))


@st.composite
def invalid_default_transitions(draw):
    """Generate invalid (current_state, target_state) pairs not in VALID_TRANSITIONS."""
    all_states = list(DefaultState)

    # Build list of all invalid transitions
    invalid_pairs = []
    for from_state in all_states:
        valid_targets = VALID_TRANSITIONS.get(from_state, set())
        for to_state in all_states:
            if to_state not in valid_targets:
                invalid_pairs.append((from_state, to_state))

    return draw(st.sampled_from(invalid_pairs))


@st.composite
def extensions(draw):
    """Generate valid file extensions for testing."""
    supported = [
        ".md",
        ".py",
        ".txt",
        ".js",
        ".html",
        ".css",
        ".json",
        ".yml",
        ".yaml",
        ".xml",
        ".csv",
        ".sql",
    ]
    return draw(st.sampled_from(supported))


# =============================================================================
# Property 8: Default State Transition Validity
# Validates: Requirements 5.2, 5.3
# =============================================================================


class TestDefaultStateTransitions:
    """Feature: vince-cli-implementation, Property 8: Default State Transition Validity

    *For any* default state transition, if the transition is in the VALID_TRANSITIONS
    map, validate_transition SHALL succeed. If the transition is not valid,
    validate_transition SHALL raise DefaultExistsError (for active→active) or
    NoDefaultError (for none→removed).
    """

    @given(transition=valid_default_transitions(), ext=extensions())
    @settings(max_examples=100)
    def test_valid_transitions_succeed(self, transition, ext):
        """Property: All valid transitions should succeed without raising errors."""
        current, target = transition

        # Should not raise any exception
        validate_transition(current, target, ext)

    @given(ext=extensions())
    @settings(max_examples=100)
    def test_none_to_removed_raises_no_default_error(self, ext):
        """Property: Transitioning from none to removed should raise NoDefaultError."""
        with pytest.raises(NoDefaultError) as exc_info:
            validate_transition(DefaultState.NONE, DefaultState.REMOVED, ext)

        assert exc_info.value.code == "VE302"
        assert ext in exc_info.value.message

    @given(ext=extensions())
    @settings(max_examples=100)
    def test_active_to_active_raises_default_exists_error(self, ext):
        """Property: Transitioning from active to active should raise DefaultExistsError."""
        with pytest.raises(DefaultExistsError) as exc_info:
            validate_transition(DefaultState.ACTIVE, DefaultState.ACTIVE, ext)

        assert exc_info.value.code == "VE301"
        assert ext in exc_info.value.message

    @given(ext=extensions())
    @settings(max_examples=100)
    def test_active_to_pending_raises_default_exists_error(self, ext):
        """Property: Transitioning from active to pending should raise DefaultExistsError."""
        with pytest.raises(DefaultExistsError) as exc_info:
            validate_transition(DefaultState.ACTIVE, DefaultState.PENDING, ext)

        assert exc_info.value.code == "VE301"
        assert ext in exc_info.value.message

    @given(ext=extensions())
    @settings(max_examples=100)
    def test_pending_to_removed_raises_invalid_transition(self, ext):
        """Property: Transitioning from pending to removed should raise InvalidTransitionError."""
        # Pending entries should be deleted (go to NONE), not marked as removed
        with pytest.raises(InvalidTransitionError):
            validate_transition(DefaultState.PENDING, DefaultState.REMOVED, ext)

    @given(ext=extensions())
    @settings(max_examples=100)
    def test_removed_to_pending_raises_invalid_transition(self, ext):
        """Property: Transitioning from removed to pending should raise InvalidTransitionError."""
        # Removed entries can only go back to active, not pending
        with pytest.raises(InvalidTransitionError):
            validate_transition(DefaultState.REMOVED, DefaultState.PENDING, ext)

    @given(ext=extensions())
    @settings(max_examples=100)
    def test_removed_to_none_raises_invalid_transition(self, ext):
        """Property: Transitioning from removed to none should raise InvalidTransitionError."""
        with pytest.raises(InvalidTransitionError):
            validate_transition(DefaultState.REMOVED, DefaultState.NONE, ext)

    @given(ext=extensions())
    @settings(max_examples=100)
    def test_removed_to_removed_raises_invalid_transition(self, ext):
        """Property: Transitioning from removed to removed should raise InvalidTransitionError."""
        with pytest.raises(InvalidTransitionError):
            validate_transition(DefaultState.REMOVED, DefaultState.REMOVED, ext)


class TestDefaultStateEnum:
    """Tests for DefaultState enum and helper functions."""

    def test_all_states_defined(self):
        """All expected states should be defined."""
        assert DefaultState.NONE.value == "none"
        assert DefaultState.PENDING.value == "pending"
        assert DefaultState.ACTIVE.value == "active"
        assert DefaultState.REMOVED.value == "removed"

    def test_state_count(self):
        """Should have exactly 4 states."""
        assert len(DefaultState) == 4

    @given(state=st.sampled_from(list(DefaultState)))
    @settings(max_examples=100)
    def test_get_state_from_string_roundtrip(self, state):
        """Property: Converting state to string and back should return same state."""
        result = get_state_from_string(state.value)
        assert result == state

    def test_get_state_from_string_case_insensitive(self):
        """get_state_from_string should be case insensitive."""
        assert get_state_from_string("PENDING") == DefaultState.PENDING
        assert get_state_from_string("Pending") == DefaultState.PENDING
        assert get_state_from_string("pending") == DefaultState.PENDING

    def test_get_state_from_string_invalid(self):
        """get_state_from_string should raise ValueError for invalid states."""
        with pytest.raises(ValueError) as exc_info:
            get_state_from_string("invalid")

        assert "Invalid state" in str(exc_info.value)


class TestValidTransitionsMap:
    """Tests for the VALID_TRANSITIONS mapping."""

    def test_none_can_transition_to_pending_and_active(self):
        """none state should be able to transition to pending and active."""
        assert DefaultState.PENDING in VALID_TRANSITIONS[DefaultState.NONE]
        assert DefaultState.ACTIVE in VALID_TRANSITIONS[DefaultState.NONE]

    def test_pending_can_transition_to_active_and_none(self):
        """pending state should be able to transition to active and none."""
        assert DefaultState.ACTIVE in VALID_TRANSITIONS[DefaultState.PENDING]
        assert DefaultState.NONE in VALID_TRANSITIONS[DefaultState.PENDING]

    def test_active_can_only_transition_to_removed(self):
        """active state should only be able to transition to removed."""
        assert VALID_TRANSITIONS[DefaultState.ACTIVE] == {DefaultState.REMOVED}

    def test_removed_can_only_transition_to_active(self):
        """removed state should only be able to transition to active."""
        assert VALID_TRANSITIONS[DefaultState.REMOVED] == {DefaultState.ACTIVE}


# =============================================================================
# Import Offer State Machine
# =============================================================================

from vince.errors import OfferExistsError, OfferInUseError, OfferNotFoundError
from vince.state.offer_state import \
    VALID_TRANSITIONS as OFFER_VALID_TRANSITIONS
from vince.state.offer_state import InvalidOfferTransitionError, OfferState
from vince.state.offer_state import \
    get_state_from_string as get_offer_state_from_string
from vince.state.offer_state import \
    validate_transition as validate_offer_transition

# =============================================================================
# Strategies for Offer State Machine
# =============================================================================


@st.composite
def valid_offer_transitions(draw):
    """Generate valid (current_state, target_state) pairs from OFFER_VALID_TRANSITIONS."""
    # Build list of all valid transitions
    valid_pairs = []
    for from_state, to_states in OFFER_VALID_TRANSITIONS.items():
        for to_state in to_states:
            valid_pairs.append((from_state, to_state))

    return draw(st.sampled_from(valid_pairs))


@st.composite
def invalid_offer_transitions(draw):
    """Generate invalid (current_state, target_state) pairs not in OFFER_VALID_TRANSITIONS."""
    all_states = list(OfferState)

    # Build list of all invalid transitions
    invalid_pairs = []
    for from_state in all_states:
        valid_targets = OFFER_VALID_TRANSITIONS.get(from_state, set())
        for to_state in all_states:
            if to_state not in valid_targets:
                invalid_pairs.append((from_state, to_state))

    return draw(st.sampled_from(invalid_pairs))


@st.composite
def offer_ids(draw):
    """Generate valid offer IDs for testing."""
    import string

    first = draw(st.sampled_from(string.ascii_lowercase))
    rest = draw(
        st.text(
            alphabet=string.ascii_lowercase + string.digits + "_-",
            min_size=0,
            max_size=15,
        )
    )
    return first + rest


# =============================================================================
# Property 9: Offer State Transition Validity
# Validates: Requirements 5.5, 5.6
# =============================================================================


class TestOfferStateTransitions:
    """Feature: vince-cli-implementation, Property 9: Offer State Transition Validity

    *For any* offer state transition, if the transition is in the VALID_TRANSITIONS
    map, the transition SHALL succeed. If the transition is not valid, the
    appropriate error SHALL be raised.
    """

    @given(transition=valid_offer_transitions(), offer_id=offer_ids())
    @settings(max_examples=100)
    def test_valid_transitions_succeed(self, transition, offer_id):
        """Property: All valid transitions should succeed without raising errors."""
        current, target = transition

        # Should not raise any exception (when not in use)
        validate_offer_transition(current, target, offer_id, in_use=False)

    @given(offer_id=offer_ids())
    @settings(max_examples=100)
    def test_none_to_rejected_raises_offer_not_found_error(self, offer_id):
        """Property: Transitioning from none to rejected should raise OfferNotFoundError."""
        with pytest.raises(OfferNotFoundError) as exc_info:
            validate_offer_transition(OfferState.NONE, OfferState.REJECTED, offer_id)

        assert exc_info.value.code == "VE104"
        assert offer_id in exc_info.value.message

    @given(offer_id=offer_ids())
    @settings(max_examples=100)
    def test_created_to_created_raises_offer_exists_error(self, offer_id):
        """Property: Transitioning from created to created should raise OfferExistsError."""
        with pytest.raises(OfferExistsError) as exc_info:
            validate_offer_transition(OfferState.CREATED, OfferState.CREATED, offer_id)

        assert exc_info.value.code == "VE303"
        assert offer_id in exc_info.value.message

    @given(offer_id=offer_ids())
    @settings(max_examples=100)
    def test_active_to_created_raises_offer_exists_error(self, offer_id):
        """Property: Transitioning from active to created should raise OfferExistsError."""
        with pytest.raises(OfferExistsError) as exc_info:
            validate_offer_transition(OfferState.ACTIVE, OfferState.CREATED, offer_id)

        assert exc_info.value.code == "VE303"
        assert offer_id in exc_info.value.message

    @given(offer_id=offer_ids())
    @settings(max_examples=100)
    def test_active_to_rejected_when_in_use_raises_offer_in_use_error(self, offer_id):
        """Property: Rejecting an active offer that is in use should raise OfferInUseError."""
        with pytest.raises(OfferInUseError) as exc_info:
            validate_offer_transition(
                OfferState.ACTIVE, OfferState.REJECTED, offer_id, in_use=True
            )

        assert exc_info.value.code == "VE304"
        assert offer_id in exc_info.value.message

    @given(offer_id=offer_ids())
    @settings(max_examples=100)
    def test_active_to_rejected_when_not_in_use_succeeds(self, offer_id):
        """Property: Rejecting an active offer that is not in use should succeed."""
        # Should not raise any exception
        validate_offer_transition(
            OfferState.ACTIVE, OfferState.REJECTED, offer_id, in_use=False
        )

    @given(target=st.sampled_from(list(OfferState)), offer_id=offer_ids())
    @settings(max_examples=100)
    def test_rejected_to_any_raises_invalid_transition(self, target, offer_id):
        """Property: Transitioning from rejected to any state should raise InvalidOfferTransitionError."""
        # Rejected is a terminal state
        with pytest.raises(InvalidOfferTransitionError):
            validate_offer_transition(OfferState.REJECTED, target, offer_id)

    @given(offer_id=offer_ids())
    @settings(max_examples=100)
    def test_none_to_active_raises_invalid_transition(self, offer_id):
        """Property: Transitioning from none to active should raise InvalidOfferTransitionError."""
        # Must go through created first
        with pytest.raises(InvalidOfferTransitionError):
            validate_offer_transition(OfferState.NONE, OfferState.ACTIVE, offer_id)

    @given(offer_id=offer_ids())
    @settings(max_examples=100)
    def test_created_to_none_raises_invalid_transition(self, offer_id):
        """Property: Transitioning from created to none should raise InvalidOfferTransitionError."""
        with pytest.raises(InvalidOfferTransitionError):
            validate_offer_transition(OfferState.CREATED, OfferState.NONE, offer_id)


class TestOfferStateEnum:
    """Tests for OfferState enum and helper functions."""

    def test_all_states_defined(self):
        """All expected states should be defined."""
        assert OfferState.NONE.value == "none"
        assert OfferState.CREATED.value == "created"
        assert OfferState.ACTIVE.value == "active"
        assert OfferState.REJECTED.value == "rejected"

    def test_state_count(self):
        """Should have exactly 4 states."""
        assert len(OfferState) == 4

    @given(state=st.sampled_from(list(OfferState)))
    @settings(max_examples=100)
    def test_get_state_from_string_roundtrip(self, state):
        """Property: Converting state to string and back should return same state."""
        result = get_offer_state_from_string(state.value)
        assert result == state

    def test_get_state_from_string_case_insensitive(self):
        """get_state_from_string should be case insensitive."""
        assert get_offer_state_from_string("CREATED") == OfferState.CREATED
        assert get_offer_state_from_string("Created") == OfferState.CREATED
        assert get_offer_state_from_string("created") == OfferState.CREATED

    def test_get_state_from_string_invalid(self):
        """get_state_from_string should raise ValueError for invalid states."""
        with pytest.raises(ValueError) as exc_info:
            get_offer_state_from_string("invalid")

        assert "Invalid state" in str(exc_info.value)


class TestOfferValidTransitionsMap:
    """Tests for the OFFER_VALID_TRANSITIONS mapping."""

    def test_none_can_only_transition_to_created(self):
        """none state should only be able to transition to created."""
        assert OFFER_VALID_TRANSITIONS[OfferState.NONE] == {OfferState.CREATED}

    def test_created_can_transition_to_active_and_rejected(self):
        """created state should be able to transition to active and rejected."""
        assert OfferState.ACTIVE in OFFER_VALID_TRANSITIONS[OfferState.CREATED]
        assert OfferState.REJECTED in OFFER_VALID_TRANSITIONS[OfferState.CREATED]

    def test_active_can_only_transition_to_rejected(self):
        """active state should only be able to transition to rejected."""
        assert OFFER_VALID_TRANSITIONS[OfferState.ACTIVE] == {OfferState.REJECTED}

    def test_rejected_is_terminal_state(self):
        """rejected state should have no valid transitions (terminal state)."""
        assert OFFER_VALID_TRANSITIONS[OfferState.REJECTED] == set()
