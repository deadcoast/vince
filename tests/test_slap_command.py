"""
Unit Tests for Vince CLI slap command

Feature: vince-cli-implementation
Tests for the slap command functionality.
Requirements: 8.5, 8.6, 8.7
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


@pytest.fixture
def project_config(tmp_path, isolated_data_dir):
    """Create a project config that points to the isolated data dir."""
    config_dir = tmp_path / ".vince_config"
    config_dir.mkdir()
    config_file = config_dir / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "data_dir": str(isolated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }
        )
    )
    return config_file


class TestSlapCommand:
    """Tests for the slap command."""

    def test_slap_creates_pending_default(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap without -set creates a pending default entry.

        Requirements: 8.5
        """

        # Monkeypatch get_config to use isolated data dir
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

        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["slap", str(mock_executable), "--md"])

        assert result.exit_code == 0
        assert "Default identified" in result.output or "✓" in result.output

        # Verify defaults.json was updated
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "pending"
        assert defaults_data["defaults"][0]["extension"] == ".md"

    def test_slap_with_set_creates_active_default_and_offer(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap with -set creates an active default entry and auto-creates an offer.

        Requirements: 8.6
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

        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["slap", str(mock_executable), "-set", "--py"])

        assert result.exit_code == 0
        assert "Default set" in result.output or "✓" in result.output
        assert "Offer created" in result.output

        # Verify defaults.json was updated with active state
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "active"
        assert defaults_data["defaults"][0]["extension"] == ".py"

        # Verify offers.json was updated
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 1
        assert offers_data["offers"][0]["auto_created"] is True
        assert offers_data["offers"][0]["state"] == "created"

    def test_slap_error_when_default_exists(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap raises error when default already exists for extension.

        Requirements: 8.7
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

        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["slap", str(mock_executable), "--md"])

        # Should fail with error
        assert result.exit_code == 1
        assert "VE301" in result.output or "Default already exists" in result.output

    def test_slap_error_invalid_path(self, runner, isolated_data_dir, monkeypatch):
        """Test slap raises error for invalid path.

        Requirements: 8.1
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

        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["slap", "/nonexistent/path", "--md"])

        # Typer validates path existence before our code runs
        assert result.exit_code != 0

    def test_slap_error_no_extension_specified(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap raises error when no extension is specified.

        Requirements: 8.2
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

        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["slap", str(mock_executable)])

        # Should fail with error about no extension
        assert result.exit_code == 1
        assert "VE102" in result.output or "extension" in result.output.lower()

    def test_slap_verbose_output(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap with verbose flag shows additional info.

        Requirements: 8.4
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

        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["slap", str(mock_executable), "--md", "-vb"])

        assert result.exit_code == 0
        # Verbose output should include additional info
        assert "Processing path" in result.output or "Target extension" in result.output

    def test_slap_multiple_extensions_uses_first(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap with multiple extension flags uses the first one.

        Requirements: 8.2
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

        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["slap", str(mock_executable), "--md", "--py"])

        assert result.exit_code == 0

        # Verify the first extension (.md) was used
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["extension"] == ".md"

    def test_slap_pending_to_active_transition(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test slap -set can transition pending to active.

        Requirements: 8.5, 8.6
        """
        # Pre-populate defaults.json with a pending default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
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

        monkeypatch.setattr("vince.commands.slap.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["slap", str(mock_executable), "-set", "--md"])

        assert result.exit_code == 0

        # Verify state was updated to active
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "active"
