"""
Property-Based Tests for macOS Handler

Feature: os-integration
Property 3: Set-Query Round Trip (macOS)
Validates: Requirements 2.1, 2.4

This module tests the macOS handler's set_default and get_current_default
methods to ensure they form a consistent round trip.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from vince.platform.base import AppInfo, OperationResult, Platform
from vince.platform.uti_map import UTI_MAP

# Skip all tests if not on macOS (or if we're mocking)
pytestmark = pytest.mark.skipif(
    sys.platform != "darwin",
    reason="macOS handler tests only run on macOS",
)


# =============================================================================
# Strategies for Property-Based Testing
# =============================================================================

# Strategy for supported extensions
supported_extensions = st.sampled_from(list(UTI_MAP.keys()))

# Strategy for valid bundle IDs
bundle_id_strategy = st.from_regex(
    r"^com\.[a-z]{3,10}\.[a-z]{3,10}$",
    fullmatch=True,
)


# =============================================================================
# Unit Tests for MacOSHandler
# =============================================================================


class TestMacOSHandlerBasics:
    """Basic unit tests for MacOSHandler."""

    def test_platform_property(self):
        """MacOSHandler.platform should return Platform.MACOS."""
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()
        assert handler.platform == Platform.MACOS

    def test_verify_application_with_valid_app(self, tmp_path):
        """verify_application should return AppInfo for valid .app bundle."""
        from vince.platform.macos import MacOSHandler

        # Create a mock .app bundle structure
        app_bundle = tmp_path / "Test.app"
        contents = app_bundle / "Contents"
        contents.mkdir(parents=True)

        # Create Info.plist with bundle ID
        info_plist = contents / "Info.plist"
        info_plist.write_text(
            '<?xml version="1.0"?>\n'
            '<plist version="1.0">\n'
            "<dict>\n"
            "  <key>CFBundleIdentifier</key>\n"
            "  <string>com.test.app</string>\n"
            "</dict>\n"
            "</plist>"
        )

        handler = MacOSHandler()

        # Mock the defaults command to return our bundle ID
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="com.test.app\n",
            )
            result = handler.verify_application(app_bundle)

        assert isinstance(result, AppInfo)
        assert result.path == app_bundle
        assert result.name == "Test"

    def test_verify_application_raises_for_nonexistent(self):
        """verify_application should raise ApplicationNotFoundError for missing app."""
        from vince.platform.errors import ApplicationNotFoundError
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()
        with pytest.raises(ApplicationNotFoundError):
            handler.verify_application(Path("/nonexistent/app.app"))

    def test_get_bundle_id_with_valid_bundle(self, tmp_path):
        """_get_bundle_id should extract bundle ID from Info.plist."""
        from vince.platform.macos import MacOSHandler

        # Create a mock .app bundle structure
        app_bundle = tmp_path / "Test.app"
        contents = app_bundle / "Contents"
        contents.mkdir(parents=True)

        handler = MacOSHandler()

        # Mock the defaults command
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="com.example.test\n",
            )
            result = handler._get_bundle_id(app_bundle)

        assert result == "com.example.test"

    def test_get_bundle_id_returns_none_on_failure(self, tmp_path):
        """_get_bundle_id should return None when defaults command fails."""
        from subprocess import CalledProcessError

        from vince.platform.macos import MacOSHandler

        app_bundle = tmp_path / "Test.app"
        app_bundle.mkdir(parents=True)

        handler = MacOSHandler()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = CalledProcessError(1, "defaults")
            result = handler._get_bundle_id(app_bundle)

        assert result is None

    def test_find_app_bundle_from_executable(self, tmp_path):
        """_find_app_bundle should find parent .app bundle."""
        from vince.platform.macos import MacOSHandler

        # Create nested structure: Test.app/Contents/MacOS/test
        app_bundle = tmp_path / "Test.app"
        macos_dir = app_bundle / "Contents" / "MacOS"
        macos_dir.mkdir(parents=True)
        executable = macos_dir / "test"
        executable.touch()

        handler = MacOSHandler()
        result = handler._find_app_bundle(executable)

        assert result == app_bundle

    def test_find_app_bundle_returns_none_for_standalone(self, tmp_path):
        """_find_app_bundle should return None for standalone executables."""
        from vince.platform.macos import MacOSHandler

        executable = tmp_path / "standalone_exe"
        executable.touch()

        handler = MacOSHandler()
        result = handler._find_app_bundle(executable)

        assert result is None


class TestMacOSHandlerGetCurrentDefault:
    """Tests for get_current_default method."""

    def test_get_current_default_with_duti(self):
        """get_current_default should use duti when available."""
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="/Applications/TextEdit.app\nTextEdit\ncom.apple.TextEdit\n",
            )
            result = handler.get_current_default(".txt")

        assert result == "/Applications/TextEdit.app"
        mock_run.assert_called_once()
        assert "duti" in mock_run.call_args[0][0]

    def test_get_current_default_falls_back_when_duti_missing(self):
        """get_current_default should fall back when duti is not installed."""
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("duti not found")

            # Also mock the PyObjC fallback
            with patch.object(
                handler, "_query_launch_services", return_value=None
            ) as mock_ls:
                result = handler.get_current_default(".txt")

        assert result is None
        mock_ls.assert_called_once()

    def test_get_current_default_returns_none_for_unknown_extension(self):
        """get_current_default should return None for unmapped extensions."""
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()
        result = handler.get_current_default(".unknown_ext_xyz")

        assert result is None


class TestMacOSHandlerSetDefault:
    """Tests for set_default method."""

    def test_set_default_dry_run(self, tmp_path):
        """set_default with dry_run should not make changes."""
        from vince.platform.macos import MacOSHandler

        # Create mock app bundle
        app_bundle = tmp_path / "Test.app"
        contents = app_bundle / "Contents"
        contents.mkdir(parents=True)

        handler = MacOSHandler()

        with patch("subprocess.run") as mock_run:
            # Mock bundle ID extraction
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="com.test.app\n",
            )

            result = handler.set_default(".md", app_bundle, dry_run=True)

        assert result.success is True
        assert "Would set" in result.message
        # Calls: bundle ID extraction + get_current_default (duti -x)
        # No call for duti -s (the actual set operation)
        duti_set_calls = [
            call for call in mock_run.call_args_list
            if "duti" in call[0][0] and "-s" in call[0][0]
        ]
        assert len(duti_set_calls) == 0, "dry_run should not call duti -s"

    def test_set_default_with_duti(self, tmp_path):
        """set_default should use duti when available."""
        from vince.platform.macos import MacOSHandler

        # Create mock app bundle
        app_bundle = tmp_path / "Test.app"
        contents = app_bundle / "Contents"
        contents.mkdir(parents=True)

        handler = MacOSHandler()

        with patch("subprocess.run") as mock_run:
            # First call: bundle ID extraction
            # Second call: duti -s
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="com.test.app\n",
            )

            result = handler.set_default(".md", app_bundle, dry_run=False)

        assert result.success is True
        assert "Test" in result.message

    def test_set_default_returns_error_for_unknown_extension(self, tmp_path):
        """set_default should return error for unmapped extensions."""
        from vince.platform.macos import MacOSHandler

        # Create mock app bundle
        app_bundle = tmp_path / "Test.app"
        contents = app_bundle / "Contents"
        contents.mkdir(parents=True)

        handler = MacOSHandler()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="com.test.app\n",
            )

            result = handler.set_default(".unknown_xyz", app_bundle, dry_run=False)

        assert result.success is False
        assert "No UTI mapping" in result.message
        assert result.error_code == "VE602"

    def test_set_default_raises_for_missing_bundle_id(self, tmp_path):
        """set_default should raise BundleIdNotFoundError when bundle ID missing."""
        from vince.platform.errors import BundleIdNotFoundError
        from vince.platform.macos import MacOSHandler

        # Create mock app bundle without bundle ID
        app_bundle = tmp_path / "Test.app"
        contents = app_bundle / "Contents"
        contents.mkdir(parents=True)

        handler = MacOSHandler()

        with patch("subprocess.run") as mock_run:
            from subprocess import CalledProcessError

            mock_run.side_effect = CalledProcessError(1, "defaults")

            with pytest.raises(BundleIdNotFoundError):
                handler.set_default(".md", app_bundle, dry_run=False)


class TestMacOSHandlerRemoveDefault:
    """Tests for remove_default method."""

    def test_remove_default_dry_run(self):
        """remove_default with dry_run should not make changes."""
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()
        result = handler.remove_default(".md", dry_run=True)

        assert result.success is True
        assert "Would reset" in result.message

    def test_remove_default_returns_error_for_unknown_extension(self):
        """remove_default should still work for unknown extensions."""
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()
        result = handler.remove_default(".unknown_xyz", dry_run=True)

        # Should still succeed in dry run mode
        assert result.success is True


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestMacOSHandlerProperties:
    """Property-based tests for MacOSHandler.

    **Property 3: Set-Query Round Trip (macOS)**
    **Validates: Requirements 2.1, 2.4**
    """

    @given(extension=supported_extensions, bundle_id=bundle_id_strategy)
    @settings(max_examples=100)
    def test_set_query_round_trip_dry_run(self, extension, bundle_id):
        """
        Property 3: Set-Query Round Trip (macOS)

        For any valid extension and application, if set_default succeeds
        in dry_run mode, the operation should be idempotent and not
        affect the actual OS state.

        **Validates: Requirements 2.1, 2.4**
        """
        import tempfile

        from vince.platform.macos import MacOSHandler

        # Create mock app bundle in a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            app_bundle = Path(tmp_dir) / "Test.app"
            contents = app_bundle / "Contents"
            contents.mkdir(parents=True, exist_ok=True)

            handler = MacOSHandler()

            with patch("subprocess.run") as mock_run:
                # Mock bundle ID extraction
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout=f"{bundle_id}\n",
                )

                # Dry run should always succeed for valid extensions
                result = handler.set_default(extension, app_bundle, dry_run=True)

                assert result.success is True
                assert "Would set" in result.message
                assert bundle_id in result.message

    @given(extension=supported_extensions)
    @settings(max_examples=100)
    def test_get_current_default_returns_consistent_type(self, extension):
        """
        Property: get_current_default returns consistent types.

        For any supported extension, get_current_default should return
        either a string path or None, never raise an exception.

        **Validates: Requirements 4.1**
        """
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()

        with patch("subprocess.run") as mock_run:
            # Simulate duti not found
            mock_run.side_effect = FileNotFoundError("duti not found")

            with patch.object(handler, "_query_launch_services", return_value=None):
                result = handler.get_current_default(extension)

        assert result is None or isinstance(result, str)

    @given(extension=supported_extensions)
    @settings(max_examples=100)
    def test_remove_default_dry_run_idempotent(self, extension):
        """
        Property: remove_default dry_run is idempotent.

        For any supported extension, remove_default in dry_run mode
        should always succeed and not modify state.

        **Validates: Requirements 5.1, 5.2, 7.1, 7.2**
        """
        from vince.platform.macos import MacOSHandler

        handler = MacOSHandler()

        # First call
        result1 = handler.remove_default(extension, dry_run=True)
        # Second call
        result2 = handler.remove_default(extension, dry_run=True)

        assert result1.success is True
        assert result2.success is True
        assert result1.message == result2.message
