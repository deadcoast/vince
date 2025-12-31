"""
Unit Tests for Vince CLI reject command

Feature: vince-cli-implementation
Tests for the reject command functionality.
Requirements: 13.4, 13.5
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


class TestRejectCommand:
    """Tests for the reject command."""
    
    def test_reject_transitions_offer_to_rejected(self, runner, isolated_data_dir, monkeypatch):
        """Test reject transitions offer state to rejected.
        
        Requirements: 13.4
        """
        # Pre-populate offers.json with an existing offer in created state
        offers_data = {
            "version": "1.0.0",
            "offers": [{
                "offer_id": "my-offer",
                "default_id": "def-md-000",
                "state": "created",
                "auto_created": False,
                "created_at": "2024-01-01T00:00:00+00:00"
            }]
        }
        (isolated_data_dir / "offers.json").write_text(json.dumps(offers_data))
        
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
        
        monkeypatch.setattr("vince.commands.reject.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.reject.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["reject", "my-offer"])
        
        assert result.exit_code == 0
        assert "rejected" in result.output.lower() or "✓" in result.output
        
        # Verify offers.json was updated
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 1
        assert offers_data["offers"][0]["offer_id"] == "my-offer"
        assert offers_data["offers"][0]["state"] == "rejected"
    
    def test_reject_active_offer(self, runner, isolated_data_dir, monkeypatch):
        """Test reject can transition active offer to rejected.
        
        Requirements: 13.4
        """
        # Pre-populate offers.json with an active offer
        offers_data = {
            "version": "1.0.0",
            "offers": [{
                "offer_id": "active-offer",
                "default_id": "def-py-000",
                "state": "active",
                "auto_created": True,
                "created_at": "2024-01-01T00:00:00+00:00",
                "used_at": "2024-01-02T00:00:00+00:00"
            }]
        }
        (isolated_data_dir / "offers.json").write_text(json.dumps(offers_data))
        
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
        
        monkeypatch.setattr("vince.commands.reject.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.reject.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["reject", "active-offer"])
        
        assert result.exit_code == 0
        
        # Verify state changed to rejected
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert offers_data["offers"][0]["state"] == "rejected"
    
    def test_reject_error_offer_not_found(self, runner, isolated_data_dir, monkeypatch):
        """Test reject raises error when offer_id does not exist.
        
        Requirements: 13.5
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
        
        monkeypatch.setattr("vince.commands.reject.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.reject.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["reject", "nonexistent-offer"])
        
        # Should fail with VE104 error
        assert result.exit_code == 1
        assert "VE104" in result.output or "not found" in result.output.lower()
    
    def test_reject_with_complete_delete_flag(self, runner, isolated_data_dir, monkeypatch):
        """Test reject with -. flag completely removes offer from data file.
        
        Requirements: 13.2
        """
        # Pre-populate offers.json with an existing offer
        offers_data = {
            "version": "1.0.0",
            "offers": [{
                "offer_id": "delete-me",
                "default_id": "def-md-000",
                "state": "created",
                "auto_created": False,
                "created_at": "2024-01-01T00:00:00+00:00"
            }]
        }
        (isolated_data_dir / "offers.json").write_text(json.dumps(offers_data))
        
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
        
        monkeypatch.setattr("vince.commands.reject.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.reject.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["reject", "delete-me", "-."])
        
        assert result.exit_code == 0
        assert "deleted" in result.output.lower() or "✓" in result.output
        
        # Verify offer was completely removed from data file
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 0
    
    def test_reject_verbose_output(self, runner, isolated_data_dir, monkeypatch):
        """Test reject with verbose flag shows additional info.
        
        Requirements: 13.3
        """
        # Pre-populate offers.json with an existing offer
        offers_data = {
            "version": "1.0.0",
            "offers": [{
                "offer_id": "verbose-test",
                "default_id": "def-md-000",
                "state": "created",
                "auto_created": False,
                "created_at": "2024-01-01T00:00:00+00:00"
            }]
        }
        (isolated_data_dir / "offers.json").write_text(json.dumps(offers_data))
        
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
        
        monkeypatch.setattr("vince.commands.reject.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.reject.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["reject", "verbose-test", "-vb"])
        
        assert result.exit_code == 0
        # Verbose output should include state change info
        assert "Rejecting offer" in result.output or "State changed" in result.output or "Found offer" in result.output
