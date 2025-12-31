"""
Unit Tests for Vince CLI offer command

Feature: vince-cli-implementation
Tests for the offer command functionality.
Requirements: 12.5, 12.6, 12.7
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


class TestOfferCommand:
    """Tests for the offer command."""
    
    def test_offer_creates_offer_entry(self, runner, mock_executable, isolated_data_dir, monkeypatch):
        """Test offer creates a new offer entry in created state.
        
        Requirements: 12.5
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
        
        monkeypatch.setattr("vince.commands.offer.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["offer", "my-editor", str(mock_executable), "--md"])
        
        assert result.exit_code == 0
        assert "Offer created" in result.output or "✓" in result.output
        
        # Verify offers.json was updated
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 1
        assert offers_data["offers"][0]["offer_id"] == "my-editor"
        assert offers_data["offers"][0]["state"] == "created"
        assert offers_data["offers"][0]["auto_created"] is False
    
    def test_offer_creates_default_if_not_exists(self, runner, mock_executable, isolated_data_dir, monkeypatch):
        """Test offer creates a default entry if one doesn't exist for the extension.
        
        Requirements: 12.5
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
        
        monkeypatch.setattr("vince.commands.offer.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["offer", "code-py", str(mock_executable), "--py"])
        
        assert result.exit_code == 0
        
        # Verify defaults.json was also updated
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["extension"] == ".py"
        assert defaults_data["defaults"][0]["state"] == "pending"
    
    def test_offer_uses_existing_default(self, runner, mock_executable, isolated_data_dir, monkeypatch):
        """Test offer uses existing default entry if one exists.
        
        Requirements: 12.5
        """
        # Pre-populate defaults.json with an existing default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [{
                "id": "def-md-000",
                "extension": ".md",
                "application_path": "/usr/bin/existing",
                "state": "active",
                "created_at": "2024-01-01T00:00:00+00:00"
            }]
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        
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
        
        monkeypatch.setattr("vince.commands.offer.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["offer", "my-md-editor", str(mock_executable), "--md"])
        
        assert result.exit_code == 0
        
        # Verify offer references the existing default
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 1
        assert offers_data["offers"][0]["default_id"] == "def-md-000"
        
        # Verify no new default was created
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
    
    def test_offer_error_when_offer_exists(self, runner, mock_executable, isolated_data_dir, monkeypatch):
        """Test offer raises error when offer_id already exists.
        
        Requirements: 12.6
        """
        # Pre-populate offers.json with an existing offer
        offers_data = {
            "version": "1.0.0",
            "offers": [{
                "offer_id": "existing-offer",
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
        
        monkeypatch.setattr("vince.commands.offer.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["offer", "existing-offer", str(mock_executable), "--md"])
        
        # Should fail with error
        assert result.exit_code == 1
        assert "VE303" in result.output or "Offer already exists" in result.output
    
    def test_offer_error_invalid_offer_id_format(self, runner, mock_executable, isolated_data_dir, monkeypatch):
        """Test offer raises error for invalid offer_id format.
        
        Requirements: 12.7
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
        
        monkeypatch.setattr("vince.commands.offer.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_get_data_dir)
        
        # Test with uppercase (invalid)
        result = runner.invoke(app, ["offer", "Invalid-ID", str(mock_executable), "--md"])
        
        assert result.exit_code == 1
        assert "VE103" in result.output or "Invalid offer_id" in result.output
    
    def test_offer_error_reserved_name(self, runner, mock_executable, isolated_data_dir, monkeypatch):
        """Test offer raises error for reserved offer_id names.
        
        Requirements: 12.7
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
        
        monkeypatch.setattr("vince.commands.offer.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_get_data_dir)
        
        # Test with reserved name
        result = runner.invoke(app, ["offer", "help", str(mock_executable), "--md"])
        
        assert result.exit_code == 1
        assert "VE103" in result.output or "Invalid offer_id" in result.output
    
    def test_offer_verbose_output(self, runner, mock_executable, isolated_data_dir, monkeypatch):
        """Test offer with verbose flag shows additional info.
        
        Requirements: 12.4
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
        
        monkeypatch.setattr("vince.commands.offer.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["offer", "verbose-test", str(mock_executable), "--md", "-vb"])
        
        assert result.exit_code == 0
        # Verbose output should include additional info
        assert "Validating offer_id" in result.output or "Processing path" in result.output
    
    def test_offer_error_no_extension_specified(self, runner, mock_executable, isolated_data_dir, monkeypatch):
        """Test offer raises error when no extension is specified.
        
        Requirements: 12.3
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
        
        monkeypatch.setattr("vince.commands.offer.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_get_data_dir)
        
        result = runner.invoke(app, ["offer", "my-offer", str(mock_executable)])
        
        # Should fail with error about no extension
        assert result.exit_code == 1
        assert "VE102" in result.output or "extension" in result.output.lower()
