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
                "created_at": "2024-01-01T00:00:00+00:00"
            },
            {
                "id": "def-py-001",
                "extension": ".py",
                "application_path": "/usr/bin/code",
                "application_name": "code",
                "state": "pending",
                "created_at": "2024-01-02T00:00:00+00:00"
            },
            {
                "id": "def-txt-002",
                "extension": ".txt",
                "application_path": "/usr/bin/nano",
                "application_name": "nano",
                "state": "removed",
                "created_at": "2024-01-03T00:00:00+00:00"
            }
        ]
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
                "created_at": "2024-01-01T00:00:00+00:00"
            },
            {
                "offer_id": "code-py",
                "default_id": "def-py-001",
                "state": "created",
                "auto_created": False,
                "created_at": "2024-01-02T00:00:00+00:00"
            },
            {
                "offer_id": "old-offer",
                "default_id": "def-txt-002",
                "state": "rejected",
                "auto_created": False,
                "created_at": "2024-01-03T00:00:00+00:00"
            }
        ]
    }
    (data_dir / "offers.json").write_text(json.dumps(offers_data))
    
    return data_dir


class TestListCommand:
    """Tests for the list command."""
    
    def test_list_def_displays_defaults_table(self, runner, populated_data_dir, monkeypatch):
        """Test list -def displays defaults table.
        
        Requirements: 14.4
        """
        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5
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
    
    def test_list_off_displays_offers_table(self, runner, populated_data_dir, monkeypatch):
        """Test list -off displays offers table.
        
        Requirements: 14.5
        """
        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5
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
    
    def test_list_all_displays_both_tables(self, runner, populated_data_dir, monkeypatch):
        """Test list -all displays both defaults and offers tables.
        
        Requirements: 14.6
        """
        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5
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
                "max_backups": 5
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
    
    def test_list_empty_data_shows_warning(self, runner, isolated_data_dir, monkeypatch):
        """Test list with empty data shows warning message.
        
        Requirements: 14.4, 14.5
        """
        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(isolated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5
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
                "max_backups": 5
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
                "max_backups": 5
            }
        
        def mock_get_data_dir(config=None):
            return populated_data_dir
        
        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["list", "-def", "-vb"])
        
        assert result.exit_code == 0
        # Verbose output should include total count
        assert "Total defaults" in result.output or "Displaying subsection" in result.output
    
    def test_list_app_displays_applications(self, runner, populated_data_dir, monkeypatch):
        """Test list -app displays applications table.
        
        Requirements: 14.1
        """
        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5
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
                "max_backups": 5
            }
        
        def mock_get_data_dir(config=None):
            return populated_data_dir
        
        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["list", "-cmd"])
        
        assert result.exit_code == 0
        assert "Commands" in result.output
        assert "vim-md" in result.output
    
    def test_list_ext_displays_extensions(self, runner, populated_data_dir, monkeypatch):
        """Test list -ext displays extensions table.
        
        Requirements: 14.1
        """
        def mock_get_config(*args, **kwargs):
            return {
                "version": "1.0.0",
                "data_dir": str(populated_data_dir),
                "verbose": False,
                "backup_enabled": False,
                "max_backups": 5
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
