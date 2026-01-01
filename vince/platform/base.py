"""Platform handler base types and protocol.

This module defines the core abstractions for platform-specific file association
handlers. It provides:
- Platform enum for OS detection
- AppInfo dataclass for application metadata
- OperationResult dataclass for operation outcomes
- PlatformHandler Protocol defining the handler interface

Requirements: 1.1
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable


class Platform(Enum):
    """Supported platforms for file association operations.

    Values:
        MACOS: macOS (darwin) platform
        WINDOWS: Windows (win32) platform
        UNSUPPORTED: Any other platform
    """

    MACOS = "darwin"
    WINDOWS = "win32"
    UNSUPPORTED = "unsupported"


@dataclass
class AppInfo:
    """Information about a validated application.

    Attributes:
        path: Resolved path to the application
        name: Display name of the application
        bundle_id: macOS bundle identifier (None on Windows)
        executable: Windows executable path (None on macOS)
    """

    path: Path
    name: str
    bundle_id: Optional[str] = None  # macOS only
    executable: Optional[str] = None  # Windows: actual .exe path


@dataclass
class OperationResult:
    """Result of a platform operation.

    Attributes:
        success: Whether the operation succeeded
        message: Human-readable result message
        previous_default: The default before this operation (for rollback)
        error_code: Error code if operation failed (VE6xx series)
        rollback_attempted: Whether a rollback was attempted after failure
        rollback_succeeded: Whether the rollback succeeded (None if not attempted)
        rollback_message: Details about the rollback attempt
    """

    success: bool
    message: str
    previous_default: Optional[str] = None
    error_code: Optional[str] = None
    rollback_attempted: bool = False
    rollback_succeeded: Optional[bool] = None
    rollback_message: Optional[str] = None


@runtime_checkable
class PlatformHandler(Protocol):
    """Protocol for platform-specific file association handlers.

    Implementations must provide methods for:
    - Setting default applications for extensions
    - Removing/resetting default applications
    - Querying current default applications
    - Verifying application validity
    """

    @property
    def platform(self) -> Platform:
        """Return the platform this handler supports."""
        ...

    def set_default(
        self,
        extension: str,
        app_path: Path,
        dry_run: bool = False,
    ) -> OperationResult:
        """Set the OS default application for an extension.

        Args:
            extension: File extension (e.g., ".md", ".py")
            app_path: Path to the application
            dry_run: If True, simulate without making changes

        Returns:
            OperationResult with success status and details
        """
        ...

    def remove_default(
        self,
        extension: str,
        dry_run: bool = False,
    ) -> OperationResult:
        """Remove/reset the OS default for an extension.

        Args:
            extension: File extension to reset
            dry_run: If True, simulate without making changes

        Returns:
            OperationResult with success status and details
        """
        ...

    def get_current_default(self, extension: str) -> Optional[str]:
        """Query the current OS default application for an extension.

        Args:
            extension: File extension to query

        Returns:
            Path to current default application, or None if not set
        """
        ...

    def verify_application(self, app_path: Path) -> AppInfo:
        """Verify application exists and extract metadata.

        Args:
            app_path: Path to the application to verify

        Returns:
            AppInfo with application metadata

        Raises:
            ApplicationNotFoundError: If application is invalid
        """
        ...
