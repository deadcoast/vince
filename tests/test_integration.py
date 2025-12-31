"""
Integration Tests for Vince CLI command flows

Feature: vince-cli-implementation
Tests for end-to-end command flows and interactions.
Requirements: 15.4
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


def create_mock_config(data_dir):
    """Create a mock config function for testing."""

    def mock_get_config(*args, **kwargs):
        return {
            "version": "1.0.0",
            "data_dir": str(data_dir),
            "verbose": False,
            "backup_enabled": False,
            "max_backups": 5,
        }

    return mock_get_config


def create_mock_data_dir(data_dir):
    """Create a mock data dir function for testing."""

    def mock_get_data_dir(config=None):
        return data_dir

    return mock_get_data_dir


class TestSlapListChopFlow:
    """Integration tests for slap → list → chop flow.

    Requirements: 15.4
    """

    def test_slap_list_chop_complete_flow(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test complete flow: slap creates default, list shows it, chop removes it.

        This tests the full lifecycle of a default entry:
        1. slap creates a pending default
        2. list -def shows the default
        3. chop -forget removes the default
        4. list -def no longer shows the default
        """
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        # Patch all commands
        monkeypatch.setattr("vince.commands.slap.get_config", mock_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.chop.get_config", mock_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_data_dir)

        # Step 1: slap creates a pending default
        result = runner.invoke(app, ["slap", str(mock_executable), "--md"])
        assert result.exit_code == 0
        assert "Default identified" in result.output or "✓" in result.output

        # Verify default was created
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "pending"
        assert defaults_data["defaults"][0]["extension"] == ".md"

        # Step 2: list -def shows the default
        result = runner.invoke(app, ["list", "-def"])
        assert result.exit_code == 0
        assert ".md" in result.output

        # Step 3: chop -forget removes the default
        result = runner.invoke(app, ["chop", "--md", "-forget"])
        assert result.exit_code == 0
        assert "Default removed" in result.output or "✓" in result.output

        # Verify default state changed to removed
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "removed"

        # Step 4: list -def no longer shows the removed default
        result = runner.invoke(app, ["list", "-def"])
        assert result.exit_code == 0
        # Removed defaults should not appear in list
        assert ".md" not in result.output or "No defaults found" in result.output

    def test_slap_set_list_chop_flow(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test flow with slap -set: creates active default, list shows it, chop removes it."""
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        monkeypatch.setattr("vince.commands.slap.get_config", mock_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.chop.get_config", mock_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_data_dir)

        # Step 1: slap -set creates an active default
        result = runner.invoke(app, ["slap", str(mock_executable), "-set", "--py"])
        assert result.exit_code == 0
        assert "Default set" in result.output or "✓" in result.output

        # Verify default was created with active state
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "active"

        # Step 2: list -def shows the active default
        result = runner.invoke(app, ["list", "-def"])
        assert result.exit_code == 0
        assert ".py" in result.output

        # Step 3: chop -forget removes the default
        result = runner.invoke(app, ["chop", "--py", "-forget"])
        assert result.exit_code == 0

        # Verify default state changed to removed
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "removed"


class TestSlapSetOfferAutoCreation:
    """Integration tests for slap -set → offer auto-creation flow.

    Requirements: 15.4
    """

    def test_slap_set_auto_creates_offer(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test that slap -set automatically creates an offer entry.

        This tests:
        1. slap -set creates an active default
        2. An offer is automatically created
        3. list -off shows the auto-created offer
        """
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        monkeypatch.setattr("vince.commands.slap.get_config", mock_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_data_dir)

        # Step 1: slap -set creates active default and auto-creates offer
        result = runner.invoke(app, ["slap", str(mock_executable), "-set", "--md"])
        assert result.exit_code == 0
        assert "Default set" in result.output or "✓" in result.output
        assert "Offer created" in result.output

        # Verify default was created
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "active"
        default_id = defaults_data["defaults"][0]["id"]

        # Verify offer was auto-created
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 1
        assert offers_data["offers"][0]["auto_created"] is True
        assert offers_data["offers"][0]["default_id"] == default_id
        assert offers_data["offers"][0]["state"] == "created"

        # Step 2: list -off shows the auto-created offer
        result = runner.invoke(app, ["list", "-off"])
        assert result.exit_code == 0
        assert "Offers" in result.output
        # The offer_id should contain the app name and extension
        assert "mock" in result.output.lower() or "md" in result.output.lower()

    def test_slap_set_offer_references_correct_default(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test that auto-created offer correctly references the default entry."""
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        monkeypatch.setattr("vince.commands.slap.get_config", mock_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_data_dir)

        # Create default with slap -set
        result = runner.invoke(app, ["slap", str(mock_executable), "-set", "--json"])
        assert result.exit_code == 0

        # Verify the offer references the correct default
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())

        default_id = defaults_data["defaults"][0]["id"]
        offer_default_id = offers_data["offers"][0]["default_id"]

        assert default_id == offer_default_id


class TestOfferRejectFlow:
    """Integration tests for offer → reject flow.

    Requirements: 15.4
    """

    def test_offer_reject_complete_flow(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test complete flow: offer creates entry, reject removes it.

        This tests:
        1. offer creates a new offer entry
        2. list -off shows the offer
        3. reject transitions offer to rejected state
        4. list -off no longer shows the rejected offer
        """
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        monkeypatch.setattr("vince.commands.offer.get_config", mock_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.reject.get_config", mock_config)
        monkeypatch.setattr("vince.commands.reject.get_data_dir", mock_data_dir)

        # Step 1: offer creates a new offer entry
        result = runner.invoke(
            app, ["offer", "my-editor", str(mock_executable), "--md"]
        )
        assert result.exit_code == 0
        assert "Offer created" in result.output or "✓" in result.output

        # Verify offer was created
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 1
        assert offers_data["offers"][0]["offer_id"] == "my-editor"
        assert offers_data["offers"][0]["state"] == "created"

        # Step 2: list -off shows the offer
        result = runner.invoke(app, ["list", "-off"])
        assert result.exit_code == 0
        assert "my-editor" in result.output

        # Step 3: reject transitions offer to rejected state
        result = runner.invoke(app, ["reject", "my-editor"])
        assert result.exit_code == 0
        assert "rejected" in result.output.lower() or "✓" in result.output

        # Verify offer state changed to rejected
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert offers_data["offers"][0]["state"] == "rejected"

        # Step 4: list -off no longer shows the rejected offer
        result = runner.invoke(app, ["list", "-off"])
        assert result.exit_code == 0
        # Rejected offers should not appear in list
        assert "my-editor" not in result.output or "No offers found" in result.output

    def test_offer_reject_with_complete_delete(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test offer → reject with -. flag completely removes the offer."""
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        monkeypatch.setattr("vince.commands.offer.get_config", mock_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.reject.get_config", mock_config)
        monkeypatch.setattr("vince.commands.reject.get_data_dir", mock_data_dir)

        # Create offer
        result = runner.invoke(
            app, ["offer", "delete-me", str(mock_executable), "--py"]
        )
        assert result.exit_code == 0

        # Verify offer exists
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 1

        # Reject with complete delete flag
        result = runner.invoke(app, ["reject", "delete-me", "-."])
        assert result.exit_code == 0

        # Verify offer was completely removed
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 0

    def test_multiple_offers_reject_one(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test rejecting one offer doesn't affect others."""
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        monkeypatch.setattr("vince.commands.offer.get_config", mock_config)
        monkeypatch.setattr("vince.commands.offer.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.reject.get_config", mock_config)
        monkeypatch.setattr("vince.commands.reject.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_data_dir)

        # Create two offers
        result = runner.invoke(
            app, ["offer", "offer-one", str(mock_executable), "--md"]
        )
        assert result.exit_code == 0

        result = runner.invoke(
            app, ["offer", "offer-two", str(mock_executable), "--py"]
        )
        assert result.exit_code == 0

        # Verify both offers exist
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(offers_data["offers"]) == 2

        # Reject only one offer
        result = runner.invoke(app, ["reject", "offer-one"])
        assert result.exit_code == 0

        # Verify only offer-one was rejected
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        offer_one = next(
            o for o in offers_data["offers"] if o["offer_id"] == "offer-one"
        )
        offer_two = next(
            o for o in offers_data["offers"] if o["offer_id"] == "offer-two"
        )

        assert offer_one["state"] == "rejected"
        assert offer_two["state"] == "created"

        # list -off should only show offer-two
        result = runner.invoke(app, ["list", "-off"])
        assert result.exit_code == 0
        assert "offer-two" in result.output
        assert "offer-one" not in result.output


class TestComplexFlows:
    """Integration tests for complex multi-command flows.

    Requirements: 15.4
    """

    def test_full_lifecycle_slap_offer_reject_chop(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test full lifecycle: slap → offer → reject → chop."""
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        # Patch all commands
        for cmd in ["slap", "offer", "reject", "chop", "list_cmd"]:
            monkeypatch.setattr(f"vince.commands.{cmd}.get_config", mock_config)
            monkeypatch.setattr(f"vince.commands.{cmd}.get_data_dir", mock_data_dir)

        # Step 1: slap creates pending default
        result = runner.invoke(app, ["slap", str(mock_executable), "--md"])
        assert result.exit_code == 0

        # Step 2: offer creates an offer for the default
        result = runner.invoke(
            app, ["offer", "my-md-editor", str(mock_executable), "--md"]
        )
        assert result.exit_code == 0

        # Verify both exist
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert len(offers_data["offers"]) == 1

        # Step 3: reject the offer
        result = runner.invoke(app, ["reject", "my-md-editor"])
        assert result.exit_code == 0

        # Step 4: chop the default
        result = runner.invoke(app, ["chop", "--md", "-forget"])
        assert result.exit_code == 0

        # Verify final states
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        offers_data = json.loads((isolated_data_dir / "offers.json").read_text())

        assert defaults_data["defaults"][0]["state"] == "removed"
        assert offers_data["offers"][0]["state"] == "rejected"

    def test_set_forget_set_again_flow(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test set → forget → set again flow (re-activation)."""
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        for cmd in ["set_cmd", "forget", "list_cmd"]:
            monkeypatch.setattr(f"vince.commands.{cmd}.get_config", mock_config)
            monkeypatch.setattr(f"vince.commands.{cmd}.get_data_dir", mock_data_dir)

        # Step 1: set creates active default
        result = runner.invoke(app, ["set", str(mock_executable), "--md"])
        assert result.exit_code == 0

        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "active"

        # Step 2: forget removes the default
        result = runner.invoke(app, ["forget", "--md"])
        assert result.exit_code == 0

        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "removed"

        # Step 3: set again re-activates (creates new entry or updates)
        result = runner.invoke(app, ["set", str(mock_executable), "--md"])
        assert result.exit_code == 0

        # Verify default is active again
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        # Should have an active default for .md
        active_defaults = [
            d
            for d in defaults_data["defaults"]
            if d["state"] == "active" and d["extension"] == ".md"
        ]
        assert len(active_defaults) >= 1
