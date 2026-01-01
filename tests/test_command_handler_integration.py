"""
Property-Based Tests for Command-Handler Integration

Feature: os-integration
Property 7: Command Integration Calls Handler
Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5

This module tests that vince commands properly integrate with the platform
handler to apply OS-level file association changes.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from typer.testing import CliRunner

from vince.main import app
from vince.platform.base import OperationResult, Platform


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def runner():
    """Provide a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_executable(tmp_path):
    """Create a mock executable file for testing."""
    exe = tmp_path / "mock_app"
    exe.write_text("#!/bin/bash\necho 'mock'")
    exe.chmod(0o755)
    return exe


@pytest.fixture
def isolated_data_dir(tmp_path):
    """Provide isolated data directory with empty data files."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()
    (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    return data_dir


def mock_config_factory(isolated_data_dir):
    """Create mock config functions for a given data directory."""
    def mock_get_config(*args, **kwargs):
        return {
            "version": "1.0.0",
            "data_dir": str(isolated_data_dir),
            "verbose": False,
            "backup_enabled": False,
            "max_backups": 5,
        }

    def mock_get_data_dir(config=None):
        return isolated_data_dir

    return mock_get_config, mock_get_data_dir


# =============================================================================
# Strategies for Property-Based Testing
# =============================================================================

# Strategy for supported extensions
supported_extensions = st.sampled_from([
    ".md", ".py", ".txt", ".js", ".html", ".css",
    ".json", ".yml", ".yaml", ".xml", ".csv", ".sql"
])

# Strategy for extension flags
extension_flags = st.sampled_from([
    "--md", "--py", "--txt", "--js", "--html", "--css",
    "--json", "--yml", "--yaml", "--xml", "--csv", "--sql"
])


# =============================================================================
# Unit Tests for Command-Handler Integration
# =============================================================================


class TestSlapCommandHandlerIntegration:
    """Tests for slap command integration with platform handler.
    
    Requirements: 10.1, 10.5
    """

    def test_slap_set_calls_platform_handler(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap -set calls platform handler's set_default.
        
        Requirements: 10.1
        """
        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Set mock_app as default for .md",
            previous_default="/Applications/TextEdit.app",
        )

        with patch("vince.commands.slap.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.slap.get_handler", return_value=mock_handler):
                result = runner.invoke(
                    app, ["slap", str(mock_executable), "-set", "--md"]
                )

        assert result.exit_code == 0
        mock_handler.set_default.assert_called_once()
        call_args = mock_handler.set_default.call_args
        assert call_args[0][0] == ".md"  # extension
        assert call_args[1]["dry_run"] is False

    def test_slap_set_warns_on_os_failure(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap -set warns when OS operation fails.
        
        Requirements: 10.5
        """
        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        # Mock the platform handler to fail
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=False,
            message="Launch Services error",
            error_code="VE605",
        )

        with patch("vince.commands.slap.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.slap.get_handler", return_value=mock_handler):
                result = runner.invoke(
                    app, ["slap", str(mock_executable), "-set", "--md"]
                )

        # Command should still succeed (JSON update worked)
        assert result.exit_code == 0
        # But should warn about OS failure
        assert "OS operation failed" in result.output or "sync" in result.output

    def test_slap_dry_run_does_not_modify_os(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap -set -dry does not modify OS state.
        
        Requirements: 7.1, 7.2
        """
        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Would set mock_app as default for .md",
            previous_default="/Applications/TextEdit.app",
        )

        with patch("vince.commands.slap.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.slap.get_handler", return_value=mock_handler):
                result = runner.invoke(
                    app, ["slap", str(mock_executable), "-set", "-dry", "--md"]
                )

        assert result.exit_code == 0
        mock_handler.set_default.assert_called_once()
        call_args = mock_handler.set_default.call_args
        assert call_args[1]["dry_run"] is True
        assert "dry run" in result.output.lower()


class TestSetCommandHandlerIntegration:
    """Tests for set command integration with platform handler.
    
    Requirements: 10.3
    """

    def test_set_calls_platform_handler(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test set command calls platform handler's set_default.
        
        Requirements: 10.3
        """
        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.set_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.set_cmd.get_data_dir", mock_get_data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Set mock_app as default for .py",
            previous_default=None,
        )

        with patch("vince.commands.set_cmd.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.set_cmd.get_handler", return_value=mock_handler):
                result = runner.invoke(
                    app, ["set", str(mock_executable), "--py"]
                )

        assert result.exit_code == 0
        mock_handler.set_default.assert_called_once()
        call_args = mock_handler.set_default.call_args
        assert call_args[0][0] == ".py"


class TestChopCommandHandlerIntegration:
    """Tests for chop command integration with platform handler.
    
    Requirements: 10.2
    """

    def test_chop_forget_calls_platform_handler(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test chop -forget calls platform handler's remove_default.
        
        Requirements: 10.2
        """
        # Pre-populate defaults.json with an active default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/existing",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))

        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.chop.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_get_data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.remove_default.return_value = OperationResult(
            success=True,
            message="Removed default for .md",
            previous_default="/usr/bin/existing",
        )

        with patch("vince.commands.chop.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.chop.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["chop", "-forget", "--md"])

        assert result.exit_code == 0
        mock_handler.remove_default.assert_called_once()
        call_args = mock_handler.remove_default.call_args
        assert call_args[0][0] == ".md"


class TestForgetCommandHandlerIntegration:
    """Tests for forget command integration with platform handler.
    
    Requirements: 10.4
    """

    def test_forget_calls_platform_handler(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test forget command calls platform handler's remove_default.
        
        Requirements: 10.4
        """
        # Pre-populate defaults.json with an active default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-py-000",
                    "extension": ".py",
                    "application_path": "/usr/bin/python",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))

        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.forget.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.forget.get_data_dir", mock_get_data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.remove_default.return_value = OperationResult(
            success=True,
            message="Removed default for .py",
            previous_default="/usr/bin/python",
        )

        with patch("vince.commands.forget.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.forget.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["forget", "--py"])

        assert result.exit_code == 0
        mock_handler.remove_default.assert_called_once()
        call_args = mock_handler.remove_default.call_args
        assert call_args[0][0] == ".py"


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestCommandHandlerIntegrationProperties:
    """Property-based tests for command-handler integration.

    **Property 7: Command Integration Calls Handler**
    **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**
    """

    @given(ext_flag=extension_flags)
    @settings(max_examples=12)
    def test_slap_set_always_calls_handler_for_supported_extensions(
        self, ext_flag, tmp_path
    ):
        """
        Property 7: Command Integration Calls Handler

        For any supported extension, slap -set should always attempt to
        call the platform handler's set_default method.

        **Validates: Requirements 10.1**
        """
        runner = CliRunner()

        # Create mock executable
        exe = tmp_path / "mock_app"
        exe.write_text("#!/bin/bash\necho 'mock'")
        exe.chmod(0o755)

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir()
        (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Set mock_app as default",
            previous_default=None,
        )

        with patch("vince.commands.slap.get_config", mock_get_config):
            with patch("vince.commands.slap.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.slap.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.slap.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["slap", str(exe), "-set", ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called
        mock_handler.set_default.assert_called_once()

        # Extension should match the flag
        expected_ext = ext_flag.replace("--", ".")
        call_args = mock_handler.set_default.call_args
        assert call_args[0][0] == expected_ext

    @given(ext_flag=extension_flags)
    @settings(max_examples=12)
    def test_set_always_calls_handler_for_supported_extensions(
        self, ext_flag, tmp_path
    ):
        """
        Property 7: Command Integration Calls Handler

        For any supported extension, set command should always attempt to
        call the platform handler's set_default method.

        **Validates: Requirements 10.3**
        """
        runner = CliRunner()

        # Create mock executable
        exe = tmp_path / "mock_app"
        exe.write_text("#!/bin/bash\necho 'mock'")
        exe.chmod(0o755)

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir()
        (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Set mock_app as default",
            previous_default=None,
        )

        with patch("vince.commands.set_cmd.get_config", mock_get_config):
            with patch("vince.commands.set_cmd.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.set_cmd.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.set_cmd.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["set", str(exe), ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called
        mock_handler.set_default.assert_called_once()

        # Extension should match the flag
        expected_ext = ext_flag.replace("--", ".")
        call_args = mock_handler.set_default.call_args
        assert call_args[0][0] == expected_ext

    @given(ext_flag=extension_flags)
    @settings(max_examples=12)
    def test_chop_forget_always_calls_handler_for_active_defaults(
        self, ext_flag, tmp_path
    ):
        """
        Property 7: Command Integration Calls Handler

        For any supported extension with an active default, chop -forget
        should always attempt to call the platform handler's remove_default.

        **Validates: Requirements 10.2**
        """
        runner = CliRunner()

        # Create isolated data dir with active default
        data_dir = tmp_path / ".vince"
        data_dir.mkdir()

        ext = ext_flag.replace("--", ".")
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": f"def-{ext[1:]}-000",
                    "extension": ext,
                    "application_path": "/usr/bin/existing",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.remove_default.return_value = OperationResult(
            success=True,
            message=f"Removed default for {ext}",
            previous_default="/usr/bin/existing",
        )

        with patch("vince.commands.chop.get_config", mock_get_config):
            with patch("vince.commands.chop.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.chop.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.chop.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["chop", "-forget", ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called
        mock_handler.remove_default.assert_called_once()

        # Extension should match the flag
        call_args = mock_handler.remove_default.call_args
        assert call_args[0][0] == ext

    @given(ext_flag=extension_flags)
    @settings(max_examples=12)
    def test_forget_always_calls_handler_for_active_defaults(
        self, ext_flag, tmp_path
    ):
        """
        Property 7: Command Integration Calls Handler

        For any supported extension with an active default, forget command
        should always attempt to call the platform handler's remove_default.

        **Validates: Requirements 10.4**
        """
        runner = CliRunner()

        # Create isolated data dir with active default
        data_dir = tmp_path / ".vince"
        data_dir.mkdir()

        ext = ext_flag.replace("--", ".")
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": f"def-{ext[1:]}-000",
                    "extension": ext,
                    "application_path": "/usr/bin/existing",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.remove_default.return_value = OperationResult(
            success=True,
            message=f"Removed default for {ext}",
            previous_default="/usr/bin/existing",
        )

        with patch("vince.commands.forget.get_config", mock_get_config):
            with patch("vince.commands.forget.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.forget.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.forget.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["forget", ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called
        mock_handler.remove_default.assert_called_once()

        # Extension should match the flag
        call_args = mock_handler.remove_default.call_args
        assert call_args[0][0] == ext

    @given(ext_flag=extension_flags)
    @settings(max_examples=12)
    def test_os_failure_does_not_fail_command(
        self, ext_flag, tmp_path
    ):
        """
        Property 7: Command Integration Calls Handler

        For any supported extension, if the OS operation fails, the command
        should still succeed (JSON update worked) but warn the user.

        **Validates: Requirements 10.5**
        """
        runner = CliRunner()

        # Create mock executable
        exe = tmp_path / "mock_app"
        exe.write_text("#!/bin/bash\necho 'mock'")
        exe.chmod(0o755)

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir()
        (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler to fail
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=False,
            message="OS operation failed",
            error_code="VE605",
        )

        with patch("vince.commands.slap.get_config", mock_get_config):
            with patch("vince.commands.slap.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.slap.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.slap.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["slap", str(exe), "-set", ext_flag]
                        )

        # Command should still succeed (JSON update worked)
        assert result.exit_code == 0

        # Should warn about OS failure
        assert "OS operation failed" in result.output or "sync" in result.output

        # JSON should still be updated
        defaults_data = json.loads((data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "active"
