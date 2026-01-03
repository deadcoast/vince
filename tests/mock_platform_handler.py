"""
Mock Platform Handler for Vince CLI Testing

This module provides a MockPlatformHandler class that implements the PlatformHandler
protocol for testing OS integration without making actual OS changes.

Requirements: 20.1
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from vince.platform.base import AppInfo, OperationResult, Platform


@dataclass
class MockPlatformHandler:
    """Mock platform handler for testing OS integration.

    This class implements the PlatformHandler protocol and provides:
    - Tracking of all method calls for verification
    - Configurable failure modes for error testing
    - In-memory storage of defaults for state verification

    Attributes:
        platform: The platform this handler simulates (default: MACOS)
        _defaults: Internal storage of extension -> app_path mappings
        _calls: List of (method_name, kwargs) tuples for call verification
        _should_fail: If True, all operations return failure
        _fail_extensions: Set of extensions that should fail operations
        _fail_on_next: If True, the next operation will fail then reset

    Requirements: 20.1
    """

    platform: Platform = Platform.MACOS
    _defaults: dict[str, str] = field(default_factory=dict)
    _calls: list[tuple[str, dict]] = field(default_factory=list)
    _should_fail: bool = False
    _fail_extensions: set[str] = field(default_factory=set)
    _fail_on_next: bool = False
    _fail_error_code: str = "VE605"
    _fail_message: str = "Mock failure"

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

        Requirements: 20.2, 20.3
        """
        self._calls.append(
            (
                "set_default",
                {
                    "extension": extension,
                    "app_path": app_path,
                    "dry_run": dry_run,
                },
            )
        )

        # Check for configured failures
        if self._should_fail_operation(extension):
            return OperationResult(
                success=False,
                message=f"{self._fail_message} for {extension}",
                error_code=self._fail_error_code,
            )

        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would set {extension} to {app_path}",
            )

        # Store the default
        previous = self._defaults.get(extension)
        self._defaults[extension] = str(app_path)

        return OperationResult(
            success=True,
            message=f"Set {extension} to {app_path}",
            previous_default=previous,
        )

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

        Requirements: 20.4, 20.5
        """
        self._calls.append(
            (
                "remove_default",
                {
                    "extension": extension,
                    "dry_run": dry_run,
                },
            )
        )

        # Check for configured failures
        if self._should_fail_operation(extension):
            return OperationResult(
                success=False,
                message=f"{self._fail_message} for {extension}",
                error_code=self._fail_error_code,
            )

        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would remove default for {extension}",
            )

        # Remove the default
        previous = self._defaults.pop(extension, None)

        return OperationResult(
            success=True,
            message=f"Removed default for {extension}",
            previous_default=previous,
        )

    def get_current_default(self, extension: str) -> Optional[str]:
        """Query the current OS default application for an extension.

        Args:
            extension: File extension to query

        Returns:
            Path to current default application, or None if not set

        Requirements: 20.8
        """
        self._calls.append(
            (
                "get_current_default",
                {"extension": extension},
            )
        )
        return self._defaults.get(extension)

    def verify_application(self, app_path: Path) -> AppInfo:
        """Verify application exists and extract metadata.

        Args:
            app_path: Path to the application to verify

        Returns:
            AppInfo with application metadata

        Requirements: 20.1
        """
        self._calls.append(
            (
                "verify_application",
                {"app_path": app_path},
            )
        )

        # Generate mock app info
        app_name = app_path.stem
        bundle_id = None

        # If it looks like a macOS app bundle, generate a bundle ID
        if str(app_path).endswith(".app"):
            bundle_id = f"com.test.{app_name.lower()}"

        return AppInfo(
            path=app_path,
            name=app_name,
            bundle_id=bundle_id,
        )

    # =========================================================================
    # Configuration Methods for Test Setup
    # =========================================================================

    def configure_failure(
        self,
        should_fail: bool = True,
        error_code: str = "VE605",
        message: str = "Mock failure",
    ) -> None:
        """Configure the handler to fail all operations.

        Args:
            should_fail: If True, all operations will fail
            error_code: Error code to return on failure
            message: Error message to return on failure
        """
        self._should_fail = should_fail
        self._fail_error_code = error_code
        self._fail_message = message

    def configure_extension_failure(
        self,
        extension: str,
        error_code: str = "VE605",
        message: str = "Mock failure",
    ) -> None:
        """Configure the handler to fail operations for a specific extension.

        Args:
            extension: Extension that should fail
            error_code: Error code to return on failure
            message: Error message to return on failure
        """
        self._fail_extensions.add(extension)
        self._fail_error_code = error_code
        self._fail_message = message

    def configure_next_failure(
        self,
        error_code: str = "VE605",
        message: str = "Mock failure",
    ) -> None:
        """Configure the handler to fail the next operation only.

        Args:
            error_code: Error code to return on failure
            message: Error message to return on failure
        """
        self._fail_on_next = True
        self._fail_error_code = error_code
        self._fail_message = message

    def set_existing_default(self, extension: str, app_path: str) -> None:
        """Pre-populate a default for testing.

        Args:
            extension: File extension
            app_path: Application path to set as default
        """
        self._defaults[extension] = app_path

    def reset(self) -> None:
        """Reset the handler to initial state."""
        self._defaults.clear()
        self._calls.clear()
        self._should_fail = False
        self._fail_extensions.clear()
        self._fail_on_next = False
        self._fail_error_code = "VE605"
        self._fail_message = "Mock failure"

    # =========================================================================
    # Verification Methods for Test Assertions
    # =========================================================================

    def get_calls(self, method_name: Optional[str] = None) -> list[tuple[str, dict]]:
        """Get recorded method calls, optionally filtered by method name.

        Args:
            method_name: If provided, only return calls to this method

        Returns:
            List of (method_name, kwargs) tuples
        """
        if method_name is None:
            return list(self._calls)
        return [(name, kwargs) for name, kwargs in self._calls if name == method_name]

    def was_called(self, method_name: str) -> bool:
        """Check if a method was called.

        Args:
            method_name: Name of the method to check

        Returns:
            True if the method was called at least once
        """
        return any(name == method_name for name, _ in self._calls)

    def call_count(self, method_name: str) -> int:
        """Get the number of times a method was called.

        Args:
            method_name: Name of the method to count

        Returns:
            Number of times the method was called
        """
        return sum(1 for name, _ in self._calls if name == method_name)

    def get_stored_defaults(self) -> dict[str, str]:
        """Get all stored defaults.

        Returns:
            Dictionary of extension -> app_path mappings
        """
        return dict(self._defaults)

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _should_fail_operation(self, extension: str) -> bool:
        """Check if an operation should fail based on configuration.

        Args:
            extension: The extension being operated on

        Returns:
            True if the operation should fail
        """
        # Check one-time failure
        if self._fail_on_next:
            self._fail_on_next = False
            return True

        # Check global failure
        if self._should_fail:
            return True

        # Check extension-specific failure
        if extension in self._fail_extensions:
            return True

        return False


def create_mock_handler(
    platform: Platform = Platform.MACOS,
    existing_defaults: Optional[dict[str, str]] = None,
) -> MockPlatformHandler:
    """Factory function to create a configured MockPlatformHandler.

    Args:
        platform: Platform to simulate
        existing_defaults: Pre-existing defaults to populate

    Returns:
        Configured MockPlatformHandler instance
    """
    handler = MockPlatformHandler(platform=platform)

    if existing_defaults:
        for ext, path in existing_defaults.items():
            handler.set_existing_default(ext, path)

    return handler
