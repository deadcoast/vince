"""
Hypothesis Strategies for Vince CLI Property-Based Testing

This module provides Hypothesis strategies (generators) for generating test data
used in property-based tests across the vince CLI test suite.

Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6
"""

import string

from hypothesis import strategies as st

from vince.state.default_state import VALID_TRANSITIONS, DefaultState
from vince.state.offer_state import VALID_TRANSITIONS as OFFER_VALID_TRANSITIONS
from vince.state.offer_state import OfferState
from vince.validation.extension import SUPPORTED_EXTENSIONS
from vince.validation.offer_id import RESERVED_NAMES


# =============================================================================
# Extension Strategies (Requirements: 21.1, 21.2, 21.3)
# =============================================================================


@st.composite
def valid_extensions(draw: st.DrawFn) -> str:
    """Generate valid file extensions from the supported set.

    Returns:
        A valid extension from SUPPORTED_EXTENSIONS (e.g., ".md", ".py")
    """
    return draw(st.sampled_from(sorted(SUPPORTED_EXTENSIONS)))


@st.composite
def unsupported_extensions(draw: st.DrawFn) -> str:
    """Generate extensions that match pattern but are not supported.

    Returns:
        An unsupported extension (e.g., ".exe", ".dll", ".so")
    """
    unsupported = [".exe", ".dll", ".so", ".bin", ".dat", ".log", ".tmp", ".bak"]
    return draw(st.sampled_from(unsupported))


# =============================================================================
# Offer ID Strategies (Requirements: 21.4, 21.5, 21.6)
# =============================================================================


@st.composite
def valid_offer_ids(draw: st.DrawFn) -> str:
    """Generate valid offer IDs matching the pattern ^[a-z][a-z0-9_-]{0,31}$.

    Returns:
        A valid offer_id (e.g., "my-app", "code_editor", "vim2")
    """
    first = draw(st.sampled_from(string.ascii_lowercase))
    rest_length = draw(st.integers(min_value=0, max_value=31))
    rest = draw(
        st.text(
            alphabet=string.ascii_lowercase + string.digits + "_-",
            min_size=rest_length,
            max_size=rest_length,
        )
    )
    offer_id = first + rest

    # Ensure we don't generate reserved names
    if offer_id in RESERVED_NAMES:
        offer_id = f"custom-{offer_id}"

    return offer_id


@st.composite
def invalid_pattern_offer_ids(draw: st.DrawFn) -> str:
    """Generate offer IDs that don't match the required pattern.

    Returns:
        An invalid offer_id (e.g., "1abc", "Abc", "_abc", "abc def")
    """
    strategies = [
        st.just("1abc"),  # Starts with number
        st.just("9test"),  # Starts with number
        st.just("Abc"),  # Starts with uppercase
        st.just("ABC"),  # All uppercase
        st.just("_abc"),  # Starts with underscore
        st.just("-abc"),  # Starts with hyphen
        st.just(""),  # Empty string
        st.just("a" * 33),  # Too long (33 chars)
        st.just("abc def"),  # Contains space
        st.just("abc.def"),  # Contains dot
        st.just("abc@def"),  # Contains special char
        st.just("abc!def"),  # Contains special char
    ]
    return draw(st.one_of(*strategies))


@st.composite
def reserved_offer_names(draw: st.DrawFn) -> str:
    """Generate reserved names that cannot be used as offer IDs.

    Returns:
        A reserved name (e.g., "help", "version", "list")
    """
    return draw(st.sampled_from(sorted(RESERVED_NAMES)))


# =============================================================================
# State Transition Strategies (Requirements: 6.1, 6.2, 7.1, 7.2)
# =============================================================================


@st.composite
def valid_default_transitions(draw: st.DrawFn) -> tuple[DefaultState, DefaultState]:
    """Generate valid (current_state, target_state) pairs from VALID_TRANSITIONS.

    Returns:
        A tuple of (current_state, target_state) that is a valid transition
    """
    valid_pairs: list[tuple[DefaultState, DefaultState]] = []
    for from_state, to_states in VALID_TRANSITIONS.items():
        for to_state in to_states:
            valid_pairs.append((from_state, to_state))
    return draw(st.sampled_from(valid_pairs))


@st.composite
def invalid_default_transitions(draw: st.DrawFn) -> tuple[DefaultState, DefaultState]:
    """Generate invalid (current_state, target_state) pairs not in VALID_TRANSITIONS.

    Returns:
        A tuple of (current_state, target_state) that is an invalid transition
    """
    all_states = list(DefaultState)
    invalid_pairs: list[tuple[DefaultState, DefaultState]] = []
    for from_state in all_states:
        valid_targets = VALID_TRANSITIONS.get(from_state, set())
        for to_state in all_states:
            if to_state not in valid_targets:
                invalid_pairs.append((from_state, to_state))
    return draw(st.sampled_from(invalid_pairs))


@st.composite
def valid_offer_transitions(draw: st.DrawFn) -> tuple[OfferState, OfferState]:
    """Generate valid (current_state, target_state) pairs from OFFER_VALID_TRANSITIONS.

    Returns:
        A tuple of (current_state, target_state) that is a valid offer transition
    """
    valid_pairs: list[tuple[OfferState, OfferState]] = []
    for from_state, to_states in OFFER_VALID_TRANSITIONS.items():
        for to_state in to_states:
            valid_pairs.append((from_state, to_state))
    return draw(st.sampled_from(valid_pairs))


@st.composite
def invalid_offer_transitions(draw: st.DrawFn) -> tuple[OfferState, OfferState]:
    """Generate invalid (current_state, target_state) pairs not in OFFER_VALID_TRANSITIONS.

    Returns:
        A tuple of (current_state, target_state) that is an invalid offer transition
    """
    all_states = list(OfferState)
    invalid_pairs: list[tuple[OfferState, OfferState]] = []
    for from_state in all_states:
        valid_targets = OFFER_VALID_TRANSITIONS.get(from_state, set())
        for to_state in all_states:
            if to_state not in valid_targets:
                invalid_pairs.append((from_state, to_state))
    return draw(st.sampled_from(invalid_pairs))


# =============================================================================
# Application Path Strategies (Requirements: 21.1)
# =============================================================================


@st.composite
def valid_application_paths(draw: st.DrawFn) -> str:
    """Generate valid-looking application paths.

    Returns:
        A valid-looking application path (e.g., "/usr/bin/vim")
    """
    app_name = draw(
        st.text(
            alphabet=string.ascii_lowercase + string.digits + "_-",
            min_size=1,
            max_size=20,
        )
    )
    # Ensure app_name is not empty after filtering
    if not app_name:
        app_name = "app"
    return f"/usr/bin/{app_name}"


@st.composite
def valid_macos_app_paths(draw: st.DrawFn) -> str:
    """Generate valid-looking macOS application bundle paths.

    Returns:
        A valid-looking macOS app path (e.g., "/Applications/TextEdit.app")
    """
    app_name = draw(
        st.text(
            alphabet=string.ascii_letters + string.digits,
            min_size=1,
            max_size=20,
        )
    )
    if not app_name:
        app_name = "App"
    return f"/Applications/{app_name}.app"


# =============================================================================
# Default Entry Strategies (Requirements: 17.1, 17.3)
# =============================================================================


@st.composite
def valid_default_entries(draw: st.DrawFn) -> dict:
    """Generate valid default entry data.

    Returns:
        A dictionary representing a valid DefaultEntry
    """
    ext = draw(valid_extensions())
    app_path = draw(valid_application_paths())
    state = draw(st.sampled_from(["pending", "active"]))
    entry_num = draw(st.integers(min_value=0, max_value=999))

    return {
        "id": f"def-{ext[1:]}-{entry_num:03d}",
        "extension": ext,
        "application_path": app_path,
        "application_name": app_path.split("/")[-1],
        "state": state,
        "os_synced": state == "active",
        "created_at": "2024-01-01T00:00:00+00:00",
    }


@st.composite
def valid_active_default_entries(draw: st.DrawFn) -> dict:
    """Generate valid active default entry data.

    Returns:
        A dictionary representing a valid active DefaultEntry
    """
    ext = draw(valid_extensions())
    app_path = draw(valid_application_paths())
    entry_num = draw(st.integers(min_value=0, max_value=999))

    return {
        "id": f"def-{ext[1:]}-{entry_num:03d}",
        "extension": ext,
        "application_path": app_path,
        "application_name": app_path.split("/")[-1],
        "state": "active",
        "os_synced": True,
        "created_at": "2024-01-01T00:00:00+00:00",
    }


# =============================================================================
# Offer Entry Strategies (Requirements: 17.2, 17.4)
# =============================================================================


@st.composite
def valid_offer_entries(draw: st.DrawFn) -> dict:
    """Generate valid offer entry data.

    Returns:
        A dictionary representing a valid OfferEntry
    """
    offer_id = draw(valid_offer_ids())
    default_num = draw(st.integers(min_value=0, max_value=999))
    ext = draw(valid_extensions())
    state = draw(st.sampled_from(["created", "active"]))

    return {
        "offer_id": offer_id,
        "default_id": f"def-{ext[1:]}-{default_num:03d}",
        "state": state,
        "auto_created": draw(st.booleans()),
        "created_at": "2024-01-01T00:00:00+00:00",
    }


# =============================================================================
# Backup Testing Strategies (Requirements: 18.1, 18.2, 18.3)
# =============================================================================


@st.composite
def backup_test_params(draw: st.DrawFn) -> tuple[int, int]:
    """Generate parameters for backup retention tests.

    Returns:
        A tuple of (num_writes, max_backups) for testing backup limits
    """
    num_writes = draw(st.integers(min_value=1, max_value=10))
    max_backups = draw(st.integers(min_value=1, max_value=5))
    return (num_writes, max_backups)


# =============================================================================
# Command Parameter Strategies
# =============================================================================


@st.composite
def dry_run_commands(draw: st.DrawFn) -> str:
    """Generate command names that support the -dry flag.

    Returns:
        A command name that supports dry run (e.g., "slap", "chop")
    """
    commands_with_dry = ["slap", "chop", "set", "forget", "sync"]
    return draw(st.sampled_from(commands_with_dry))


@st.composite
def verbose_commands(draw: st.DrawFn) -> str:
    """Generate command names that support the -vb flag.

    Returns:
        A command name that supports verbose output
    """
    commands_with_verbose = [
        "slap",
        "chop",
        "set",
        "forget",
        "offer",
        "reject",
        "list",
        "sync",
    ]
    return draw(st.sampled_from(commands_with_verbose))
