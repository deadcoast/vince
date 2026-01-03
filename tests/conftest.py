"""
Shared Test Fixtures for Vince CLI

This module provides shared pytest fixtures used across multiple test files.
Consolidating fixtures here reduces code duplication and improves test maintainability.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import json
from pathlib import Path
from typing import Callable
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from vince.platform.base import OperationResult, Platform


# =============================================================================
# Core Fixtures (Requirements: 5.1, 5.2, 5.3, 5.4)
# =============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CLI test runner.

    Returns:
        CliRunner instance for invoking CLI commands in tests.

    Requirements: 5.4
    """
    return CliRunner()


@pytest.fixture
def mock_executable(tmp_path: Path) -> Path:
    """Create a mock executable file for testing.

    Creates a simple bash script that can be used as a mock application
    in tests that require an executable file path.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created mock executable.

    Requirements: 5.2
    """
    exe = tmp_path / "mock_app"
    exe.write_text("#!/bin/bash\necho 'mock'")
    exe.chmod(0o755)
    return exe


@pytest.fixture
def isolated_data_dir(tmp_path: Path) -> Path:
    """Provide isolated data directory with empty JSON files.

    Creates a .vince directory with empty defaults.json and offers.json
    files for testing commands in isolation.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 5.3
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "defaults.json").write_text('{"version": "1.1.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    return data_dir


@pytest.fixture
def populated_data_dir(tmp_path: Path) -> Path:
    """Provide isolated data directory with sample data.

    Creates a .vince directory with pre-populated defaults and offers
    for testing list and query operations.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory with sample data.

    Requirements: 5.3
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)

    # Create sample defaults
    defaults_data = {
        "version": "1.1.0",
        "defaults": [
            {
                "id": "def-md-000",
                "extension": ".md",
                "application_path": "/usr/bin/vim",
                "application_name": "vim",
                "state": "active",
                "os_synced": True,
                "created_at": "2024-01-01T00:00:00+00:00",
            },
            {
                "id": "def-py-001",
                "extension": ".py",
                "application_path": "/usr/bin/code",
                "application_name": "code",
                "state": "pending",
                "os_synced": False,
                "created_at": "2024-01-02T00:00:00+00:00",
            },
            {
                "id": "def-txt-002",
                "extension": ".txt",
                "application_path": "/usr/bin/nano",
                "application_name": "nano",
                "state": "removed",
                "os_synced": False,
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


# =============================================================================
# Platform Mock Fixtures (Requirements: 5.5)
# =============================================================================


@pytest.fixture
def mock_platform_handler() -> MagicMock:
    """Provide a mock platform handler for OS integration tests.

    Creates a MagicMock configured to simulate a macOS platform handler
    with successful operation results by default.

    Returns:
        MagicMock configured as a platform handler.

    Requirements: 5.5
    """
    handler = MagicMock()
    handler.platform = Platform.MACOS

    # Configure default successful responses
    handler.set_default.return_value = OperationResult(
        success=True,
        message="Mock: Set as default",
        previous_default=None,
    )
    handler.remove_default.return_value = OperationResult(
        success=True,
        message="Mock: Removed default",
        previous_default="/usr/bin/previous",
    )
    handler.get_current_default.return_value = None
    handler.verify_application.return_value = MagicMock(
        path=Path("/usr/bin/mock"),
        name="mock_app",
        bundle_id=None,
        executable=None,
    )

    return handler


@pytest.fixture
def mock_get_handler(mock_platform_handler: MagicMock) -> Callable[[], MagicMock]:
    """Provide a factory function that returns the mock platform handler.

    This fixture is useful for patching vince.platform.get_handler.

    Args:
        mock_platform_handler: The mock handler fixture.

    Returns:
        A callable that returns the mock platform handler.

    Requirements: 5.5
    """
    def _get_handler() -> MagicMock:
        return mock_platform_handler

    return _get_handler


@pytest.fixture
def mock_unsupported_platform() -> MagicMock:
    """Provide a mock handler for unsupported platform scenarios.

    Creates a MagicMock configured to simulate an unsupported platform,
    useful for testing platform detection and fallback behavior.

    Returns:
        MagicMock configured as an unsupported platform handler.

    Requirements: 5.5
    """
    handler = MagicMock()
    handler.platform = Platform.UNSUPPORTED

    # Configure responses that indicate unsupported operations
    handler.set_default.return_value = OperationResult(
        success=False,
        message="Platform not supported",
        error_code="VE601",
    )
    handler.remove_default.return_value = OperationResult(
        success=False,
        message="Platform not supported",
        error_code="VE601",
    )
    handler.get_current_default.return_value = None
    handler.verify_application.side_effect = NotImplementedError(
        "Platform not supported"
    )

    return handler


# =============================================================================
# Helper Functions for Test Configuration
# =============================================================================


def create_mock_config(data_dir: Path) -> Callable[..., dict]:
    """Create a mock config function for testing.

    Factory function that creates a mock get_config function
    pointing to the specified data directory.

    Args:
        data_dir: Path to the test data directory.

    Returns:
        A callable that returns a config dictionary.
    """
    def mock_get_config(*args, **kwargs) -> dict:
        return {
            "version": "1.0.0",
            "data_dir": str(data_dir),
            "verbose": False,
            "backup_enabled": False,
            "max_backups": 5,
        }

    return mock_get_config


def create_mock_data_dir(data_dir: Path) -> Callable[..., Path]:
    """Create a mock data dir function for testing.

    Factory function that creates a mock get_data_dir function
    returning the specified data directory.

    Args:
        data_dir: Path to the test data directory.

    Returns:
        A callable that returns the data directory path.
    """
    def mock_get_data_dir(config=None) -> Path:  # noqa: ARG001
        return data_dir

    return mock_get_data_dir


# =============================================================================
# Trackable Mock Platform Handler Fixture (Requirements: 20.1)
# =============================================================================


@pytest.fixture
def trackable_mock_handler():
    """Provide a trackable MockPlatformHandler for detailed verification.

    This fixture provides the custom MockPlatformHandler class that tracks
    all method calls and supports configurable failure modes.

    Returns:
        MockPlatformHandler instance with call tracking.

    Requirements: 20.1
    """
    from tests.mock_platform_handler import MockPlatformHandler

    return MockPlatformHandler()


# =============================================================================
# Corrupted Data Fixtures (Requirements: 2.4, 2.5, 2.6, 2.7, 2.8)
# =============================================================================


@pytest.fixture
def corrupted_defaults_json(tmp_path: Path) -> Path:
    """Provide data directory with corrupted defaults.json.

    Creates a .vince directory with an invalid JSON file for testing
    error handling of corrupted data files.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory with corrupted defaults.json.

    Requirements: 2.4
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    # Write invalid JSON (missing closing brace)
    (data_dir / "defaults.json").write_text('{"version": "1.1.0", "defaults": [')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    return data_dir


@pytest.fixture
def corrupted_defaults_invalid_state(tmp_path: Path) -> Path:
    """Provide data directory with defaults.json containing invalid state.

    Creates a .vince directory with a defaults.json file that has an
    invalid state value for testing schema validation.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 2.5
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    defaults_data = {
        "version": "1.1.0",
        "defaults": [
            {
                "id": "def-md-000",
                "extension": ".md",
                "application_path": "/usr/bin/vim",
                "application_name": "vim",
                "state": "invalid_state",  # Invalid state value
                "os_synced": False,
                "created_at": "2024-01-01T00:00:00+00:00",
            }
        ],
    }
    (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    return data_dir


@pytest.fixture
def corrupted_defaults_missing_field(tmp_path: Path) -> Path:
    """Provide data directory with defaults.json missing required field.

    Creates a .vince directory with a defaults.json file that is missing
    a required field for testing schema validation.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 2.6
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    defaults_data = {
        "version": "1.1.0",
        "defaults": [
            {
                "id": "def-md-000",
                # Missing "extension" field
                "application_path": "/usr/bin/vim",
                "application_name": "vim",
                "state": "active",
                "os_synced": False,
                "created_at": "2024-01-01T00:00:00+00:00",
            }
        ],
    }
    (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    return data_dir


@pytest.fixture
def corrupted_offers_json(tmp_path: Path) -> Path:
    """Provide data directory with corrupted offers.json.

    Creates a .vince directory with an invalid JSON file for testing
    error handling of corrupted offer data files.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory with corrupted offers.json.

    Requirements: 2.7
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "defaults.json").write_text('{"version": "1.1.0", "defaults": []}')
    # Write invalid JSON (missing closing bracket)
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": [')
    return data_dir


@pytest.fixture
def corrupted_offers_invalid_pattern(tmp_path: Path) -> Path:
    """Provide data directory with offers.json containing invalid offer_id pattern.

    Creates a .vince directory with an offers.json file that has an
    invalid offer_id pattern for testing schema validation.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 2.8
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "defaults.json").write_text('{"version": "1.1.0", "defaults": []}')
    offers_data = {
        "version": "1.0.0",
        "offers": [
            {
                "offer_id": "1invalid",  # Invalid: starts with number
                "default_id": "def-md-000",
                "state": "created",
                "auto_created": False,
                "created_at": "2024-01-01T00:00:00+00:00",
            }
        ],
    }
    (data_dir / "offers.json").write_text(json.dumps(offers_data))
    return data_dir


# =============================================================================
# Invalid Config Fixtures (Requirements: 4.1, 4.2, 4.3, 4.4)
# =============================================================================


@pytest.fixture
def invalid_config_unknown_option(tmp_path: Path) -> Path:
    """Provide data directory with config.json containing unknown option.

    Creates a .vince directory with a config.json file that has an
    unknown configuration option for testing config validation.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 4.1
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "defaults.json").write_text('{"version": "1.1.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    config_data = {
        "version": "1.0.0",
        "unknown_option": "some_value",  # Unknown option
    }
    (data_dir / "config.json").write_text(json.dumps(config_data))
    return data_dir


@pytest.fixture
def invalid_config_color_theme(tmp_path: Path) -> Path:
    """Provide data directory with config.json containing invalid color_theme.

    Creates a .vince directory with a config.json file that has an
    invalid color_theme value for testing config validation.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 4.2
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "defaults.json").write_text('{"version": "1.1.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    config_data = {
        "version": "1.0.0",
        "color_theme": "invalid_theme",  # Invalid theme value
    }
    (data_dir / "config.json").write_text(json.dumps(config_data))
    return data_dir


@pytest.fixture
def invalid_config_max_backups(tmp_path: Path) -> Path:
    """Provide data directory with config.json containing out-of-range max_backups.

    Creates a .vince directory with a config.json file that has an
    out-of-range max_backups value for testing config validation.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 4.3
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "defaults.json").write_text('{"version": "1.1.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    config_data = {
        "version": "1.0.0",
        "max_backups": 150,  # Out of range (0-100)
    }
    (data_dir / "config.json").write_text(json.dumps(config_data))
    return data_dir


@pytest.fixture
def invalid_config_malformed_json(tmp_path: Path) -> Path:
    """Provide data directory with malformed config.json.

    Creates a .vince directory with a config.json file that has
    invalid JSON syntax for testing config error handling.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 4.4
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "defaults.json").write_text('{"version": "1.1.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    # Write invalid JSON (missing closing brace)
    (data_dir / "config.json").write_text('{"version": "1.0.0", "verbose": true')
    return data_dir


# =============================================================================
# Active Default Fixtures for State Testing
# =============================================================================


@pytest.fixture
def data_dir_with_active_default(tmp_path: Path) -> Path:
    """Provide data directory with an active default for state testing.

    Creates a .vince directory with an active default entry for testing
    state transition errors like DefaultExistsError.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 3.1, 3.2
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    defaults_data = {
        "version": "1.1.0",
        "defaults": [
            {
                "id": "def-md-000",
                "extension": ".md",
                "application_path": "/usr/bin/vim",
                "application_name": "vim",
                "state": "active",
                "os_synced": True,
                "created_at": "2024-01-01T00:00:00+00:00",
            }
        ],
    }
    (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    return data_dir


@pytest.fixture
def data_dir_with_active_offer(tmp_path: Path) -> Path:
    """Provide data directory with an active offer for state testing.

    Creates a .vince directory with an active offer entry for testing
    state transition errors like OfferInUseError.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the created .vince data directory.

    Requirements: 3.5, 3.6
    """
    data_dir = tmp_path / ".vince"
    data_dir.mkdir(exist_ok=True)
    defaults_data = {
        "version": "1.1.0",
        "defaults": [
            {
                "id": "def-md-000",
                "extension": ".md",
                "application_path": "/usr/bin/vim",
                "application_name": "vim",
                "state": "active",
                "os_synced": True,
                "created_at": "2024-01-01T00:00:00+00:00",
            }
        ],
    }
    (data_dir / "defaults.json").write_text(json.dumps(defaults_data))
    offers_data = {
        "version": "1.0.0",
        "offers": [
            {
                "offer_id": "vim-md",
                "default_id": "def-md-000",
                "state": "active",
                "auto_created": True,
                "created_at": "2024-01-01T00:00:00+00:00",
            }
        ],
    }
    (data_dir / "offers.json").write_text(json.dumps(offers_data))
    return data_dir
