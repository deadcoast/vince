"""Platform-specific error classes for OS integration.

This module defines error classes for OS-level file association operations.
Error codes are in the VE6xx series:
- VE601: Unsupported platform
- VE602: Cannot determine application bundle ID (macOS)
- VE603: Registry access denied (Windows)
- VE604: Application not found or invalid
- VE605: OS operation failed (generic)
- VE606: Sync partially failed

Requirements: 8.1, 8.2, 8.3
"""

from typing import List

from vince.errors import VinceError


class UnsupportedPlatformError(VinceError):
    """VE601: Platform not supported.

    Raised when vince is run on an unsupported operating system.
    Currently only macOS and Windows are supported.
    """

    def __init__(self, platform: str):
        super().__init__(
            code="VE601",
            message=f"Unsupported platform: {platform}",
            recovery="vince supports macOS and Windows only",
        )


class BundleIdNotFoundError(VinceError):
    """VE602: Cannot determine macOS bundle ID.

    Raised when the bundle identifier cannot be extracted from
    a macOS application bundle's Info.plist.
    """

    def __init__(self, app_path: str):
        super().__init__(
            code="VE602",
            message=f"Cannot determine bundle ID for: {app_path}",
            recovery="Ensure the path points to a valid .app bundle",
        )


class RegistryAccessError(VinceError):
    """VE603: Windows registry access denied.

    Raised when vince cannot read or write to the Windows registry
    due to insufficient permissions.
    """

    def __init__(self, operation: str):
        super().__init__(
            code="VE603",
            message=f"Registry access denied: {operation}",
            recovery="Run vince as administrator or check permissions",
        )


class ApplicationNotFoundError(VinceError):
    """VE604: Application not found or invalid.

    Raised when the specified application path does not exist
    or is not a valid executable.
    """

    def __init__(self, app_path: str):
        super().__init__(
            code="VE604",
            message=f"Application not found or invalid: {app_path}",
            recovery="Verify the application path exists and is executable",
        )


class OSOperationError(VinceError):
    """VE605: Generic OS operation failure.

    Raised when an OS-level operation fails for reasons not covered
    by more specific error codes.
    """

    def __init__(self, operation: str, details: str):
        super().__init__(
            code="VE605",
            message=f"OS operation failed: {operation} - {details}",
            recovery="Check system logs for details",
        )


class SyncPartialError(VinceError):
    """VE606: Sync completed with some failures.

    Raised when a sync operation completes but some extensions
    failed to sync properly.
    """

    def __init__(self, succeeded: int, failed: int, failures: List[str]):
        super().__init__(
            code="VE606",
            message=f"Sync partially failed: {succeeded} succeeded, {failed} failed",
            recovery=f"Failed extensions: {', '.join(failures)}",
        )


class RollbackError(VinceError):
    """VE607: Rollback operation failed.

    Raised when an OS operation fails and the subsequent rollback
    attempt also fails, leaving the system in an inconsistent state.
    """

    def __init__(
        self,
        original_error: str,
        rollback_error: str,
        extension: str,
    ):
        super().__init__(
            code="VE607",
            message=(
                f"Operation failed and rollback also failed for {extension}. "
                f"Original error: {original_error}. Rollback error: {rollback_error}"
            ),
            recovery=(
                "System may be in inconsistent state. "
                "Manually verify file associations and try again."
            ),
        )
        self.original_error = original_error
        self.rollback_error = rollback_error
        self.extension = extension
