"""Windows implementation of PlatformHandler using Registry.

This module provides the WindowsHandler class that implements file association
operations on Windows using:
- Windows Registry (winreg) for storing file associations
- ProgID entries for application registration
- SHChangeNotify for shell notification

Requirements: 3.1, 3.2, 3.3, 3.5, 4.1, 5.1, 5.3, 7.1, 7.2, 9.1
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vince.platform.base import AppInfo, OperationResult, Platform
from vince.platform.errors import ApplicationNotFoundError

# Type hints for Windows-specific modules
if TYPE_CHECKING:
    pass  # winreg and ctypes types are built-in


def _get_winreg() -> Any:
    """Get the winreg module, raising ImportError on non-Windows."""
    if sys.platform != "win32":
        raise ImportError("winreg is only available on Windows")
    import winreg
    return winreg


def _get_ctypes() -> Any:
    """Get the ctypes module with Windows-specific functionality."""
    if sys.platform != "win32":
        raise ImportError("Windows ctypes functionality not available")
    import ctypes
    return ctypes


class WindowsHandler:
    """Windows implementation using Registry.

    This handler manages file associations on Windows by:
    1. Creating ProgID entries in HKEY_CURRENT_USER\\Software\\Classes
    2. Associating extensions with ProgIDs
    3. Notifying the shell of changes via SHChangeNotify

    Requirements: 3.1
    """

    @property
    def platform(self) -> Platform:
        """Return the platform this handler supports.

        Returns:
            Platform.WINDOWS
        """
        return Platform.WINDOWS

    def verify_application(self, app_path: Path) -> AppInfo:
        """Verify Windows executable and extract metadata.

        Handles both .exe files directly and directories containing executables.
        For directories, searches for the first .exe file.

        Args:
            app_path: Path to the application (can be .exe or directory)

        Returns:
            AppInfo with application metadata including executable path

        Raises:
            ApplicationNotFoundError: If application doesn't exist

        Requirements: 3.1
        """
        resolved = app_path.resolve()

        if not resolved.exists():
            raise ApplicationNotFoundError(str(app_path))

        # Handle .exe directly or find executable in folder
        if resolved.suffix.lower() == ".exe":
            exe_path = resolved
        else:
            # Look for .exe in directory
            exe_path = self._find_executable(resolved)

        return AppInfo(
            path=resolved,
            name=resolved.stem,
            executable=str(exe_path) if exe_path else None,
        )

    def _find_executable(self, path: Path) -> Optional[Path]:
        """Find main executable in a directory.

        If the path is a file, returns it directly.
        If the path is a directory, searches for the first .exe file.

        Args:
            path: Path to file or directory

        Returns:
            Path to executable, or None if not found
        """
        if path.is_file():
            return path
        if path.is_dir():
            for exe in path.glob("*.exe"):
                return exe
        return None

    def get_current_default(self, extension: str) -> Optional[str]:
        """Query Windows Registry for current default application.

        Checks the UserChoice registry key first (modern Windows),
        then falls back to HKEY_CLASSES_ROOT for older associations.

        Args:
            extension: File extension (e.g., ".md", ".py")

        Returns:
            Path to current default application, or None if not set

        Requirements: 4.1
        """
        try:
            winreg = _get_winreg()
        except ImportError:
            return None

        ext = extension if extension.startswith(".") else f".{extension}"

        # Check user choice first (modern Windows)
        try:
            key_path = (
                f"Software\\Microsoft\\Windows\\CurrentVersion\\"
                f"Explorer\\FileExts\\{ext}\\UserChoice"
            )
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")
                return self._resolve_prog_id(prog_id)
        except OSError:
            pass

        # Fall back to class registration (HKEY_CLASSES_ROOT)
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                prog_id, _ = winreg.QueryValueEx(key, "")
                return self._resolve_prog_id(prog_id)
        except OSError:
            return None

    def _resolve_prog_id(self, prog_id: str) -> Optional[str]:
        """Resolve ProgID to application path.

        Looks up the shell\\open\\command key for the ProgID to find
        the actual executable path.

        Args:
            prog_id: Programmatic Identifier to resolve

        Returns:
            Path to application executable, or None if not found
        """
        try:
            winreg = _get_winreg()
        except ImportError:
            return None

        try:
            key_path = f"{prog_id}\\shell\\open\\command"
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
                command, _ = winreg.QueryValueEx(key, "")
                # Extract path from command (handle quotes)
                if command.startswith('"'):
                    return command.split('"')[1]
                return command.split()[0]
        except OSError:
            # Try HKEY_CURRENT_USER as fallback
            try:
                key_path = f"Software\\Classes\\{prog_id}\\shell\\open\\command"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    command, _ = winreg.QueryValueEx(key, "")
                    if command.startswith('"'):
                        return command.split('"')[1]
                    return command.split()[0]
            except OSError:
                return None

    def set_default(
        self,
        extension: str,
        app_path: Path,
        dry_run: bool = False,
    ) -> OperationResult:
        """Set default application via Windows Registry.

        Creates a ProgID entry for the application and associates
        the extension with it. Records the previous default for rollback.

        Args:
            extension: File extension (e.g., ".md", ".py")
            app_path: Path to the application
            dry_run: If True, simulate without making changes

        Returns:
            OperationResult with success status and details

        Requirements: 3.1, 3.2, 3.3, 3.5, 7.1, 7.2, 9.1
        """
        app_info = self.verify_application(app_path)
        ext = extension if extension.startswith(".") else f".{extension}"

        if not app_info.executable:
            return OperationResult(
                success=False,
                message=f"Cannot find executable for {app_path}",
                error_code="VE604",
            )

        # Record previous default for rollback (Requirement 9.1)
        previous = self.get_current_default(extension)
        prog_id = f"vince.{ext[1:]}"

        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would register {prog_id} -> {app_info.executable}",
                previous_default=previous,
            )

        try:
            # Create ProgID entry
            self._create_prog_id(prog_id, app_info)

            # Associate extension with ProgID
            self._associate_extension(ext, prog_id)

            # Notify shell of change (Requirement 3.5)
            self._notify_shell()

            return OperationResult(
                success=True,
                message=f"Set {app_info.name} as default for {extension}",
                previous_default=previous,
            )
        except PermissionError:
            return OperationResult(
                success=False,
                message="Registry access denied. Run as administrator.",
                error_code="VE603",
                previous_default=previous,
            )
        except ImportError as e:
            return OperationResult(
                success=False,
                message=f"Windows registry not available: {e}",
                error_code="VE605",
                previous_default=previous,
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Registry operation failed: {e}",
                error_code="VE605",
                previous_default=previous,
            )

    def _create_prog_id(self, prog_id: str, app_info: AppInfo) -> None:
        """Create ProgID entry in registry.

        Creates the following registry structure:
        HKEY_CURRENT_USER\\Software\\Classes\\{prog_id}
            (Default) = "{app_name} File"
            shell\\open\\command
                (Default) = "\"{executable}\" \"%1\""

        Args:
            prog_id: Programmatic Identifier to create
            app_info: Application information with executable path

        Requirements: 3.2
        """
        winreg = _get_winreg()

        # HKEY_CURRENT_USER\Software\Classes\{prog_id}
        key_path = f"Software\\Classes\\{prog_id}"

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{app_info.name} File")

        # shell\open\command
        cmd_path = f"{key_path}\\shell\\open\\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_path) as key:
            command = f'"{app_info.executable}" "%1"'
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)

    def _associate_extension(self, ext: str, prog_id: str) -> None:
        """Associate extension with ProgID.

        Creates the following registry structure:
        HKEY_CURRENT_USER\\Software\\Classes\\{ext}
            (Default) = "{prog_id}"

        Also attempts to clear the UserChoice key for modern Windows.

        Args:
            ext: File extension (with leading dot)
            prog_id: Programmatic Identifier to associate

        Requirements: 3.3
        """
        winreg = _get_winreg()

        # HKEY_CURRENT_USER\Software\Classes\{ext}
        key_path = f"Software\\Classes\\{ext}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, prog_id)

        # Try to clear UserChoice for modern Windows
        # Note: UserChoice is protected by a hash on modern Windows,
        # so this may not work, but we try anyway
        fe_path = (
            f"Software\\Microsoft\\Windows\\CurrentVersion\\"
            f"Explorer\\FileExts\\{ext}\\UserChoice"
        )
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fe_path)
        except OSError:
            # UserChoice may not exist or may be protected
            pass

    def _notify_shell(self) -> None:
        """Notify Windows shell of file association change.

        Calls SHChangeNotify with SHCNE_ASSOCCHANGED to inform
        the shell that file associations have changed.

        Requirements: 3.5
        """
        ctypes = _get_ctypes()
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(
            SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None
        )

    def remove_default(
        self,
        extension: str,
        dry_run: bool = False,
    ) -> OperationResult:
        """Remove custom file association.

        Deletes the vince-created ProgID and extension association,
        allowing Windows to fall back to system defaults.

        Args:
            extension: File extension to reset
            dry_run: If True, simulate without making changes

        Returns:
            OperationResult with success status

        Requirements: 5.1, 5.3
        """
        ext = extension if extension.startswith(".") else f".{extension}"
        prog_id = f"vince.{ext[1:]}"
        previous = self.get_current_default(extension)

        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would remove {prog_id} association",
                previous_default=previous,
            )

        try:
            winreg = _get_winreg()

            # Remove ProgID
            self._delete_key_recursive(
                winreg.HKEY_CURRENT_USER,
                f"Software\\Classes\\{prog_id}",
            )

            # Remove extension association
            self._delete_key_recursive(
                winreg.HKEY_CURRENT_USER,
                f"Software\\Classes\\{ext}",
            )

            # Notify shell
            self._notify_shell()

            return OperationResult(
                success=True,
                message=f"Removed custom default for {extension}",
                previous_default=previous,
            )
        except ImportError as e:
            return OperationResult(
                success=False,
                message=f"Windows registry not available: {e}",
                error_code="VE605",
                previous_default=previous,
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to remove: {e}",
                error_code="VE605",
                previous_default=previous,
            )

    def _delete_key_recursive(self, hkey: int, key_path: str) -> None:
        """Recursively delete a registry key and all its subkeys.

        Windows registry keys cannot be deleted if they have subkeys,
        so this method deletes all subkeys first.

        Args:
            hkey: Registry hive (e.g., HKEY_CURRENT_USER)
            key_path: Path to the key to delete
        """
        winreg = _get_winreg()

        try:
            with winreg.OpenKey(
                hkey, key_path, 0, winreg.KEY_ALL_ACCESS
            ) as key:
                # Delete all subkeys first
                while True:
                    try:
                        subkey = winreg.EnumKey(key, 0)
                        self._delete_key_recursive(hkey, f"{key_path}\\{subkey}")
                    except OSError:
                        # No more subkeys
                        break
            # Now delete the key itself
            winreg.DeleteKey(hkey, key_path)
        except OSError:
            # Key doesn't exist or access denied
            pass
