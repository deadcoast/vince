"""
Unit Tests for Vince CLI chop command

Feature: vince-cli-implementation
Tests for the chop command functionality.
Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
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
def isolated_data_dir(tmp_path):
    """Provide isolated data directory with empty data files."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()
    (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    return data_dir


class TestChopCommand:
    """Tests for the chop command."""

    def test_chop_with_forget_removes_active_default(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test chop with -forget transitions active default to removed state.

        Requirements: 9.4
        """
        # Pre-populate defaults.json with an active default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/vim",
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

        monkeypatch.setattr("vince.commands.chop.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["chop", "--md", "-forget"])

        assert result.exit_code == 0
        assert "Default removed" in result.output or "✓" in result.output

        # Verify defaults.json was updated to removed state
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "removed"

    def test_chop_error_when_no_default_exists(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test chop raises error when no default exists for extension.

        Requirements: 9.5
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

        monkeypatch.setattr("vince.commands.chop.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["chop", "--md", "-forget"])

        # Should fail with NoDefaultError (VE302)
        assert result.exit_code == 1
        assert "VE302" in result.output or "No default set" in result.output

    def test_chop_without_forget_shows_info(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test chop without -forget shows current default info.

        Requirements: 9.1
        """
        # Pre-populate defaults.json with an active default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-py-000",
                    "extension": ".py",
                    "application_path": "/usr/bin/python3",
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

        monkeypatch.setattr("vince.commands.chop.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["chop", "--py"])

        assert result.exit_code == 0
        # Should show info about the default without changing state
        assert "/usr/bin/python3" in result.output or "Default for" in result.output

        # Verify state was NOT changed
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "active"

    def test_chop_error_no_extension_specified(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test chop raises error when no extension is specified.

        Requirements: 9.1
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

        monkeypatch.setattr("vince.commands.chop.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["chop", "-forget"])

        # Should fail with error about no extension
        assert result.exit_code == 1
        assert "VE102" in result.output or "extension" in result.output.lower()

    def test_chop_verbose_output(self, runner, isolated_data_dir, monkeypatch):
        """Test chop with verbose flag shows additional info.

        Requirements: 9.3
        """
        # Pre-populate defaults.json with an active default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-txt-000",
                    "extension": ".txt",
                    "application_path": "/usr/bin/nano",
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

        monkeypatch.setattr("vince.commands.chop.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["chop", "--txt", "-forget", "-vb"])

        assert result.exit_code == 0
        # Verbose output should include additional info
        assert "Target extension" in result.output or "Current state" in result.output

    def test_chop_pending_default_to_removed(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test chop with -forget on pending default transitions to removed.

        Requirements: 9.4
        """
        # Pre-populate defaults.json with a pending default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-js-000",
                    "extension": ".js",
                    "application_path": "/usr/bin/node",
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

        monkeypatch.setattr("vince.commands.chop.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["chop", "--js", "-forget"])

        assert result.exit_code == 0

        # Verify state was updated to removed
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "removed"
