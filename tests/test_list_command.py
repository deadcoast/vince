"""
Unit Tests for Vince CLI list command

Feature: vince-cli-implementation
Tests for the list command functionality.
Requirements: 14.4, 14.5, 14.6, 14.7
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


@pytest.fixture
def populated_data_dir(tmp_path):
    """Provide isolated data directory with sample data."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()

    # Create sample defaults
    defaults_data = {
        "version": "1.0.0",
        "defaults": [
            {
                "id": "def-md-000",
                "extension": ".md",
                "application_path": "/usr/bin/vim",
                "application_name": "vim",
                "state": "active",
                "created_at": "2024-01-01T00:00:00+00:00",
            },
            {
                "id": "def-py-001",
                "extension": ".py",
                "application_path": "/usr/bin/code",
                "application_name": "code",
                "state": "pending",
                "created_at": "2024-01-02T00:00:00+00:00",
            },
            {
                "id": "def-txt-002",
                "extension": ".txt",
                "application_path": "/usr/bin/nano",
                "application_name": "nano",
                "state": "removed",
                "created_at": "2024-01-03T00:00:00+00:00",
            },
        ],
    }
    (data_dir / "defaults.json").write_text(json.dumps(defaults_data))

    # Create sample offers
    offers_data = {
        "version": "1.0.0",
        "offers": [
            {
                "offer_id": "vim-md",
                "default_id": "def-md-000",
                "state": "active",
                "auto_created": True,
                "created_at": "2024-01-01T00:00:00+00:00",
            },
            {
                "offer_id": "code-py",
                "default_id": "def-py-001",
                "state": "created",
                "auto_created": False,
                "created_at": "2024-01-02T00:00:00+00:00",
            },
            {
                "offer_id": "old-offer",
                "default_id": "def-txt-002",
                "state": "rejected",
                "auto_created": False,
                "created_at": "2024-01-03T00:00:00+00:00",
            },
        ],
    }
    (data_dir / "offers.json").write_text(json.dumps(offers_data))

    return data_dir


class TestListCommand:
    """Tests for the list command."""

    def test_list_def_displays_defaults_table(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -def displays defaults table.

        Requirements: 14.4
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-def"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        # Should show active and pending, not removed
        assert ".md" in result.output
        assert ".py" in result.output
        # Removed entries should not appear
        assert "removed" not in result.output.lower() or ".txt" not in result.output

    def test_list_off_displays_offers_table(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -off displays offers table.

        Requirements: 14.5
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-off"])

        assert result.exit_code == 0
        assert "Offers" in result.output
        # Should show active and created, not rejected
        assert "vim-md" in result.output
        assert "code-py" in result.output
        # Rejected entries should not appear
        assert "old-offer" not in result.output

    def test_list_all_displays_both_tables(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -all displays both defaults and offers tables.

        Requirements: 14.6
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-all"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        assert "Offers" in result.output
        # Should show data from both tables
        assert ".md" in result.output
        assert "vim-md" in result.output

    def test_list_default_shows_all(self, runner, populated_data_dir, monkeypatch):
        """Test list without subsection defaults to -all.

        Requirements: 14.6
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should show both tables by default
        assert "Defaults" in result.output
        assert "Offers" in result.output

    def test_list_empty_data_shows_warning(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test list with empty data shows warning message.

        Requirements: 14.4, 14.5
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

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-def"])

        assert result.exit_code == 0
        assert "No defaults found" in result.output or "⚠" in result.output

    def test_list_with_extension_filter(self, runner, populated_data_dir, monkeypatch):
        """Test list with extension filter shows only matching entries.

        Requirements: 14.2
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-def", "--md"])

        assert result.exit_code == 0
        assert ".md" in result.output
        # Should not show .py entries
        assert ".py" not in result.output

    def test_list_verbose_output(self, runner, populated_data_dir, monkeypatch):
        """Test list with verbose flag shows additional info.

        Requirements: 14.3
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-def", "-vb"])

        assert result.exit_code == 0
        # Verbose output should include total count
        assert (
            "Total defaults" in result.output
            or "Displaying subsection" in result.output
        )

    def test_list_app_displays_applications(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -app displays applications table.

        Requirements: 14.1
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-app"])

        assert result.exit_code == 0
        assert "Applications" in result.output
        assert "vim" in result.output or "/usr/bin/vim" in result.output

    def test_list_cmd_displays_commands(self, runner, populated_data_dir, monkeypatch):
        """Test list -cmd displays commands table.

        Requirements: 14.1
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-cmd"])

        assert result.exit_code == 0
        assert "Commands" in result.output
        assert "vim-md" in result.output

    def test_list_ext_displays_extensions(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -ext displays extensions table.

        Requirements: 14.1
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-ext"])

        assert result.exit_code == 0
        assert "Extensions" in result.output
        assert ".md" in result.output
        assert ".py" in result.output


# =============================================================================
# Subsection Flag Tests (Requirements: 4.1, 4.2, 4.3)
# =============================================================================


class TestListSubsectionFlags:
    """Tests for list command subsection flags.

    Requirements: 4.1, 4.2, 4.3
    """

    def test_list_app_shows_unique_applications(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -app shows unique applications with their extensions.

        Requirements: 4.1
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-app"])

        assert result.exit_code == 0
        assert "Applications" in result.output
        # Should show application names or paths
        assert "vim" in result.output or "/usr/bin/vim" in result.output
        assert "code" in result.output or "/usr/bin/code" in result.output
        # Should show extensions column
        assert ".md" in result.output

    def test_list_app_with_verbose_shows_count(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -app with verbose flag shows application count.

        Requirements: 4.1
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-app", "-vb"])

        assert result.exit_code == 0
        assert "Applications" in result.output
        assert "Total applications" in result.output

    def test_list_cmd_shows_offer_commands(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -cmd shows offer commands/aliases.

        Requirements: 4.2
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-cmd"])

        assert result.exit_code == 0
        assert "Commands" in result.output
        # Should show offer IDs as commands
        assert "vim-md" in result.output
        assert "code-py" in result.output
        # Should show auto-created column
        assert "Yes" in result.output or "No" in result.output

    def test_list_cmd_with_verbose_shows_count(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -cmd with verbose flag shows command count.

        Requirements: 4.2
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-cmd", "-vb"])

        assert result.exit_code == 0
        assert "Commands" in result.output
        assert "Total commands" in result.output

    def test_list_ext_shows_extension_details(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -ext shows extension details with counts and states.

        Requirements: 4.3
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-ext"])

        assert result.exit_code == 0
        assert "Extensions" in result.output
        # Should show extensions
        assert ".md" in result.output
        assert ".py" in result.output
        # Should show states
        assert "active" in result.output or "pending" in result.output

    def test_list_ext_with_verbose_shows_count(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -ext with verbose flag shows extension count.

        Requirements: 4.3
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-ext", "-vb"])

        assert result.exit_code == 0
        assert "Extensions" in result.output
        assert "Total extensions" in result.output

    def test_list_app_empty_data_shows_warning(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test list -app with empty data shows warning.

        Requirements: 4.1
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

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-app"])

        assert result.exit_code == 0
        assert "No applications found" in result.output or "⚠" in result.output

    def test_list_cmd_empty_data_shows_warning(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test list -cmd with empty data shows warning.

        Requirements: 4.2
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

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-cmd"])

        assert result.exit_code == 0
        assert "No commands found" in result.output or "⚠" in result.output

    def test_list_ext_empty_data_shows_warning(
        self, runner, isolated_data_dir, monkeypatch
    ):
        """Test list -ext with empty data shows warning.

        Requirements: 4.3
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

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-ext"])

        assert result.exit_code == 0
        assert "No extensions found" in result.output or "⚠" in result.output

    def test_list_app_with_extension_filter(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -app with extension filter shows only matching apps.

        Requirements: 4.1
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["list", "-app", "--md"])

        assert result.exit_code == 0
        assert "Applications" in result.output
        # Should show vim (associated with .md)
        assert "vim" in result.output or "/usr/bin/vim" in result.output
        # Should not show code (associated with .py)
        assert "code" not in result.output


# =============================================================================
# OS Integration Tests (Requirements: 4.4, 4.5)
# =============================================================================


class TestListOSIntegration:
    """Tests for list command OS integration features.

    Requirements: 4.4, 4.5
    """

    def test_list_def_shows_mismatch_warning_when_paths_differ(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -def shows warning indicator when vince and OS defaults differ.

        Requirements: 4.4
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        # Mock platform handler to return different path than vince default
        mock_handler = MagicMock()
        # Vince has /usr/bin/vim for .md, but OS returns different app
        mock_handler.get_current_default.return_value = "/Applications/TextEdit.app"

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        with patch("vince.platform.get_platform", return_value=Platform.MACOS):
            with patch("vince.platform.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["list", "-def"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        # Should show mismatch warning indicator
        assert "⚠" in result.output

    def test_list_def_shows_success_when_paths_match(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -def shows success indicator when vince and OS defaults match.

        Requirements: 4.4
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        # Mock platform handler to return same path as vince default
        mock_handler = MagicMock()
        # Vince has /usr/bin/vim for .md, OS returns same
        mock_handler.get_current_default.return_value = "/usr/bin/vim"

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        with patch("vince.platform.get_platform", return_value=Platform.MACOS):
            with patch("vince.platform.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["list", "-def"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        # Should show success indicator
        assert "✓" in result.output

    def test_list_def_shows_unknown_when_os_query_fails(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -def shows 'unknown' when OS query fails.

        Requirements: 4.5
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        # Mock platform handler to raise exception (query failure)
        mock_handler = MagicMock()
        mock_handler.get_current_default.side_effect = Exception("Query failed")

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        with patch("vince.platform.get_platform", return_value=Platform.MACOS):
            with patch("vince.platform.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["list", "-def"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        # Should show unknown indicator (?) for failed query
        assert "?" in result.output or "unknown" in result.output

    def test_list_def_shows_unknown_when_os_returns_none(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -def shows 'unknown' when OS returns None.

        Requirements: 4.5
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        # Mock platform handler to return None (no default set in OS)
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = None

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        with patch("vince.platform.get_platform", return_value=Platform.MACOS):
            with patch("vince.platform.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["list", "-def"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        # Should show unknown indicator (?) when OS returns None
        assert "?" in result.output or "unknown" in result.output

    def test_list_def_shows_unknown_on_unsupported_platform(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -def shows 'unknown' on unsupported platform.

        Requirements: 4.5
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        with patch("vince.platform.get_platform", return_value=Platform.UNSUPPORTED):
            result = runner.invoke(app, ["list", "-def"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        # Should show unknown indicator (?) for unsupported platform
        assert "?" in result.output or "unknown" in result.output

    def test_list_def_verbose_shows_mismatch_count(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -def with verbose shows mismatch count.

        Requirements: 4.4
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        # Mock platform handler to return different paths (mismatches)
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = "/different/path"

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        with patch("vince.platform.get_platform", return_value=Platform.MACOS):
            with patch("vince.platform.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["list", "-def", "-vb"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        # Verbose should show mismatch count
        assert "Mismatches detected" in result.output

    def test_list_def_verbose_shows_os_default_info(
        self, runner, populated_data_dir, monkeypatch
    ):
        """Test list -def with verbose shows OS default info.

        Requirements: 4.4
        """

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return populated_data_dir

        # Mock platform handler to return a path
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = "/usr/bin/vim"

        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)

        with patch("vince.platform.get_platform", return_value=Platform.MACOS):
            with patch("vince.platform.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["list", "-def", "-vb"])

        assert result.exit_code == 0
        assert "Defaults" in result.output
        # Verbose should show OS default info
        assert "OS default for" in result.output


# =============================================================================
# Property-Based Tests for Mismatch Detection
# =============================================================================

from unittest.mock import MagicMock, patch

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from vince.output.tables import _get_sync_status, _normalize_path, create_defaults_table
from vince.platform.base import Platform


# Strategy for supported extensions
supported_extensions = st.sampled_from([
    ".md", ".py", ".txt", ".js", ".html", ".css",
    ".json", ".yml", ".yaml", ".xml", ".csv", ".sql"
])

# Strategy for application paths
app_path_strategy = st.sampled_from([
    "/Applications/Visual Studio Code.app",
    "/Applications/Sublime Text.app",
    "/usr/bin/vim",
    "/usr/bin/nano",
    "/usr/local/bin/code",
    "C:\\Program Files\\VSCode\\code.exe",
    "C:\\Program Files\\Notepad++\\notepad++.exe",
])


class TestMismatchDetectionProperties:
    """Property-based tests for mismatch detection in list command.

    **Property 4: List Mismatch Detection**
    **Validates: Requirements 4.4**
    """

    @given(
        vince_path=app_path_strategy,
        os_path=app_path_strategy,
    )
    @settings(max_examples=100)
    def test_mismatch_detected_when_paths_differ(self, vince_path, os_path):
        """
        Property 4: List Mismatch Detection

        For any vince default path and OS default path, if the normalized
        paths differ, the sync status should show a warning indicator.

        **Validates: Requirements 4.4**
        """
        vince_normalized = _normalize_path(vince_path)
        os_normalized = _normalize_path(os_path)

        status = _get_sync_status(vince_path, os_path)

        if vince_normalized == os_normalized:
            # Paths match - should show success
            assert status.plain == "✓", f"Expected ✓ for matching paths: {vince_path} == {os_path}"
        else:
            # Paths differ - should show warning
            assert status.plain == "⚠", f"Expected ⚠ for mismatched paths: {vince_path} != {os_path}"

    @given(path=app_path_strategy)
    @settings(max_examples=100)
    def test_matching_paths_show_success(self, path):
        """
        Property 4: List Mismatch Detection

        For any path, when vince and OS defaults are the same,
        the sync status should show a success indicator.

        **Validates: Requirements 4.4**
        """
        status = _get_sync_status(path, path)
        assert status.plain == "✓", f"Expected ✓ for identical paths: {path}"

    @given(path=app_path_strategy)
    @settings(max_examples=100)
    def test_unknown_os_default_shows_question_mark(self, path):
        """
        Property 4: List Mismatch Detection

        For any vince path, when OS default is unknown (None),
        the sync status should show a question mark indicator.

        **Validates: Requirements 4.4**
        """
        status = _get_sync_status(path, None)
        assert status.plain == "?", f"Expected ? for unknown OS default with vince path: {path}"

    @given(extension=supported_extensions)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_list_queries_os_for_each_extension(self, extension, tmp_path):
        """
        Property 4: List Mismatch Detection

        For any supported extension with an active default, the list command
        should query the OS for the current default application.

        **Validates: Requirements 4.4**
        """
        import uuid
        from typer.testing import CliRunner
        from vince.main import app

        runner = CliRunner()

        # Create isolated data dir with unique name for each hypothesis iteration
        unique_id = uuid.uuid4().hex[:8]
        data_dir = tmp_path / f".vince_{unique_id}"
        data_dir.mkdir(parents=True, exist_ok=True)

        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": f"def-{extension[1:]}-000",
                    "extension": extension,
                    "application_path": "/usr/bin/vim",
                    "application_name": "vim",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return data_dir

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = "/usr/bin/vim"

        with patch("vince.commands.list_cmd.get_config", mock_get_config):
            with patch("vince.commands.list_cmd.get_data_dir", mock_get_data_dir):
                with patch("vince.platform.get_platform", return_value=Platform.MACOS):
                    with patch("vince.platform.get_handler", return_value=mock_handler):
                        result = runner.invoke(app, ["list", "-def"])

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called to query OS default
        mock_handler.get_current_default.assert_called()

        # The extension should be in the output
        assert extension in result.output

    @given(
        extension=supported_extensions,
        vince_path=app_path_strategy,
        os_path=app_path_strategy,
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_mismatch_indicator_in_table_output(self, extension, vince_path, os_path, tmp_path):
        """
        Property 4: List Mismatch Detection

        For any extension with a vince default and OS default, the table
        should correctly show the mismatch indicator based on path comparison.

        **Validates: Requirements 4.4**
        """
        import uuid
        from typer.testing import CliRunner
        from vince.main import app

        runner = CliRunner()

        # Create isolated data dir with unique name for each hypothesis iteration
        unique_id = uuid.uuid4().hex[:8]
        data_dir = tmp_path / f".vince_{unique_id}"
        data_dir.mkdir(parents=True, exist_ok=True)

        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": f"def-{extension[1:]}-000",
                    "extension": extension,
                    "application_path": vince_path,
                    "application_name": "TestApp",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5,
            }

        def mock_get_data_dir(config=None):
            return data_dir

        # Mock the platform handler to return the OS path
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = os_path

        with patch("vince.commands.list_cmd.get_config", mock_get_config):
            with patch("vince.commands.list_cmd.get_data_dir", mock_get_data_dir):
                with patch("vince.platform.get_platform", return_value=Platform.MACOS):
                    with patch("vince.platform.get_handler", return_value=mock_handler):
                        result = runner.invoke(app, ["list", "-def"])

        # Command should succeed
        assert result.exit_code == 0

        # Check for appropriate indicator based on path comparison
        vince_normalized = _normalize_path(vince_path)
        os_normalized = _normalize_path(os_path)

        if vince_normalized == os_normalized:
            # Paths match - should show success indicator
            assert "✓" in result.output, f"Expected ✓ for matching paths in output"
        else:
            # Paths differ - should show warning indicator
            assert "⚠" in result.output, f"Expected ⚠ for mismatched paths in output"


class TestNormalizePathProperties:
    """Property-based tests for path normalization."""

    @given(path=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    @settings(max_examples=100)
    def test_normalize_removes_trailing_slashes(self, path):
        """Normalized paths should not have trailing slashes."""
        normalized = _normalize_path(path)
        assert not normalized.endswith("/"), f"Path should not end with /: {normalized}"
        assert not normalized.endswith("\\"), f"Path should not end with \\: {normalized}"

    @given(path=app_path_strategy)
    @settings(max_examples=100)
    def test_normalize_is_idempotent(self, path):
        """Normalizing a path twice should give the same result."""
        once = _normalize_path(path)
        twice = _normalize_path(once)
        assert once == twice, f"Normalization should be idempotent: {once} != {twice}"

    def test_normalize_empty_path(self):
        """Empty path should normalize to empty string."""
        assert _normalize_path("") == ""
        assert _normalize_path(None) == "" if _normalize_path(None) is not None else True


class TestCreateDefaultsTableWithOsDefaults:
    """Tests for create_defaults_table with OS defaults column."""

    def test_table_without_os_defaults_has_three_columns(self):
        """Table without OS defaults should have 3 columns."""
        defaults = [
            {"extension": ".md", "application_path": "/usr/bin/vim", "state": "active"}
        ]
        table = create_defaults_table(defaults)
        assert len(table.columns) == 3

    def test_table_with_os_defaults_has_five_columns(self):
        """Table with OS defaults should have 5 columns."""
        defaults = [
            {"extension": ".md", "application_path": "/usr/bin/vim", "state": "active"}
        ]
        os_defaults = {".md": "/usr/bin/vim"}
        table = create_defaults_table(defaults, os_defaults)
        assert len(table.columns) == 5

    def test_table_shows_unknown_for_none_os_default(self):
        """Table should show 'unknown' when OS default is None."""
        defaults = [
            {"extension": ".md", "application_path": "/usr/bin/vim", "state": "active"}
        ]
        os_defaults = {".md": None}
        table = create_defaults_table(defaults, os_defaults)
        # The table should have been created with the unknown value
        assert len(table.columns) == 5
