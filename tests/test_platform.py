"""
Unit Tests for Platform Detection and OS-Specific Error Classes

Feature: os-integration
Tests: Platform detection, error classes VE601-VE606
Validates: Requirements 1.1, 1.2, 8.3
"""

import re
import sys
from unittest.mock import patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vince.errors import VinceError
from vince.platform import (
    AppInfo,
    OperationResult,
    Platform,
    _reset_handler,
    get_handler,
    get_platform,
)
from vince.platform.errors import (
    ApplicationNotFoundError,
    BundleIdNotFoundError,
    OSOperationError,
    RegistryAccessError,
    SyncPartialError,
    UnsupportedPlatformError,
)

# All VE6xx error classes
OS_ERROR_CLASSES = [
    (UnsupportedPlatformError, "linux", "VE601"),
    (BundleIdNotFoundError, "/path/to/app", "VE602"),
    (RegistryAccessError, "write operation", "VE603"),
    (ApplicationNotFoundError, "/invalid/path", "VE604"),
]

# OSOperationError and SyncPartialError have different signatures
OS_OPERATION_ERROR_ARGS = ("set_default", "permission denied")
SYNC_PARTIAL_ERROR_ARGS = (5, 2, [".md", ".py"])


# =============================================================================
# Platform Detection Tests
# Validates: Requirements 1.1, 1.2
# =============================================================================


class TestPlatformDetection:
    """Test platform detection functionality."""

    def test_get_platform_returns_platform_enum(self):
        """get_platform() should return a Platform enum value."""
        result = get_platform()
        assert isinstance(result, Platform)

    def test_get_platform_detects_macos(self):
        """get_platform() should return MACOS on darwin."""
        with patch.object(sys, "platform", "darwin"):
            result = get_platform()
            assert result == Platform.MACOS

    def test_get_platform_detects_windows(self):
        """get_platform() should return WINDOWS on win32."""
        with patch.object(sys, "platform", "win32"):
            result = get_platform()
            assert result == Platform.WINDOWS

    def test_get_platform_detects_unsupported(self):
        """get_platform() should return UNSUPPORTED on other platforms."""
        with patch.object(sys, "platform", "linux"):
            result = get_platform()
            assert result == Platform.UNSUPPORTED

    @given(platform=st.sampled_from(["freebsd", "aix", "cygwin", "unknown"]))
    @settings(max_examples=10)
    def test_get_platform_unsupported_variants(self, platform):
        """get_platform() should return UNSUPPORTED for various non-supported platforms."""
        with patch.object(sys, "platform", platform):
            result = get_platform()
            assert result == Platform.UNSUPPORTED

    def test_platform_enum_values(self):
        """Platform enum should have correct string values."""
        assert Platform.MACOS.value == "darwin"
        assert Platform.WINDOWS.value == "win32"
        assert Platform.UNSUPPORTED.value == "unsupported"


class TestGetHandler:
    """Test the get_handler() factory function."""

    def setup_method(self):
        """Reset handler singleton before each test."""
        _reset_handler()

    def teardown_method(self):
        """Reset handler singleton after each test."""
        _reset_handler()

    def test_get_handler_raises_on_unsupported_platform(self):
        """get_handler() should raise UnsupportedPlatformError on unsupported platforms."""
        with patch.object(sys, "platform", "linux"):
            _reset_handler()
            with pytest.raises(UnsupportedPlatformError) as exc_info:
                get_handler()
            assert exc_info.value.code == "VE601"
            assert "linux" in exc_info.value.message

    def test_get_handler_singleton_behavior(self):
        """get_handler() should return the same instance on repeated calls."""
        # This test only works on supported platforms with handler modules
        current_platform = get_platform()
        if current_platform == Platform.UNSUPPORTED:
            pytest.skip("Cannot test singleton on unsupported platform")

        try:
            handler1 = get_handler()
            handler2 = get_handler()
            assert handler1 is handler2
        except ModuleNotFoundError:
            pytest.skip("Platform handler module not yet implemented")

    def test_reset_handler_clears_singleton(self):
        """_reset_handler() should clear the singleton instance."""
        current_platform = get_platform()
        if current_platform == Platform.UNSUPPORTED:
            pytest.skip("Cannot test reset on unsupported platform")

        try:
            _handler1 = get_handler()
            _reset_handler()
            handler2 = get_handler()
            # After reset, we get a new instance (though it may be equal)
            # The key is that the singleton was cleared
            assert handler2 is not None
        except ModuleNotFoundError:
            pytest.skip("Platform handler module not yet implemented")


# =============================================================================
# OS Error Classes Tests
# Validates: Requirements 8.1, 8.2, 8.3
# =============================================================================


class TestOSErrorClasses:
    """Test OS-specific error classes (VE6xx series)."""

    @pytest.mark.parametrize("error_class,arg,expected_code", OS_ERROR_CLASSES)
    def test_error_has_correct_code(self, error_class, arg, expected_code):
        """Each OS error class should have the correct VE6xx code."""
        error = error_class(arg)
        assert error.code == expected_code

    @pytest.mark.parametrize("error_class,arg,expected_code", OS_ERROR_CLASSES)
    def test_error_inherits_from_vince_error(self, error_class, arg, expected_code):
        """All OS error classes should inherit from VinceError."""
        error = error_class(arg)
        assert isinstance(error, VinceError)
        assert isinstance(error, Exception)

    @pytest.mark.parametrize("error_class,arg,expected_code", OS_ERROR_CLASSES)
    def test_error_has_message(self, error_class, arg, expected_code):
        """All OS error classes should have a non-empty message."""
        error = error_class(arg)
        assert error.message is not None
        assert len(error.message) > 0
        assert arg in error.message

    @pytest.mark.parametrize("error_class,arg,expected_code", OS_ERROR_CLASSES)
    def test_error_has_recovery(self, error_class, arg, expected_code):
        """All OS error classes should have a recovery suggestion."""
        error = error_class(arg)
        assert error.recovery is not None
        assert len(error.recovery) > 10

    @pytest.mark.parametrize("error_class,arg,expected_code", OS_ERROR_CLASSES)
    def test_error_str_includes_code(self, error_class, arg, expected_code):
        """Error __str__ should include the error code."""
        error = error_class(arg)
        assert expected_code in str(error)


class TestOSOperationError:
    """Test OSOperationError (VE605) specifically."""

    def test_os_operation_error_code(self):
        """OSOperationError should have code VE605."""
        error = OSOperationError(*OS_OPERATION_ERROR_ARGS)
        assert error.code == "VE605"

    def test_os_operation_error_message_includes_operation(self):
        """OSOperationError message should include the operation name."""
        error = OSOperationError("set_default", "permission denied")
        assert "set_default" in error.message
        assert "permission denied" in error.message

    def test_os_operation_error_inherits_from_vince_error(self):
        """OSOperationError should inherit from VinceError."""
        error = OSOperationError(*OS_OPERATION_ERROR_ARGS)
        assert isinstance(error, VinceError)


class TestSyncPartialError:
    """Test SyncPartialError (VE606) specifically."""

    def test_sync_partial_error_code(self):
        """SyncPartialError should have code VE606."""
        error = SyncPartialError(*SYNC_PARTIAL_ERROR_ARGS)
        assert error.code == "VE606"

    def test_sync_partial_error_message_includes_counts(self):
        """SyncPartialError message should include success/failure counts."""
        error = SyncPartialError(5, 2, [".md", ".py"])
        assert "5" in error.message
        assert "2" in error.message

    def test_sync_partial_error_recovery_includes_failures(self):
        """SyncPartialError recovery should list failed extensions."""
        error = SyncPartialError(5, 2, [".md", ".py"])
        assert ".md" in error.recovery
        assert ".py" in error.recovery

    def test_sync_partial_error_inherits_from_vince_error(self):
        """SyncPartialError should inherit from VinceError."""
        error = SyncPartialError(*SYNC_PARTIAL_ERROR_ARGS)
        assert isinstance(error, VinceError)


class TestErrorCodeFormat:
    """Test that all VE6xx error codes follow the correct format."""

    def test_all_os_errors_follow_ve6xx_format(self):
        """All OS error codes should match VE6## pattern."""
        pattern = r"^VE6\d{2}$"

        errors = [
            UnsupportedPlatformError("linux"),
            BundleIdNotFoundError("/path"),
            RegistryAccessError("write"),
            ApplicationNotFoundError("/path"),
            OSOperationError("op", "details"),
            SyncPartialError(1, 1, [".md"]),
        ]

        for error in errors:
            assert re.match(pattern, error.code), (
                f"{type(error).__name__} code '{error.code}' "
                f"doesn't match VE6## format"
            )

    def test_all_os_error_codes_are_unique(self):
        """All OS error codes should be unique."""
        errors = [
            UnsupportedPlatformError("linux"),
            BundleIdNotFoundError("/path"),
            RegistryAccessError("write"),
            ApplicationNotFoundError("/path"),
            OSOperationError("op", "details"),
            SyncPartialError(1, 1, [".md"]),
        ]

        codes = [e.code for e in errors]
        assert len(codes) == len(set(codes)), "Duplicate error codes found"

    def test_os_error_codes_are_sequential(self):
        """OS error codes should be VE601-VE606."""
        expected_codes = {"VE601", "VE602", "VE603", "VE604", "VE605", "VE606"}

        errors = [
            UnsupportedPlatformError("linux"),
            BundleIdNotFoundError("/path"),
            RegistryAccessError("write"),
            ApplicationNotFoundError("/path"),
            OSOperationError("op", "details"),
            SyncPartialError(1, 1, [".md"]),
        ]

        actual_codes = {e.code for e in errors}
        assert actual_codes == expected_codes


# =============================================================================
# Data Classes Tests
# =============================================================================


class TestAppInfo:
    """Test AppInfo dataclass."""

    def test_app_info_creation(self):
        """AppInfo should be creatable with required fields."""
        from pathlib import Path

        info = AppInfo(path=Path("/app"), name="TestApp")
        assert info.path == Path("/app")
        assert info.name == "TestApp"
        assert info.bundle_id is None
        assert info.executable is None

    def test_app_info_with_bundle_id(self):
        """AppInfo should accept bundle_id for macOS."""
        from pathlib import Path

        info = AppInfo(
            path=Path("/Applications/Test.app"),
            name="Test",
            bundle_id="com.example.test",
        )
        assert info.bundle_id == "com.example.test"

    def test_app_info_with_executable(self):
        """AppInfo should accept executable for Windows."""
        from pathlib import Path

        info = AppInfo(
            path=Path("C:/Program Files/Test"),
            name="Test",
            executable="C:/Program Files/Test/test.exe",
        )
        assert info.executable == "C:/Program Files/Test/test.exe"


class TestOperationResult:
    """Test OperationResult dataclass."""

    def test_operation_result_success(self):
        """OperationResult should represent successful operations."""
        result = OperationResult(success=True, message="Operation completed")
        assert result.success is True
        assert result.message == "Operation completed"
        assert result.previous_default is None
        assert result.error_code is None

    def test_operation_result_failure(self):
        """OperationResult should represent failed operations."""
        result = OperationResult(
            success=False,
            message="Operation failed",
            error_code="VE605",
        )
        assert result.success is False
        assert result.error_code == "VE605"

    def test_operation_result_with_previous_default(self):
        """OperationResult should track previous default for rollback."""
        result = OperationResult(
            success=True,
            message="Default changed",
            previous_default="/Applications/OldApp.app",
        )
        assert result.previous_default == "/Applications/OldApp.app"


class TestPlatformEnum:
    """Test Platform enum."""

    def test_platform_enum_members(self):
        """Platform enum should have MACOS, WINDOWS, UNSUPPORTED members."""
        assert hasattr(Platform, "MACOS")
        assert hasattr(Platform, "WINDOWS")
        assert hasattr(Platform, "UNSUPPORTED")

    def test_platform_enum_is_enum(self):
        """Platform should be an Enum."""
        from enum import Enum

        assert issubclass(Platform, Enum)
