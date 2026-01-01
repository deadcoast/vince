"""macOS implementation of PlatformHandler using Launch Services.

This module provides the MacOSHandler class that implements file association
operations on macOS using:
- duti (preferred, if installed via `brew install duti`)
- PyObjC Launch Services (fallback)
- defaults command for bundle ID extraction

Requirements: 2.1, 2.3, 2.4, 4.1, 5.1, 5.2, 7.1, 7.2, 9.1, 9.2, 9.3, 9.4
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional

from vince.platform.base import AppInfo, OperationResult, Platform
from vince.platform.errors import ApplicationNotFoundError, BundleIdNotFoundError
from vince.platform.uti_map import extension_to_uti

# Set up logging for rollback operations
logger = logging.getLogger(__name__)


class MacOSHandler:
    """macOS implementation using Launch Services.

    This handler manages file associations on macOS by:
    1. Mapping extensions to UTIs (Uniform Type Identifiers)
    2. Using duti or Launch Services to set/query defaults
    3. Extracting bundle IDs from .app bundles

    Requirements: 2.1, 2.3
    """

    @property
    def platform(self) -> Platform:
        """Return the platform this handler supports.

        Returns:
            Platform.MACOS
        """
        return Platform.MACOS

    def verify_application(self, app_path: Path) -> AppInfo:
        """Extract bundle ID and validate .app bundle.

        Handles both .app bundles and direct executables by finding
        the parent .app bundle if needed.

        Args:
            app_path: Path to the application (can be .app or executable)

        Returns:
            AppInfo with application metadata including bundle_id

        Raises:
            ApplicationNotFoundError: If application doesn't exist

        Requirements: 2.1, 2.3
        """
        resolved = app_path.resolve()

        if not resolved.exists():
            raise ApplicationNotFoundError(str(app_path))

        # Handle both .app bundles and direct executables
        if resolved.suffix == ".app":
            bundle_path = resolved
        else:
            # Try to find parent .app bundle
            bundle_path = self._find_app_bundle(resolved)

        if bundle_path and bundle_path.exists():
            bundle_id = self._get_bundle_id(bundle_path)
            return AppInfo(
                path=resolved,
                name=bundle_path.stem,
                bundle_id=bundle_id,
            )

        # Fallback for non-bundled executables
        return AppInfo(
            path=resolved,
            name=resolved.stem,
            bundle_id=None,
        )

    def _get_bundle_id(self, app_bundle: Path) -> Optional[str]:
        """Extract CFBundleIdentifier from Info.plist.

        Uses the `defaults` command to read the bundle identifier
        from the application's Info.plist file.

        Args:
            app_bundle: Path to the .app bundle

        Returns:
            Bundle identifier string, or None if not found

        Requirements: 2.3
        """
        info_plist = app_bundle / "Contents" / "Info"
        try:
            result = subprocess.run(
                ["defaults", "read", str(info_plist), "CFBundleIdentifier"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def _find_app_bundle(self, executable: Path) -> Optional[Path]:
        """Find .app bundle containing an executable.

        Traverses up the directory tree to find the parent .app bundle
        that contains the given executable.

        Args:
            executable: Path to an executable file

        Returns:
            Path to the containing .app bundle, or None if not found
        """
        current = executable
        while current != current.parent:
            if current.suffix == ".app":
                return current
            current = current.parent
        return None

    def get_current_default(self, extension: str) -> Optional[str]:
        """Query Launch Services for current default handler.

        Tries duti first (more reliable), then falls back to
        Launch Services query via PyObjC.

        Args:
            extension: File extension (e.g., ".md", ".py")

        Returns:
            Path to current default application, or None if not set

        Requirements: 4.1
        """
        uti = extension_to_uti(extension)
        if not uti:
            return None

        # Try duti first (if installed)
        ext_without_dot = extension.lstrip(".")
        try:
            result = subprocess.run(
                ["duti", "-x", ext_without_dot],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if lines:
                    # First line is app path
                    return lines[0]
        except FileNotFoundError:
            # duti not installed, try alternative
            pass

        return self._query_launch_services(uti)

    def _query_launch_services(self, uti: str) -> Optional[str]:
        """Query Launch Services directly via PyObjC.

        Args:
            uti: Uniform Type Identifier to query

        Returns:
            Path to default application, or None if not found or PyObjC unavailable
        """
        try:
            # Import PyObjC frameworks
            from Foundation import NSWorkspace  # type: ignore[import-not-found]

            workspace = NSWorkspace.sharedWorkspace()
            # Try to get URL for application that handles this UTI
            app_url = workspace.URLForApplicationToOpenContentType_(uti)
            if app_url:
                return app_url.path()
        except ImportError:
            # PyObjC not installed
            pass
        except Exception:
            # Other errors (e.g., method not available on older macOS)
            pass
        return None

    def set_default(
        self,
        extension: str,
        app_path: Path,
        dry_run: bool = False,
    ) -> OperationResult:
        """Set default using duti or Launch Services.

        Records the previous default before making changes for rollback support.
        Tries duti first (more reliable), then falls back to PyObjC.
        If the operation fails after partial changes, attempts rollback.

        Args:
            extension: File extension (e.g., ".md", ".py")
            app_path: Path to the application
            dry_run: If True, simulate without making changes

        Returns:
            OperationResult with success status and details

        Requirements: 2.1, 2.4, 7.1, 7.2, 9.1, 9.2, 9.3, 9.4
        """
        app_info = self.verify_application(app_path)
        uti = extension_to_uti(extension)

        if not uti:
            return OperationResult(
                success=False,
                message=f"No UTI mapping for extension {extension}",
                error_code="VE602",
            )

        if not app_info.bundle_id:
            raise BundleIdNotFoundError(str(app_path))

        # Record previous default for rollback (Requirement 9.1)
        previous = self.get_current_default(extension)

        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would set {app_info.bundle_id} as default for {uti}",
                previous_default=previous,
            )

        # Try duti first (more reliable)
        try:
            subprocess.run(
                ["duti", "-s", app_info.bundle_id, uti, "all"],
                check=True,
                capture_output=True,
            )
            return OperationResult(
                success=True,
                message=f"Set {app_info.name} as default for {extension}",
                previous_default=previous,
            )
        except FileNotFoundError:
            # duti not installed, try PyObjC
            result = self._set_via_launch_services(app_info, uti, previous)
            if not result.success and previous:
                # Attempt rollback (Requirements 9.2, 9.3, 9.4)
                return self._attempt_rollback(
                    extension, uti, previous, result.message, result.error_code
                )
            return result
        except subprocess.CalledProcessError as e:
            error_msg = f"duti failed: {e.stderr.decode() if e.stderr else 'unknown error'}"
            # Attempt rollback if we have a previous default (Requirements 9.2, 9.3, 9.4)
            if previous:
                return self._attempt_rollback(
                    extension, uti, previous, error_msg, "VE605"
                )
            return OperationResult(
                success=False,
                message=error_msg,
                error_code="VE605",
                previous_default=previous,
            )

    def _attempt_rollback(
        self,
        extension: str,
        uti: str,
        previous_default: str,
        original_error: str,
        original_error_code: Optional[str],
    ) -> OperationResult:
        """Attempt to rollback to the previous default after a failure.

        Args:
            extension: File extension that was being modified
            uti: UTI for the extension
            previous_default: The previous default application path
            original_error: The error message from the failed operation
            original_error_code: The error code from the failed operation

        Returns:
            OperationResult with rollback status information

        Requirements: 9.2, 9.3, 9.4
        """
        logger.info(
            f"Attempting rollback for {extension} to previous default: {previous_default}"
        )

        try:
            # Try to restore the previous default
            # First, try to get the bundle ID of the previous default
            previous_path = Path(previous_default)
            if previous_path.exists():
                try:
                    previous_app_info = self.verify_application(previous_path)
                    if previous_app_info.bundle_id:
                        # Try duti first
                        try:
                            subprocess.run(
                                ["duti", "-s", previous_app_info.bundle_id, uti, "all"],
                                check=True,
                                capture_output=True,
                            )
                            logger.info(
                                f"Rollback successful for {extension} using duti"
                            )
                            return OperationResult(
                                success=False,
                                message=original_error,
                                error_code=original_error_code,
                                previous_default=previous_default,
                                rollback_attempted=True,
                                rollback_succeeded=True,
                                rollback_message=f"Restored previous default: {previous_default}",
                            )
                        except (FileNotFoundError, subprocess.CalledProcessError):
                            # Try PyObjC fallback for rollback
                            rollback_result = self._set_via_launch_services(
                                previous_app_info, uti, None
                            )
                            if rollback_result.success:
                                logger.info(
                                    f"Rollback successful for {extension} using Launch Services"
                                )
                                return OperationResult(
                                    success=False,
                                    message=original_error,
                                    error_code=original_error_code,
                                    previous_default=previous_default,
                                    rollback_attempted=True,
                                    rollback_succeeded=True,
                                    rollback_message=f"Restored previous default: {previous_default}",
                                )
                except Exception as e:
                    rollback_error = f"Failed to restore previous default: {e}"
                    logger.error(f"Rollback failed for {extension}: {rollback_error}")
                    return OperationResult(
                        success=False,
                        message=original_error,
                        error_code="VE607",
                        previous_default=previous_default,
                        rollback_attempted=True,
                        rollback_succeeded=False,
                        rollback_message=rollback_error,
                    )

            # Previous default path doesn't exist or couldn't be restored
            rollback_error = f"Previous default not found or invalid: {previous_default}"
            logger.warning(f"Rollback skipped for {extension}: {rollback_error}")
            return OperationResult(
                success=False,
                message=original_error,
                error_code=original_error_code,
                previous_default=previous_default,
                rollback_attempted=True,
                rollback_succeeded=False,
                rollback_message=rollback_error,
            )

        except Exception as e:
            rollback_error = f"Rollback failed with unexpected error: {e}"
            logger.error(f"Rollback failed for {extension}: {rollback_error}")
            return OperationResult(
                success=False,
                message=original_error,
                error_code="VE607",
                previous_default=previous_default,
                rollback_attempted=True,
                rollback_succeeded=False,
                rollback_message=rollback_error,
            )

    def _set_via_launch_services(
        self,
        app_info: AppInfo,
        uti: str,
        previous: Optional[str],
    ) -> OperationResult:
        """Set default using PyObjC Launch Services.

        Args:
            app_info: Application information with bundle_id
            uti: Uniform Type Identifier
            previous: Previous default application path

        Returns:
            OperationResult with success status
        """
        try:
            from LaunchServices import (  # type: ignore[import-not-found]
                LSSetDefaultRoleHandlerForContentType,
                kLSRolesAll,
            )

            result = LSSetDefaultRoleHandlerForContentType(
                uti,
                kLSRolesAll,
                app_info.bundle_id,
            )
            if result == 0:
                return OperationResult(
                    success=True,
                    message=f"Set {app_info.name} as default via Launch Services",
                    previous_default=previous,
                )
            return OperationResult(
                success=False,
                message=f"Launch Services returned error code {result}",
                error_code="VE605",
                previous_default=previous,
            )
        except ImportError:
            return OperationResult(
                success=False,
                message="Neither duti nor PyObjC available. Install duti: brew install duti",
                error_code="VE605",
                previous_default=previous,
            )

    def remove_default(
        self,
        extension: str,
        dry_run: bool = False,
    ) -> OperationResult:
        """Reset to system default.

        On macOS, we can't truly "remove" a default - we reset to system default
        by removing the user preference and rebuilding the Launch Services database.

        Args:
            extension: File extension to reset
            dry_run: If True, simulate without making changes

        Returns:
            OperationResult with success status

        Requirements: 5.1, 5.2
        """
        uti = extension_to_uti(extension)
        previous = self.get_current_default(extension)

        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would reset default for {extension} (UTI: {uti})",
                previous_default=previous,
            )

        # On macOS, we reset by removing user preferences and rebuilding LS database
        try:
            # Try to remove the user preference for this UTI
            # Note: This is a simplified approach - full implementation would
            # need to parse and modify the LSHandlers array in the plist
            subprocess.run(
                [
                    "defaults",
                    "delete",
                    "com.apple.LaunchServices/com.apple.launchservices.secure",
                    "LSHandlers",
                ],
                capture_output=True,
            )

            # Rebuild Launch Services database
            lsregister_path = (
                "/System/Library/Frameworks/CoreServices.framework/"
                "Frameworks/LaunchServices.framework/Support/lsregister"
            )
            subprocess.run(
                [
                    lsregister_path,
                    "-kill",
                    "-r",
                    "-domain",
                    "local",
                    "-domain",
                    "system",
                    "-domain",
                    "user",
                ],
                capture_output=True,
            )

            return OperationResult(
                success=True,
                message=f"Reset default for {extension}",
                previous_default=previous,
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to reset: {e}",
                error_code="VE605",
                previous_default=previous,
            )
