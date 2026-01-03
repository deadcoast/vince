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
    def mock_get_data_dir(config=None) -> Path:
        return data_dir

    return mock_get_data_dir
