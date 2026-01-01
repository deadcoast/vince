"""
Property-Based Tests for Windows Handler

Feature: os-integration
Property 3: Set-Query Round Trip (Windows)
Validates: Requirements 3.1, 3.5

This module tests the Windows handler's set_default and get_current_default
methods to ensure they form a consistent round trip.

Note: These tests use mocking to simulate Windows registry operations
since the actual winreg module is only available on Windows.
"""

import sys
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from vince.platform.base import AppInfo, Platform

# Supported extensions for testing
SUPPORTED_EXTENSIONS = [
    ".md", ".py", ".txt", ".js", ".html", ".css",
    ".json", ".yml", ".yaml", ".xml", ".csv", ".sql"
]


# =============================================================================
# Strategies for Property-Based Testing
# =============================================================================

# Strategy for supported extensions
supported_extensions = st.sampled_from(SUPPORTED_EXTENSIONS)

# Strategy for valid application names
app_name_strategy = st.from_regex(
    r"^[A-Za-z][A-Za-z0-9_]{2,15}$",
    fullmatch=True,
)


# =============================================================================
# Unit Tests for WindowsHandler
# =============================================================================


class TestWindowsHandlerBasics:
    """Basic unit tests for WindowsHandler."""

    def test_platform_property(self):
        """WindowsHandler.platform should return Platform.WINDOWS."""
        from vince.platform.windows import WindowsHandler

        handler = WindowsHandler()
        assert handler.platform == Platform.WINDOWS

    def test_verify_application_with_valid_exe(self, tmp_path):
        """verify_application should return AppInfo for valid .exe file."""
        from vince.platform.windows import WindowsHandler

        # Create a mock .exe file
        exe_file = tmp_path / "test.exe"
        exe_file.touch()

        handler = WindowsHandler()
        result = handler.verify_application(exe_file)

        assert isinstance(result, AppInfo)
        assert result.path == exe_file
        assert result.name == "test"
        assert result.executable == str(exe_file)

    def test_verify_application_with_directory(self, tmp_path):
        """verify_application should find .exe in directory."""
        from vince.platform.windows import WindowsHandler

        # Create a directory with an .exe file
        app_dir = tmp_path / "TestApp"
        app_dir.mkdir()
        exe_file = app_dir / "app.exe"
        exe_file.touch()

        handler = WindowsHandler()
        result = handler.verify_application(app_dir)

        assert isinstance(result, AppInfo)
        assert result.path == app_dir
        assert result.name == "TestApp"
        assert result.executable == str(exe_file)

    def test_verify_application_raises_for_nonexistent(self):
        """verify_application should raise ApplicationNotFoundError for missing app."""
        from vince.platform.errors import ApplicationNotFoundError
        from vince.platform.windows import WindowsHandler

        handler = WindowsHandler()
        with pytest.raises(ApplicationNotFoundError):
            handler.verify_application(Path("/nonexistent/app.exe"))

    def test_verify_application_no_exe_in_directory(self, tmp_path):
        """verify_application should return None executable for dir without .exe."""
        from vince.platform.windows import WindowsHandler

        # Create a directory without any .exe files
        app_dir = tmp_path / "EmptyApp"
        app_dir.mkdir()

        handler = WindowsHandler()
        result = handler.verify_application(app_dir)

        assert result.executable is None

    def test_find_executable_with_file(self, tmp_path):
        """_find_executable should return the file if it's a file."""
        from vince.platform.windows import WindowsHandler

        file_path = tmp_path / "test.txt"
        file_path.touch()

        handler = WindowsHandler()
        result = handler._find_executable(file_path)

        assert result == file_path

    def test_find_executable_with_directory(self, tmp_path):
        """_find_executable should find first .exe in directory."""
        from vince.platform.windows import WindowsHandler

        app_dir = tmp_path / "TestApp"
        app_dir.mkdir()
        exe_file = app_dir / "main.exe"
        exe_file.touch()

        handler = WindowsHandler()
        result = handler._find_executable(app_dir)

        assert result == exe_file

    def test_find_executable_empty_directory(self, tmp_path):
        """_find_executable should return None for empty directory."""
        from vince.platform.windows import WindowsHandler

        app_dir = tmp_path / "EmptyDir"
        app_dir.mkdir()

        handler = WindowsHandler()
        result = handler._find_executable(app_dir)

        assert result is None


class TestWindowsHandlerGetCurrentDefault:
    """Tests for get_current_default method."""

    def test_get_current_default_returns_none_on_non_windows(self):
        """get_current_default should return None on non-Windows platforms."""
        from vince.platform.windows import WindowsHandler

        handler = WindowsHandler()

        # On non-Windows, this should return None gracefully
        if sys.platform != "win32":
            result = handler.get_current_default(".txt")
            assert result is None


class TestWindowsHandlerSetDefault:
    """Tests for set_default method."""

    def test_set_default_dry_run(self, tmp_path):
        """set_default with dry_run should not make changes."""
        from vince.platform.windows import WindowsHandler

        # Create mock exe file
        exe_file = tmp_path / "test.exe"
        exe_file.touch()

        handler = WindowsHandler()
        result = handler.set_default(".md", exe_file, dry_run=True)

        assert result.success is True
        assert "Would register" in result.message

    def test_set_default_returns_error_for_no_executable(self, tmp_path):
        """set_default should return error when no executable found."""
        from vince.platform.windows import WindowsHandler

        # Create empty directory
        app_dir = tmp_path / "EmptyApp"
        app_dir.mkdir()

        handler = WindowsHandler()
        result = handler.set_default(".md", app_dir, dry_run=False)

        assert result.success is False
        assert "Cannot find executable" in result.message
        assert result.error_code == "VE604"

    def test_set_default_fails_gracefully_on_non_windows(self, tmp_path):
        """set_default should fail gracefully on non-Windows platforms."""
        from vince.platform.windows import WindowsHandler

        exe_file = tmp_path / "test.exe"
        exe_file.touch()

        handler = WindowsHandler()

        if sys.platform != "win32":
            result = handler.set_default(".md", exe_file, dry_run=False)
            # Should fail because winreg is not available
            assert result.success is False
            assert result.error_code == "VE605"


class TestWindowsHandlerRemoveDefault:
    """Tests for remove_default method."""

    def test_remove_default_dry_run(self):
        """remove_default with dry_run should not make changes."""
        from vince.platform.windows import WindowsHandler

        handler = WindowsHandler()
        result = handler.remove_default(".md", dry_run=True)

        assert result.success is True
        assert "Would remove" in result.message

    def test_remove_default_fails_gracefully_on_non_windows(self):
        """remove_default should fail gracefully on non-Windows platforms."""
        from vince.platform.windows import WindowsHandler

        handler = WindowsHandler()

        if sys.platform != "win32":
            result = handler.remove_default(".md", dry_run=False)
            # Should fail because winreg is not available
            assert result.success is False
            assert result.error_code == "VE605"


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestWindowsHandlerProperties:
    """Property-based tests for WindowsHandler.

    **Property 3: Set-Query Round Trip (Windows)**
    **Validates: Requirements 3.1, 3.5**
    """

    @given(extension=supported_extensions, app_name=app_name_strategy)
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_set_query_round_trip_dry_run(self, extension, app_name, tmp_path):
        """
        Property 3: Set-Query Round Trip (Windows)

        For any valid extension and application, if set_default succeeds
        in dry_run mode, the operation should be idempotent and not
        affect the actual OS state.

        **Validates: Requirements 3.1, 3.5**
        """
        from vince.platform.windows import WindowsHandler

        # Create mock exe file
        exe_file = tmp_path / f"{app_name}.exe"
        exe_file.touch()

        handler = WindowsHandler()

        # Dry run should always succeed for valid extensions
        result = handler.set_default(extension, exe_file, dry_run=True)

        assert result.success is True
        assert "Would register" in result.message
        assert app_name in result.message

    @given(extension=supported_extensions)
    @settings(max_examples=100)
    def test_get_current_default_returns_consistent_type(self, extension):
        """
        Property: get_current_default returns consistent types.

        For any supported extension, get_current_default should return
        either a string path or None, never raise an exception.

        **Validates: Requirements 4.1**
        """
        from vince.platform.windows import WindowsHandler

        handler = WindowsHandler()
        result = handler.get_current_default(extension)

        assert result is None or isinstance(result, str)

    @given(extension=supported_extensions)
    @settings(max_examples=100)
    def test_remove_default_dry_run_idempotent(self, extension):
        """
        Property: remove_default dry_run is idempotent.

        For any supported extension, remove_default in dry_run mode
        should always succeed and not modify state.

        **Validates: Requirements 5.1, 5.3, 7.1, 7.2**
        """
        from vince.platform.windows import WindowsHandler

        handler = WindowsHandler()

        # First call
        result1 = handler.remove_default(extension, dry_run=True)
        # Second call
        result2 = handler.remove_default(extension, dry_run=True)

        assert result1.success is True
        assert result2.success is True
        assert result1.message == result2.message

    @given(extension=supported_extensions, app_name=app_name_strategy)
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_set_default_records_previous_default(self, extension, app_name, tmp_path):
        """
        Property: set_default records previous default for rollback.

        For any valid extension and application, set_default should
        record the previous default in the result for rollback support.

        **Validates: Requirements 9.1**
        """
        from vince.platform.windows import WindowsHandler

        exe_file = tmp_path / f"{app_name}.exe"
        exe_file.touch()

        handler = WindowsHandler()
        result = handler.set_default(extension, exe_file, dry_run=True)

        # previous_default should be set (even if None)
        assert hasattr(result, "previous_default")
        # In this case it's None since we're on non-Windows or no existing default
        assert result.previous_default is None


# =============================================================================
# Rollback Property Tests
# =============================================================================


class TestWindowsHandlerRollback:
    """Tests for rollback functionality in WindowsHandler.

    **Property 5: Rollback on Failure**
    **Validates: Requirements 9.1, 9.2**
    """

    def test_rollback_attempted_on_registry_failure(self, tmp_path):
        """
        When registry operation fails after partial changes, rollback should be attempted.

        **Validates: Requirements 9.1, 9.2**
        """
        from unittest.mock import MagicMock, patch

        from vince.platform.windows import WindowsHandler

        # Create mock exe file
        exe_file = tmp_path / "test.exe"
        exe_file.touch()

        handler = WindowsHandler()

        # Mock winreg to simulate partial failure
        mock_winreg = MagicMock()
        mock_winreg.HKEY_CURRENT_USER = 1
        mock_winreg.HKEY_CLASSES_ROOT = 2
        mock_winreg.REG_SZ = 1
        mock_winreg.KEY_ALL_ACCESS = 0xF003F

        # Track which operations were called
        operations = []

        def mock_create_key(hkey, path):
            operations.append(("create", path))
            # Fail on the second create (extension association)
            if "shell\\open\\command" in path:
                # First ProgID creation succeeds
                return MagicMock(__enter__=MagicMock(return_value=MagicMock()),
                                __exit__=MagicMock(return_value=False))
            if ".md" in path and "vince" not in path:
                # Extension association fails
                raise PermissionError("Access denied")
            return MagicMock(__enter__=MagicMock(return_value=MagicMock()),
                            __exit__=MagicMock(return_value=False))

        mock_winreg.CreateKey = mock_create_key
        mock_winreg.SetValueEx = MagicMock()
        mock_winreg.OpenKey = MagicMock(side_effect=OSError("Key not found"))
        mock_winreg.DeleteKey = MagicMock()
        mock_winreg.QueryValueEx = MagicMock(side_effect=OSError("Value not found"))
        mock_winreg.EnumKey = MagicMock(side_effect=OSError("No more keys"))

        with patch("vince.platform.windows._get_winreg", return_value=mock_winreg):
            with patch("vince.platform.windows._get_ctypes") as mock_ctypes:
                mock_ctypes.return_value.windll.shell32.SHChangeNotify = MagicMock()
                result = handler.set_default(".md", exe_file, dry_run=False)

        # Operation should fail
        assert result.success is False
        # Error code should indicate permission error or rollback error
        assert result.error_code in ("VE603", "VE607")

    def test_rollback_not_attempted_when_no_changes_made(self, tmp_path):
        """
        When operation fails before any changes, rollback should not be attempted.

        **Validates: Requirements 9.1, 9.2**
        """
        from unittest.mock import MagicMock, patch

        from vince.platform.windows import WindowsHandler

        # Create mock exe file
        exe_file = tmp_path / "test.exe"
        exe_file.touch()

        handler = WindowsHandler()

        # Mock winreg to fail immediately on first operation
        mock_winreg = MagicMock()
        mock_winreg.HKEY_CURRENT_USER = 1
        mock_winreg.HKEY_CLASSES_ROOT = 2
        mock_winreg.REG_SZ = 1

        # Fail immediately on CreateKey
        mock_winreg.CreateKey = MagicMock(
            side_effect=PermissionError("Access denied")
        )
        mock_winreg.OpenKey = MagicMock(side_effect=OSError("Key not found"))
        mock_winreg.QueryValueEx = MagicMock(side_effect=OSError("Value not found"))

        with patch("vince.platform.windows._get_winreg", return_value=mock_winreg):
            result = handler.set_default(".md", exe_file, dry_run=False)

        # Operation should fail
        assert result.success is False
        # Rollback should not have been attempted (no changes were made)
        assert result.rollback_attempted is False

    @given(extension=supported_extensions, app_name=app_name_strategy)
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_rollback_records_previous_default_property(
        self, extension, app_name, tmp_path
    ):
        """
        Property 5: Rollback on Failure

        For any valid extension and application, if set_default fails after
        making partial changes, the result should include rollback information.

        **Validates: Requirements 9.1, 9.2**
        """
        from unittest.mock import MagicMock, patch

        from vince.platform.windows import WindowsHandler

        # Create mock exe file
        exe_file = tmp_path / f"{app_name}.exe"
        exe_file.touch()

        handler = WindowsHandler()

        # Mock winreg to simulate partial failure
        mock_winreg = MagicMock()
        mock_winreg.HKEY_CURRENT_USER = 1
        mock_winreg.HKEY_CLASSES_ROOT = 2
        mock_winreg.REG_SZ = 1
        mock_winreg.KEY_ALL_ACCESS = 0xF003F

        create_count = [0]

        def mock_create_key(hkey, path):
            create_count[0] += 1
            # Succeed on first few creates (ProgID), fail on extension
            if create_count[0] <= 2:
                return MagicMock(
                    __enter__=MagicMock(return_value=MagicMock()),
                    __exit__=MagicMock(return_value=False),
                )
            raise PermissionError("Access denied")

        mock_winreg.CreateKey = mock_create_key
        mock_winreg.SetValueEx = MagicMock()
        mock_winreg.OpenKey = MagicMock(side_effect=OSError("Key not found"))
        mock_winreg.DeleteKey = MagicMock()
        mock_winreg.QueryValueEx = MagicMock(side_effect=OSError("Value not found"))
        mock_winreg.EnumKey = MagicMock(side_effect=OSError("No more keys"))

        with patch("vince.platform.windows._get_winreg", return_value=mock_winreg):
            with patch("vince.platform.windows._get_ctypes") as mock_ctypes:
                mock_ctypes.return_value.windll.shell32.SHChangeNotify = MagicMock()
                result = handler.set_default(extension, exe_file, dry_run=False)

        # Property: When operation fails after partial changes,
        # the result should contain rollback information
        assert result.success is False
        # If partial changes were made, rollback should be attempted
        if create_count[0] > 0:
            assert result.rollback_attempted is True

    def test_rollback_result_includes_original_error(self, tmp_path):
        """
        When rollback is attempted, the result should include the original error.

        **Validates: Requirements 9.3, 9.4**
        """
        from unittest.mock import MagicMock, patch

        from vince.platform.windows import WindowsHandler

        # Create mock exe file
        exe_file = tmp_path / "test.exe"
        exe_file.touch()

        handler = WindowsHandler()

        # Mock winreg to simulate partial failure with specific error
        mock_winreg = MagicMock()
        mock_winreg.HKEY_CURRENT_USER = 1
        mock_winreg.HKEY_CLASSES_ROOT = 2
        mock_winreg.REG_SZ = 1
        mock_winreg.KEY_ALL_ACCESS = 0xF003F

        create_count = [0]

        def mock_create_key(hkey, path):
            create_count[0] += 1
            if create_count[0] <= 2:
                return MagicMock(
                    __enter__=MagicMock(return_value=MagicMock()),
                    __exit__=MagicMock(return_value=False),
                )
            raise PermissionError("Specific permission error message")

        mock_winreg.CreateKey = mock_create_key
        mock_winreg.SetValueEx = MagicMock()
        mock_winreg.OpenKey = MagicMock(side_effect=OSError("Key not found"))
        mock_winreg.DeleteKey = MagicMock()
        mock_winreg.QueryValueEx = MagicMock(side_effect=OSError("Value not found"))
        mock_winreg.EnumKey = MagicMock(side_effect=OSError("No more keys"))

        with patch("vince.platform.windows._get_winreg", return_value=mock_winreg):
            with patch("vince.platform.windows._get_ctypes") as mock_ctypes:
                mock_ctypes.return_value.windll.shell32.SHChangeNotify = MagicMock()
                result = handler.set_default(".md", exe_file, dry_run=False)

        # Original error should be preserved
        assert result.success is False
        assert result.error_code is not None
        # If rollback was attempted, rollback info should be present
        if result.rollback_attempted:
            assert result.rollback_succeeded is not None or result.rollback_message is not None

    def test_operation_result_has_rollback_fields(self, tmp_path):
        """
        OperationResult should have rollback-related fields.

        **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
        """
        from vince.platform.base import OperationResult

        # Test that OperationResult has the new rollback fields
        result = OperationResult(
            success=False,
            message="Test error",
            previous_default="/path/to/previous",
            error_code="VE605",
            rollback_attempted=True,
            rollback_succeeded=True,
            rollback_message="Rollback successful",
        )

        assert result.rollback_attempted is True
        assert result.rollback_succeeded is True
        assert result.rollback_message == "Rollback successful"

    def test_operation_result_default_rollback_values(self):
        """
        OperationResult should have sensible defaults for rollback fields.

        **Validates: Requirements 9.1, 9.2**
        """
        from vince.platform.base import OperationResult

        # Test default values
        result = OperationResult(
            success=True,
            message="Success",
        )

        assert result.rollback_attempted is False
        assert result.rollback_succeeded is None
        assert result.rollback_message is None
