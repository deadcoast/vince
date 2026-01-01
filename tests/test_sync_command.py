"""
Property-Based Tests for Sync Command

Feature: os-integration
Property 6: Sync Applies All Active Defaults
Validates: Requirements 6.1, 6.2, 6.3, 6.4

This module tests that the sync command properly applies all active defaults
to the OS and handles various scenarios correctly.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import HealthCheck, given, settings
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
def isolated_data_dir(tmp_path):
    """Provide isolated data directory with empty data files."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
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

# Strategy for generating a list of unique extensions (1-5 extensions)
unique_extensions_list = st.lists(
    supported_extensions,
    min_size=1,
    max_size=5,
    unique=True,
)


# =============================================================================
# Unit Tests for Sync Command
# =============================================================================


class TestSyncCommandBasic:
    """Basic unit tests for sync command.
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """

    def test_sync_no_active_defaults(self, runner, isolated_data_dir, monkeypatch):
        """Test sync with no active defaults shows appropriate message.
        
        Requirements: 6.1
        """
        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.sync.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.sync.get_data_dir", mock_get_data_dir)

        result = runner.invoke(app, ["sync"])

        assert result.exit_code == 0
        assert "No active defaults to sync" in result.output

    def test_sync_applies_active_defaults(self, runner, isolated_data_dir, monkeypatch):
        """Test sync applies all active defaults to OS.
        
        Requirements: 6.1
        """
        # Pre-populate with active defaults
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/app1",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                },
                {
                    "id": "def-py-001",
                    "extension": ".py",
                    "application_path": "/usr/bin/app2",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                },
            ],
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))

        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.sync.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.sync.get_data_dir", mock_get_data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Set as default",
            previous_default=None,
        )
        mock_handler.get_current_default.return_value = None

        with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["sync"])

        assert result.exit_code == 0
        # Handler should be called for each active default
        assert mock_handler.set_default.call_count == 2

    def test_sync_skips_already_synced(self, runner, isolated_data_dir, monkeypatch):
        """Test sync skips entries that are already correctly configured.
        
        Requirements: 6.2
        """
        # Pre-populate with already-synced default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/app1",
                    "state": "active",
                    "os_synced": True,
                    "created_at": "2024-01-01T00:00:00+00:00",
                },
            ],
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))

        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.sync.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.sync.get_data_dir", mock_get_data_dir)

        # Mock the platform handler - return matching path
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = "/usr/bin/app1"
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Set as default",
            previous_default=None,
        )

        with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["sync", "-vb"])

        assert result.exit_code == 0
        # Handler's set_default should NOT be called (already synced)
        mock_handler.set_default.assert_not_called()
        assert "skipping" in result.output.lower() or "already synced" in result.output.lower()

    def test_sync_reports_failures(self, runner, isolated_data_dir, monkeypatch):
        """Test sync reports failures for each extension.
        
        Requirements: 6.3
        """
        # Pre-populate with active defaults
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/app1",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                },
            ],
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))

        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.sync.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.sync.get_data_dir", mock_get_data_dir)

        # Mock the platform handler to fail
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = None
        mock_handler.set_default.return_value = OperationResult(
            success=False,
            message="OS operation failed",
            error_code="VE605",
        )

        with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["sync"])

        # Should report failure
        assert "Failed" in result.output or "failed" in result.output

    def test_sync_continues_after_failure(self, runner, isolated_data_dir, monkeypatch):
        """Test sync continues with remaining entries after a failure.
        
        Requirements: 6.4
        """
        # Pre-populate with multiple active defaults
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/app1",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                },
                {
                    "id": "def-py-001",
                    "extension": ".py",
                    "application_path": "/usr/bin/app2",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                },
            ],
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))

        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.sync.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.sync.get_data_dir", mock_get_data_dir)

        # Mock handler: first call fails, second succeeds
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = None
        mock_handler.set_default.side_effect = [
            OperationResult(success=False, message="Failed", error_code="VE605"),
            OperationResult(success=True, message="Success", previous_default=None),
        ]

        with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                runner.invoke(app, ["sync"])

        # Both should have been attempted
        assert mock_handler.set_default.call_count == 2

    def test_sync_dry_run(self, runner, isolated_data_dir, monkeypatch):
        """Test sync -dry shows planned changes without executing.
        
        Requirements: 7.1, 7.2
        """
        # Pre-populate with active default
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/app1",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                },
            ],
        }
        (isolated_data_dir / "defaults.json").write_text(json.dumps(defaults_data))

        mock_get_config, mock_get_data_dir = mock_config_factory(isolated_data_dir)
        monkeypatch.setattr("vince.commands.sync.get_config", mock_get_config)
        monkeypatch.setattr("vince.commands.sync.get_data_dir", mock_get_data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = None
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Would set as default",
            previous_default=None,
        )

        with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
            with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                result = runner.invoke(app, ["sync", "-dry"])

        assert result.exit_code == 0
        assert "would" in result.output.lower() or "dry run" in result.output.lower()
        # Handler should be called with dry_run=True
        mock_handler.set_default.assert_called_once()
        call_args = mock_handler.set_default.call_args
        assert call_args[1]["dry_run"] is True


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestSyncCommandProperties:
    """Property-based tests for sync command.

    **Property 6: Sync Applies All Active Defaults**
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
    """

    @given(extensions=unique_extensions_list)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sync_applies_all_active_defaults(self, extensions, tmp_path):
        """
        Property 6: Sync Applies All Active Defaults

        For any set of active defaults in the JSON store, after running sync,
        the platform handler's set_default should be called for each entry
        that is not already synced.

        **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
        """
        runner = CliRunner()

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)

        # Create active defaults for each extension
        defaults_list = []
        for i, ext in enumerate(extensions):
            defaults_list.append({
                "id": f"def-{ext[1:]}-{i:03d}",
                "extension": ext,
                "application_path": f"/usr/bin/app{i}",
                "state": "active",
                "created_at": "2024-01-01T00:00:00+00:00",
            })

        defaults_data = {"version": "1.0.0", "defaults": defaults_list}
        (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = None  # Not synced
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Set as default",
            previous_default=None,
        )

        with patch("vince.commands.sync.get_config", mock_get_config):
            with patch("vince.commands.sync.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                        result = runner.invoke(app, ["sync"])

        # Command should succeed
        assert result.exit_code == 0

        # Handler should be called for each active default
        assert mock_handler.set_default.call_count == len(extensions)

        # Verify each extension was processed
        called_extensions = set()
        for call in mock_handler.set_default.call_args_list:
            called_extensions.add(call[0][0])

        assert called_extensions == set(extensions)

    @given(extensions=unique_extensions_list)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sync_skips_already_synced_entries(self, extensions, tmp_path):
        """
        Property 6: Sync Applies All Active Defaults

        For any set of active defaults that are already synced (os_synced=True
        and OS default matches), sync should skip them.

        **Validates: Requirements 6.2**
        """
        runner = CliRunner()

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)

        # Create active defaults marked as synced
        defaults_list = []
        for i, ext in enumerate(extensions):
            defaults_list.append({
                "id": f"def-{ext[1:]}-{i:03d}",
                "extension": ext,
                "application_path": f"/usr/bin/app{i}",
                "state": "active",
                "os_synced": True,
                "created_at": "2024-01-01T00:00:00+00:00",
            })

        defaults_data = {"version": "1.0.0", "defaults": defaults_list}
        (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler - return matching paths
        def mock_get_current_default(ext):
            for d in defaults_list:
                if d["extension"] == ext:
                    return d["application_path"]
            return None

        mock_handler = MagicMock()
        mock_handler.get_current_default.side_effect = mock_get_current_default
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Set as default",
            previous_default=None,
        )

        with patch("vince.commands.sync.get_config", mock_get_config):
            with patch("vince.commands.sync.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                        result = runner.invoke(app, ["sync", "-vb"])

        # Command should succeed
        assert result.exit_code == 0

        # Handler's set_default should NOT be called (all already synced)
        mock_handler.set_default.assert_not_called()

    @given(extensions=unique_extensions_list)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sync_continues_after_failures(self, extensions, tmp_path):
        """
        Property 6: Sync Applies All Active Defaults

        For any set of active defaults, if some fail to sync, the command
        should continue with remaining entries.

        **Validates: Requirements 6.4**
        """
        if len(extensions) < 2:
            # Need at least 2 extensions to test continuation
            return

        runner = CliRunner()

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)

        # Create active defaults
        defaults_list = []
        for i, ext in enumerate(extensions):
            defaults_list.append({
                "id": f"def-{ext[1:]}-{i:03d}",
                "extension": ext,
                "application_path": f"/usr/bin/app{i}",
                "state": "active",
                "created_at": "2024-01-01T00:00:00+00:00",
            })

        defaults_data = {"version": "1.0.0", "defaults": defaults_list}
        (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock handler: first call fails, rest succeed
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = None
        results = [OperationResult(success=False, message="Failed", error_code="VE605")]
        results.extend([
            OperationResult(success=True, message="Success", previous_default=None)
            for _ in range(len(extensions) - 1)
        ])
        mock_handler.set_default.side_effect = results

        with patch("vince.commands.sync.get_config", mock_get_config):
            with patch("vince.commands.sync.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                        runner.invoke(app, ["sync"])

        # All entries should have been attempted
        assert mock_handler.set_default.call_count == len(extensions)

    @given(extensions=unique_extensions_list)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sync_dry_run_no_side_effects(self, extensions, tmp_path):
        """
        Property 6: Sync Applies All Active Defaults

        For any set of active defaults, sync -dry should not modify the
        os_synced status in the JSON store.

        **Validates: Requirements 7.1, 7.2**
        """
        runner = CliRunner()

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)

        # Create active defaults (not synced)
        defaults_list = []
        for i, ext in enumerate(extensions):
            defaults_list.append({
                "id": f"def-{ext[1:]}-{i:03d}",
                "extension": ext,
                "application_path": f"/usr/bin/app{i}",
                "state": "active",
                "os_synced": False,
                "created_at": "2024-01-01T00:00:00+00:00",
            })

        defaults_data = {"version": "1.0.0", "defaults": defaults_list}
        (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = None
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Would set as default",
            previous_default=None,
        )

        with patch("vince.commands.sync.get_config", mock_get_config):
            with patch("vince.commands.sync.get_data_dir", mock_get_data_dir):
                with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
                    with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                        result = runner.invoke(app, ["sync", "-dry"])

        # Command should succeed
        assert result.exit_code == 0

        # Check that os_synced was NOT updated in the JSON
        updated_data = json.loads((data_dir / "defaults.json").read_text())
        for entry in updated_data["defaults"]:
            # os_synced should still be False (not modified by dry run)
            assert entry.get("os_synced", False) is False
