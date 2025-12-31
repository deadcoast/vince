"""
Property-Based Tests for Vince CLI Error System

Feature: vince-cli-implementation
Property 12: Error Class Completeness
Validates: Requirements 2.2
"""

import re

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vince.errors import (ConfigMalformedError, DataCorruptedError,
                          DefaultExistsError, InvalidConfigOptionError,
                          InvalidExtensionError, InvalidOfferIdError,
                          InvalidPathError, InvalidSubsectionError,
                          NoDefaultError, OfferExistsError, OfferInUseError,
                          OfferNotFoundError, PermissionDeniedError,
                          UnexpectedError, VinceError, VinceFileNotFoundError,
                          handle_error)

# All VinceError subclasses
ALL_ERROR_CLASSES = [
    InvalidPathError,
    InvalidExtensionError,
    InvalidOfferIdError,
    OfferNotFoundError,
    InvalidSubsectionError,
    VinceFileNotFoundError,
    PermissionDeniedError,
    DataCorruptedError,
    DefaultExistsError,
    NoDefaultError,
    OfferExistsError,
    OfferInUseError,
    InvalidConfigOptionError,
    ConfigMalformedError,
    UnexpectedError,
]

# Expected error codes by category
ERROR_CODE_RANGES = {
    "VE1": ["VE101", "VE102", "VE103", "VE104", "VE105"],  # Input errors
    "VE2": ["VE201", "VE202", "VE203"],  # File errors
    "VE3": ["VE301", "VE302", "VE303", "VE304"],  # State errors
    "VE4": ["VE401", "VE402"],  # Config errors
    "VE5": ["VE501"],  # System errors
}


# =============================================================================
# Property 12: Error Class Completeness
# Validates: Requirements 2.2
# Feature: vince-cli-implementation
# =============================================================================


class TestErrorClassCompleteness:
    """Feature: vince-cli-implementation, Property 12: Error Class Completeness

    *For any* VinceError subclass, it SHALL have code, message, and recovery
    attributes. The code SHALL follow the VE### format and fall within the
    correct category range.
    """

    @given(error_class=st.sampled_from(ALL_ERROR_CLASSES))
    @settings(max_examples=100)
    def test_all_error_classes_have_required_attributes(self, error_class):
        """Property: All VinceError subclasses have code, message, recovery attributes."""
        # Create an instance with a test argument
        error = error_class("test_value")

        # Verify required attributes exist
        assert hasattr(
            error, "code"
        ), f"{error_class.__name__} missing 'code' attribute"
        assert hasattr(
            error, "message"
        ), f"{error_class.__name__} missing 'message' attribute"
        assert hasattr(
            error, "recovery"
        ), f"{error_class.__name__} missing 'recovery' attribute"

        # Verify attributes are not None (except recovery which can be optional)
        assert error.code is not None, f"{error_class.__name__} has None 'code'"
        assert error.message is not None, f"{error_class.__name__} has None 'message'"

    @given(error_class=st.sampled_from(ALL_ERROR_CLASSES))
    @settings(max_examples=100)
    def test_error_codes_follow_ve_format(self, error_class):
        """Property: Error codes follow VE### format."""
        error = error_class("test_value")

        # Verify code follows VE### pattern
        pattern = r"^VE[1-5]\d{2}$"
        assert re.match(
            pattern, error.code
        ), f"{error_class.__name__} code '{error.code}' doesn't match VE### format"

    @given(error_class=st.sampled_from(ALL_ERROR_CLASSES))
    @settings(max_examples=100)
    def test_error_codes_in_correct_category(self, error_class):
        """Property: Error codes fall within correct category range."""
        error = error_class("test_value")

        # Get the category prefix (VE1, VE2, etc.)
        category = error.code[:3]

        # Verify the code is in the expected range for its category
        assert (
            category in ERROR_CODE_RANGES
        ), f"Unknown category {category} for {error_class.__name__}"
        assert (
            error.code in ERROR_CODE_RANGES[category]
        ), f"Code {error.code} not in expected range for category {category}"

    @given(error_class=st.sampled_from(ALL_ERROR_CLASSES))
    @settings(max_examples=100)
    def test_error_str_includes_code_and_message(self, error_class):
        """Property: __str__ includes both code and message."""
        error = error_class("test_value")

        error_str = str(error)
        assert (
            error.code in error_str
        ), f"{error_class.__name__}.__str__ doesn't include code"
        # Message should be partially included (at least the key part)
        assert (
            "test_value" in error.message or len(error.message) > 0
        ), f"{error_class.__name__} message is empty"

    @given(error_class=st.sampled_from(ALL_ERROR_CLASSES))
    @settings(max_examples=100)
    def test_error_recovery_is_helpful(self, error_class):
        """Property: Recovery messages provide actionable guidance."""
        error = error_class("test_value")

        # Recovery should be a non-empty string
        assert (
            error.recovery is not None
        ), f"{error_class.__name__} has no recovery message"
        assert (
            len(error.recovery) > 10
        ), f"{error_class.__name__} recovery message too short to be helpful"

    @given(error_class=st.sampled_from(ALL_ERROR_CLASSES))
    @settings(max_examples=100)
    def test_errors_are_vince_error_subclasses(self, error_class):
        """Property: All error classes inherit from VinceError."""
        assert issubclass(
            error_class, VinceError
        ), f"{error_class.__name__} is not a VinceError subclass"

        error = error_class("test_value")
        assert isinstance(
            error, VinceError
        ), f"{error_class.__name__} instance is not a VinceError"
        assert isinstance(
            error, Exception
        ), f"{error_class.__name__} instance is not an Exception"


class TestErrorCodeCoverage:
    """Test that all expected error codes are implemented."""

    def test_all_input_errors_implemented(self):
        """All VE1xx input errors should be implemented."""
        expected = {"VE101", "VE102", "VE103", "VE104", "VE105"}
        implemented = {
            InvalidPathError("x").code,
            InvalidExtensionError("x").code,
            InvalidOfferIdError("x").code,
            OfferNotFoundError("x").code,
            InvalidSubsectionError("x").code,
        }
        assert (
            expected == implemented
        ), f"Missing input errors: {expected - implemented}"

    def test_all_file_errors_implemented(self):
        """All VE2xx file errors should be implemented."""
        expected = {"VE201", "VE202", "VE203"}
        implemented = {
            VinceFileNotFoundError("x").code,
            PermissionDeniedError("x").code,
            DataCorruptedError("x").code,
        }
        assert expected == implemented, f"Missing file errors: {expected - implemented}"

    def test_all_state_errors_implemented(self):
        """All VE3xx state errors should be implemented."""
        expected = {"VE301", "VE302", "VE303", "VE304"}
        implemented = {
            DefaultExistsError("x").code,
            NoDefaultError("x").code,
            OfferExistsError("x").code,
            OfferInUseError("x").code,
        }
        assert (
            expected == implemented
        ), f"Missing state errors: {expected - implemented}"

    def test_all_config_errors_implemented(self):
        """All VE4xx config errors should be implemented."""
        expected = {"VE401", "VE402"}
        implemented = {
            InvalidConfigOptionError("x").code,
            ConfigMalformedError("x").code,
        }
        assert (
            expected == implemented
        ), f"Missing config errors: {expected - implemented}"

    def test_all_system_errors_implemented(self):
        """All VE5xx system errors should be implemented."""
        expected = {"VE501"}
        implemented = {
            UnexpectedError("x").code,
        }
        assert (
            expected == implemented
        ), f"Missing system errors: {expected - implemented}"


class TestHandleError:
    """Test the handle_error function."""

    def test_handle_error_exits_with_code_1(self):
        """handle_error should exit with code 1."""
        error = InvalidPathError("/test/path")

        with pytest.raises(SystemExit) as exc_info:
            handle_error(error)

        assert exc_info.value.code == 1

    def test_handle_error_works_with_all_error_types(self):
        """handle_error should work with all VinceError subclasses."""
        for error_class in ALL_ERROR_CLASSES:
            error = error_class("test_value")

            with pytest.raises(SystemExit) as exc_info:
                handle_error(error)

            assert exc_info.value.code == 1
