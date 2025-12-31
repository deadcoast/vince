"""
Unit Tests for Vince CLI set command

Feature: vince-cli-implementation
Tests for the set command functionality.
Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import json

import pytest
from typer.testing import CliRunner

from vince.main import app


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


class TestSetCommand:
    """Tests for the set command."""

    def test_set_creates_active_default(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test set creates an active default entry.

        Requirements: 10.4
        """

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

        monkeypatch.setattr("vince.commands.set_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.set_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["set", str(mock_executable), "--md"])

        assert result.exit_code == 0
        assert "Default set" in result.output or "✓" in result.output

        # Verify defaults.json was updated with active state
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "active"
        assert defaults_data["defaults"][0]["extension"] == ".md"

    def test_set_error_when_default_exists(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test set raises error when default already exists for extension.

        Requirements: 10.5
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

        monkeypatch.setattr("vince.commands.set_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.set_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["set", str(mock_executable), "--md"])

        # Should fail with DefaultExistsError (VE301)
        assert result.exit_code == 1
        assert "VE301" in result.output or "Default already exists" in result.output

    def test_set_error_no_extension_specified(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test set raises error when no extension is specified.

        Requirements: 10.2
        """

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

        monkeypatch.setattr("vince.commands.set_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.set_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["set", str(mock_executable)])

        # Should fail with error about no extension
        assert result.exit_code == 1
        assert "VE102" in result.output or "extension" in result.output.lower()

    def test_set_verbose_output(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test set with verbose flag shows additional info.

        Requirements: 10.3
        """

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

        monkeypatch.setattr("vince.commands.set_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.set_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["set", str(mock_executable), "--py", "-vb"])

        assert result.exit_code == 0
        # Verbose output should include additional info
        assert "Processing path" in result.output or "Target extension" in result.output

    def test_set_pending_to_active_transition(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test set can transition pending default to active.

        Requirements: 10.4
        """
        # Pre-populate defaults.json with a pending default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-txt-000",
                    "extension": ".txt",
                    "application_path": str(mock_executable),
                    "state": "pending",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))

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

        monkeypatch.setattr("vince.commands.set_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.set_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["set", str(mock_executable), "--txt"])

        assert result.exit_code == 0

        # Verify state was updated to active
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "active"
