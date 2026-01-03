"""
Property-Based Tests for Dry Run Idempotence

Feature: os-integration
Property 4: Dry Run No Side Effects
Validates: Requirements 7.1, 7.2

This module tests that the -dry flag prevents any actual OS changes
across all commands that support it (slap, set, chop, forget, sync).
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings, HealthCheck
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


def mock_config_factory(data_dir):
    """Create mock config functions for a given data directory."""
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

# Strategy for unique extension lists (for sync tests)
unique_extensions_list = st.lists(
    supported_extensions,
    min_size=1,
    max_size=5,
    unique=True
)


# =============================================================================
# Property 4: Dry Run No Side Effects
# Validates: Requirements 7.1, 7.2
# =============================================================================


class TestDryRunIdempotence:
    """Feature: os-integration, Property 4: Dry Run No Side Effects

    *For any* command with the `-dry` flag, the OS state before and after
    execution SHALL be identical (no side effects).

    **Validates: Requirements 7.1, 7.2**
    """

    @given(ext_flag=extension_flags)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_slap_dry_run_no_side_effects(self, ext_flag, tmp_path):
        """
        Property 4: Dry Run No Side Effects

        For any extension, slap -set -dry should:
        1. Pass dry_run=True to the platform handler
        2. NOT update os_synced status in JSON
        3. Display planned changes without executing

        **Validates: Requirements 7.1, 7.2**
        """
        runner = CliRunner()

        # Create mock executable
        exe = tmp_path / "mock_app"
        if not exe.exists():
            exe.write_text("#!/bin/bash\necho 'mock'")
            exe.chmod(0o755)

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Would set mock_app as default",
            previous_default="/Applications/TextEdit.app",
        )

        with patch("vince.commands.slap.get_config", mock_get_config):
            with patch("vince.commands.slap.get_data_dir", mock_get_data_dir):
                with patch("vince.platform.get_platform", return_value=Platform.MACOS):
                    with patch("vince.platform.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["slap", str(exe), "-set", "-dry", ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called with dry_run=True
        mock_handler.set_default.assert_called_once()
        call_args = mock_handler.set_default.call_args
        assert call_args[1]["dry_run"] is True

        # Check that os_synced was NOT set in the JSON
        defaults_data = json.loads((data_dir / "defaults.json").read_text())
        for entry in defaults_data["defaults"]:
            # os_synced should not be True (either missing or False)
            assert entry.get("os_synced", False) is False

        # Output should indicate dry run
        assert "dry run" in result.output.lower() or "would" in result.output.lower()

    @given(ext_flag=extension_flags)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_set_dry_run_no_side_effects(self, ext_flag, tmp_path):
        """
        Property 4: Dry Run No Side Effects

        For any extension, set -dry should:
        1. Pass dry_run=True to the platform handler
        2. NOT update os_synced status in JSON
        3. Display planned changes without executing

        **Validates: Requirements 7.1, 7.2**
        """
        runner = CliRunner()

        # Create mock executable
        exe = tmp_path / "mock_app"
        if not exe.exists():
            exe.write_text("#!/bin/bash\necho 'mock'")
            exe.chmod(0o755)

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Would set mock_app as default",
            previous_default=None,
        )

        with patch("vince.commands.set_cmd.get_config", mock_get_config):
            with patch("vince.commands.set_cmd.get_data_dir", mock_get_data_dir):
                with patch("vince.platform.get_platform", return_value=Platform.MACOS):
                    with patch("vince.platform.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["set", str(exe), "-dry", ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called with dry_run=True
        mock_handler.set_default.assert_called_once()
        call_args = mock_handler.set_default.call_args
        assert call_args[1]["dry_run"] is True

        # Check that os_synced was NOT set in the JSON
        defaults_data = json.loads((data_dir / "defaults.json").read_text())
        for entry in defaults_data["defaults"]:
            assert entry.get("os_synced", False) is False

        # Output should indicate dry run
        assert "dry run" in result.output.lower() or "would" in result.output.lower()

    @given(ext_flag=extension_flags)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_chop_dry_run_no_side_effects(self, ext_flag, tmp_path):
        """
        Property 4: Dry Run No Side Effects

        For any extension with an active default, chop -forget -dry should:
        1. Pass dry_run=True to the platform handler
        2. NOT actually remove the OS association
        3. Display planned changes without executing

        **Validates: Requirements 7.1, 7.2**
        """
        runner = CliRunner()

        # Create isolated data dir with active default
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)

        ext = ext_flag.replace("--", ".")
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": f"def-{ext[1:]}-000",
                    "extension": ext,
                    "application_path": "/usr/bin/existing",
                    "state": "active",
                    "os_synced": True,
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
            message=f"Would remove default for {ext}",
            previous_default="/usr/bin/existing",
        )

        with patch("vince.commands.chop.get_config", mock_get_config):
            with patch("vince.commands.chop.get_data_dir", mock_get_data_dir):
                with patch("vince.platform.get_platform", return_value=Platform.MACOS):
                    with patch("vince.platform.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["chop", "-forget", "-dry", ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called with dry_run=True
        mock_handler.remove_default.assert_called_once()
        call_args = mock_handler.remove_default.call_args
        assert call_args[1]["dry_run"] is True

        # Output should indicate dry run
        assert "dry run" in result.output.lower() or "would" in result.output.lower()

    @given(ext_flag=extension_flags)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_forget_dry_run_no_side_effects(self, ext_flag, tmp_path):
        """
        Property 4: Dry Run No Side Effects

        For any extension with an active default, forget -dry should:
        1. Pass dry_run=True to the platform handler
        2. NOT actually remove the OS association
        3. Display planned changes without executing

        **Validates: Requirements 7.1, 7.2**
        """
        runner = CliRunner()

        # Create isolated data dir with active default
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)

        ext = ext_flag.replace("--", ".")
        defaults_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": f"def-{ext[1:]}-000",
                    "extension": ext,
                    "application_path": "/usr/bin/existing",
                    "state": "active",
                    "os_synced": True,
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
            message=f"Would remove default for {ext}",
            previous_default="/usr/bin/existing",
        )

        with patch("vince.commands.forget.get_config", mock_get_config):
            with patch("vince.commands.forget.get_data_dir", mock_get_data_dir):
                with patch("vince.platform.get_platform", return_value=Platform.MACOS):
                    with patch("vince.platform.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["forget", "-dry", ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Handler should have been called with dry_run=True
        mock_handler.remove_default.assert_called_once()
        call_args = mock_handler.remove_default.call_args
        assert call_args[1]["dry_run"] is True

        # Output should indicate dry run
        assert "dry run" in result.output.lower() or "would" in result.output.lower()

    @given(extensions=unique_extensions_list)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sync_dry_run_no_side_effects(self, extensions, tmp_path):
        """
        Property 4: Dry Run No Side Effects

        For any set of active defaults, sync -dry should:
        1. Pass dry_run=True to the platform handler for each entry
        2. NOT update os_synced status in JSON
        3. Display planned changes without executing

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

        # Handler should have been called with dry_run=True for each extension
        assert mock_handler.set_default.call_count == len(extensions)
        for call in mock_handler.set_default.call_args_list:
            assert call[1]["dry_run"] is True

        # Check that os_synced was NOT updated in the JSON
        updated_data = json.loads((data_dir / "defaults.json").read_text())
        for entry in updated_data["defaults"]:
            # os_synced should still be False (not modified by dry run)
            assert entry.get("os_synced", False) is False

        # Output should indicate dry run
        assert "dry run" in result.output.lower() or "would" in result.output.lower()

    @given(ext_flag=extension_flags)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_dry_run_shows_planned_changes(self, ext_flag, tmp_path):
        """
        Property 4: Dry Run No Side Effects

        For any command with -dry flag, the output SHALL show what changes
        WOULD be made (extension, current OS default, proposed new default).

        **Validates: Requirements 7.3**
        """
        runner = CliRunner()

        # Create mock executable
        exe = tmp_path / "mock_app"
        if not exe.exists():
            exe.write_text("#!/bin/bash\necho 'mock'")
            exe.chmod(0o755)

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
        (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler with a descriptive message
        mock_handler = MagicMock()
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Would set mock_app as default for extension",
            previous_default="/Applications/TextEdit.app",
        )

        with patch("vince.commands.slap.get_config", mock_get_config):
            with patch("vince.commands.slap.get_data_dir", mock_get_data_dir):
                with patch("vince.platform.get_platform", return_value=Platform.MACOS):
                    with patch("vince.platform.get_handler", return_value=mock_handler):
                        result = runner.invoke(
                            app, ["slap", str(exe), "-set", "-dry", ext_flag]
                        )

        # Command should succeed
        assert result.exit_code == 0

        # Output should contain dry run indicator and planned changes
        output_lower = result.output.lower()
        assert "dry run" in output_lower or "would" in output_lower



class TestDryRunIdempotenceEnhanced:
    """Enhanced property-based tests for dry run idempotence.

    **Feature: coverage-completion, Property 3: Dry Run Idempotence**
    **Validates: Requirements 3.4**
    """

    @given(
        extensions=unique_extensions_list,
        num_invocations=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sync_dry_run_idempotence_multiple_invocations(
        self, extensions, num_invocations, tmp_path
    ):
        """
        **Feature: coverage-completion, Property 3: Dry Run Idempotence**

        *For any* set of default entries and any number of dry-run sync
        invocations, the OS state and JSON data files SHALL remain unchanged
        after all dry-run operations.

        **Validates: Requirements 3.4**
        """
        runner = CliRunner()

        # Create isolated data dir
        data_dir = tmp_path / ".vince"
        data_dir.mkdir(exist_ok=True)

        # Create active defaults (not synced) - use v1.1.0 to avoid migration changes
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

        initial_defaults_data = {"version": "1.1.0", "defaults": defaults_list}
        initial_offers_data = {"version": "1.0.0", "offers": []}

        (data_dir / "defaults.json").write_text(json.dumps(initial_defaults_data, indent=2))
        (data_dir / "offers.json").write_text(json.dumps(initial_offers_data, indent=2))

        # Capture initial state as parsed JSON (to avoid formatting differences)
        initial_defaults = json.loads((data_dir / "defaults.json").read_text())
        initial_offers = json.loads((data_dir / "offers.json").read_text())

        mock_get_config, mock_get_data_dir = mock_config_factory(data_dir)

        # Mock the platform handler
        mock_handler = MagicMock()
        mock_handler.get_current_default.return_value = None
        mock_handler.set_default.return_value = OperationResult(
            success=True,
            message="Would set as default",
            previous_default=None,
        )

        # Run sync -dry multiple times
        for _ in range(num_invocations):
            with patch("vince.commands.sync.get_config", mock_get_config):
                with patch("vince.commands.sync.get_data_dir", mock_get_data_dir):
                    with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
                        with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                            result = runner.invoke(app, ["sync", "-dry"])

            # Each invocation should succeed
            assert result.exit_code == 0

        # Property: JSON files should be semantically unchanged after all dry-run invocations
        final_defaults = json.loads((data_dir / "defaults.json").read_text())
        final_offers = json.loads((data_dir / "offers.json").read_text())

        # Compare semantic content (version may be migrated, but data should be same)
        assert final_defaults["defaults"] == initial_defaults["defaults"], \
            "defaults.json entries were modified by dry-run"
        assert final_offers == initial_offers, \
            "offers.json was modified by dry-run"

        # Property: os_synced should still be False for all entries
        for entry in final_defaults["defaults"]:
            assert entry.get("os_synced", False) is False, \
                f"os_synced was modified for {entry['extension']}"

    @given(
        extensions=unique_extensions_list,
        num_invocations=st.integers(min_value=1, max_value=3),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sync_dry_run_consistent_output(
        self, extensions, num_invocations, tmp_path
    ):
        """
        **Feature: coverage-completion, Property 3: Dry Run Idempotence**

        *For any* set of default entries, multiple dry-run sync invocations
        SHALL produce consistent output (same planned changes each time).

        **Validates: Requirements 3.4**
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

        # Run sync -dry multiple times and collect outputs
        outputs = []
        for _ in range(num_invocations):
            with patch("vince.commands.sync.get_config", mock_get_config):
                with patch("vince.commands.sync.get_data_dir", mock_get_data_dir):
                    with patch("vince.commands.sync.get_platform", return_value=Platform.MACOS):
                        with patch("vince.commands.sync.get_handler", return_value=mock_handler):
                            result = runner.invoke(app, ["sync", "-dry"])

            assert result.exit_code == 0
            outputs.append(result.output)

        # Property: All outputs should be identical (consistent behavior)
        if len(outputs) > 1:
            for i, output in enumerate(outputs[1:], start=2):
                assert output == outputs[0], \
                    f"Output from invocation {i} differs from first invocation"
