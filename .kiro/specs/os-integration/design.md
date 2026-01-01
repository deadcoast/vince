# Design Document: OS Integration Layer

## Overview

This design document describes the architecture for adding cross-platform OS integration to vince. The core addition is an abstraction layer (`vince/platform/`) that provides a unified interface for setting file associations on macOS and Windows, while the existing command structure remains intact.

The design follows the Strategy pattern - a common interface with platform-specific implementations that are selected at runtime based on the detected OS.

## Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        vince CLI Commands                       │
│  (slap, chop, set, forget, offer, reject, list, sync)           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OS Integration Layer                         │
│                  vince/platform/__init__.py                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              PlatformHandler (Protocol)                 │    │
│  │  - set_default(ext, app_path) -> Result                 │    │
│  │  - remove_default(ext) -> Result                        │    │
│  │  - get_current_default(ext) -> Optional[str]            │    │
│  │  - verify_application(app_path) -> AppInfo              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                      │
│            ┌─────────────┴─────────────┐                        │
│            ▼                           ▼                        │
│  ┌──────────────────┐       ┌──────────────────┐                │
│  │  MacOSHandler    │       │  WindowsHandler  │                │
│  │  (darwin)        │       │  (win32)         │                │
│  └──────────────────┘       └──────────────────┘                │
│            │                           │                        │
│            ▼                           ▼                        │
│  ┌──────────────────┐       ┌──────────────────┐                │
│  │ Launch Services  │       │ Windows Registry │                │
│  │ UTI Mapping      │       │ ProgID / FileExts│                │
│  │ (PyObjC/duti)    │       │ (winreg)         │                │
│  └──────────────────┘       └──────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

### Module Structure

```
vince/
├── platform/
│   ├── __init__.py          # Factory + get_handler()
│   ├── base.py              # Protocol definition + Result types
│   ├── macos.py             # macOS implementation
│   ├── windows.py           # Windows implementation
│   ├── uti_map.py           # Extension to UTI mapping table
│   └── errors.py            # Platform-specific error classes
├── commands/
│   ├── slap.py              # Updated to call platform handler
│   ├── chop.py              # Updated to call platform handler
│   ├── set_cmd.py           # Updated to call platform handler
│   ├── forget.py            # Updated to call platform handler
│   └── sync.py              # NEW: Bulk sync command
└── ...
```

## Components and Interfaces

### PlatformHandler Protocol

```python
# vince/platform/base.py
from typing import Protocol, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class Platform(Enum):
    MACOS = "darwin"
    WINDOWS = "win32"
    UNSUPPORTED = "unsupported"

@dataclass
class AppInfo:
    """Information about a validated application."""
    path: Path
    name: str
    bundle_id: Optional[str] = None  # macOS only
    executable: Optional[str] = None  # Windows: actual .exe path

@dataclass
class OperationResult:
    """Result of a platform operation."""
    success: bool
    message: str
    previous_default: Optional[str] = None
    error_code: Optional[str] = None

class PlatformHandler(Protocol):
    """Protocol for platform-specific file association handlers."""
    
    def set_default(
        self, 
        extension: str, 
        app_path: Path,
        dry_run: bool = False
    ) -> OperationResult:
        """Set the OS default application for an extension."""
        ...
    
    def remove_default(
        self, 
        extension: str,
        dry_run: bool = False
    ) -> OperationResult:
        """Remove/reset the OS default for an extension."""
        ...
    
    def get_current_default(self, extension: str) -> Optional[str]:
        """Query the current OS default application for an extension."""
        ...
    
    def verify_application(self, app_path: Path) -> AppInfo:
        """Verify application exists and extract metadata."""
        ...
    
    @property
    def platform(self) -> Platform:
        """Return the platform this handler supports."""
        ...
```

### Factory Function

```python
# vince/platform/__init__.py
import sys
from typing import Optional
from vince.platform.base import PlatformHandler, Platform
from vince.errors import UnsupportedPlatformError

_handler: Optional[PlatformHandler] = None

def get_platform() -> Platform:
    """Detect and return the current platform."""
    if sys.platform == "darwin":
        return Platform.MACOS
    elif sys.platform == "win32":
        return Platform.WINDOWS
    return Platform.UNSUPPORTED

def get_handler() -> PlatformHandler:
    """Get the platform-specific handler (singleton)."""
    global _handler
    if _handler is not None:
        return _handler
    
    platform = get_platform()
    
    if platform == Platform.MACOS:
        from vince.platform.macos import MacOSHandler
        _handler = MacOSHandler()
    elif platform == Platform.WINDOWS:
        from vince.platform.windows import WindowsHandler
        _handler = WindowsHandler()
    else:
        raise UnsupportedPlatformError(sys.platform)
    
    return _handler
```

### macOS Handler

```python
# vince/platform/macos.py
import subprocess
from pathlib import Path
from typing import Optional

from vince.platform.base import (
    PlatformHandler, Platform, AppInfo, OperationResult
)
from vince.platform.uti_map import extension_to_uti
from vince.platform.errors import (
    BundleIdNotFoundError, LaunchServicesError
)

class MacOSHandler:
    """macOS implementation using Launch Services."""
    
    @property
    def platform(self) -> Platform:
        return Platform.MACOS
    
    def verify_application(self, app_path: Path) -> AppInfo:
        """Extract bundle ID from .app bundle."""
        resolved = app_path.resolve()
        
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
                bundle_id=bundle_id
            )
        
        # Fallback for non-bundled executables
        return AppInfo(
            path=resolved,
            name=resolved.stem,
            bundle_id=None
        )
    
    def _get_bundle_id(self, app_bundle: Path) -> Optional[str]:
        """Extract CFBundleIdentifier from Info.plist."""
        try:
            result = subprocess.run(
                ["defaults", "read", str(app_bundle / "Contents/Info"), 
                 "CFBundleIdentifier"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def _find_app_bundle(self, executable: Path) -> Optional[Path]:
        """Find .app bundle containing an executable."""
        current = executable
        while current != current.parent:
            if current.suffix == ".app":
                return current
            current = current.parent
        return None
    
    def get_current_default(self, extension: str) -> Optional[str]:
        """Query Launch Services for current default handler."""
        uti = extension_to_uti(extension)
        if not uti:
            return None
        
        try:
            # Use duti if available, otherwise fall back to defaults
            result = subprocess.run(
                ["duti", "-x", extension.lstrip(".")],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if lines:
                    return lines[0]  # First line is app path
        except FileNotFoundError:
            # duti not installed, try alternative
            pass
        
        return self._query_launch_services(uti)
    
    def _query_launch_services(self, uti: str) -> Optional[str]:
        """Query Launch Services directly via Python."""
        try:
            from Foundation import NSWorkspace
            workspace = NSWorkspace.sharedWorkspace()
            app_url = workspace.URLForApplicationToOpenContentType_(uti)
            if app_url:
                return app_url.path()
        except ImportError:
            pass
        return None
    
    def set_default(
        self, 
        extension: str, 
        app_path: Path,
        dry_run: bool = False
    ) -> OperationResult:
        """Set default using duti or Launch Services."""
        app_info = self.verify_application(app_path)
        uti = extension_to_uti(extension)
        
        if not uti:
            return OperationResult(
                success=False,
                message=f"No UTI mapping for extension {extension}",
                error_code="VE602"
            )
        
        if not app_info.bundle_id:
            return OperationResult(
                success=False,
                message=f"Cannot determine bundle ID for {app_path}",
                error_code="VE602"
            )
        
        previous = self.get_current_default(extension)
        
        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would set {app_info.bundle_id} as default for {uti}",
                previous_default=previous
            )
        
        # Try duti first (more reliable)
        try:
            subprocess.run(
                ["duti", "-s", app_info.bundle_id, uti, "all"],
                check=True,
                capture_output=True
            )
            return OperationResult(
                success=True,
                message=f"Set {app_info.name} as default for {extension}",
                previous_default=previous
            )
        except FileNotFoundError:
            # duti not installed, try PyObjC
            return self._set_via_launch_services(app_info, uti, previous)
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message=f"duti failed: {e.stderr}",
                error_code="VE605"
            )
    
    def _set_via_launch_services(
        self, 
        app_info: AppInfo, 
        uti: str,
        previous: Optional[str]
    ) -> OperationResult:
        """Set default using PyObjC Launch Services."""
        try:
            from LaunchServices import (
                LSSetDefaultRoleHandlerForContentType,
                kLSRolesAll
            )
            result = LSSetDefaultRoleHandlerForContentType(
                uti, 
                kLSRolesAll, 
                app_info.bundle_id
            )
            if result == 0:
                return OperationResult(
                    success=True,
                    message=f"Set {app_info.name} as default via Launch Services",
                    previous_default=previous
                )
            return OperationResult(
                success=False,
                message=f"Launch Services returned error code {result}",
                error_code="VE605"
            )
        except ImportError:
            return OperationResult(
                success=False,
                message="Neither duti nor PyObjC available. Install duti: brew install duti",
                error_code="VE605"
            )
    
    def remove_default(
        self, 
        extension: str,
        dry_run: bool = False
    ) -> OperationResult:
        """Reset to system default (macOS doesn't have true 'remove')."""
        uti = extension_to_uti(extension)
        previous = self.get_current_default(extension)
        
        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would reset default for {extension} (UTI: {uti})",
                previous_default=previous
            )
        
        # On macOS, we can't truly "remove" - we reset to system default
        # This is done by removing the user preference
        try:
            subprocess.run(
                ["defaults", "delete", "com.apple.LaunchServices/com.apple.launchservices.secure",
                 f"LSHandlers"],
                capture_output=True
            )
            # Rebuild Launch Services database
            subprocess.run(
                ["/System/Library/Frameworks/CoreServices.framework/Frameworks/"
                 "LaunchServices.framework/Support/lsregister", 
                 "-kill", "-r", "-domain", "local", "-domain", "system", "-domain", "user"],
                capture_output=True
            )
            return OperationResult(
                success=True,
                message=f"Reset default for {extension}",
                previous_default=previous
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to reset: {e}",
                error_code="VE605"
            )
```

### Windows Handler

```python
# vince/platform/windows.py
import winreg
import ctypes
from pathlib import Path
from typing import Optional

from vince.platform.base import (
    PlatformHandler, Platform, AppInfo, OperationResult
)
from vince.platform.errors import RegistryAccessError

class WindowsHandler:
    """Windows implementation using Registry."""
    
    @property
    def platform(self) -> Platform:
        return Platform.WINDOWS
    
    def verify_application(self, app_path: Path) -> AppInfo:
        """Verify Windows executable."""
        resolved = app_path.resolve()
        
        # Handle .exe directly or find executable in folder
        if resolved.suffix.lower() == ".exe":
            exe_path = resolved
        else:
            # Look for .exe in directory
            exe_path = self._find_executable(resolved)
        
        return AppInfo(
            path=resolved,
            name=resolved.stem,
            executable=str(exe_path) if exe_path else None
        )
    
    def _find_executable(self, path: Path) -> Optional[Path]:
        """Find main executable in a directory."""
        if path.is_file():
            return path
        if path.is_dir():
            for exe in path.glob("*.exe"):
                return exe
        return None
    
    def get_current_default(self, extension: str) -> Optional[str]:
        """Query Windows Registry for current default."""
        ext = extension if extension.startswith(".") else f".{extension}"
        
        try:
            # Check user choice first
            key_path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\{ext}\\UserChoice"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")
                return self._resolve_prog_id(prog_id)
        except WindowsError:
            pass
        
        try:
            # Fall back to class registration
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                prog_id, _ = winreg.QueryValueEx(key, "")
                return self._resolve_prog_id(prog_id)
        except WindowsError:
            return None
    
    def _resolve_prog_id(self, prog_id: str) -> Optional[str]:
        """Resolve ProgID to application path."""
        try:
            key_path = f"{prog_id}\\shell\\open\\command"
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
                command, _ = winreg.QueryValueEx(key, "")
                # Extract path from command (handle quotes)
                if command.startswith('"'):
                    return command.split('"')[1]
                return command.split()[0]
        except WindowsError:
            return None
    
    def set_default(
        self, 
        extension: str, 
        app_path: Path,
        dry_run: bool = False
    ) -> OperationResult:
        """Set default via Windows Registry."""
        app_info = self.verify_application(app_path)
        ext = extension if extension.startswith(".") else f".{extension}"
        
        if not app_info.executable:
            return OperationResult(
                success=False,
                message=f"Cannot find executable for {app_path}",
                error_code="VE604"
            )
        
        previous = self.get_current_default(extension)
        prog_id = f"vince.{ext[1:]}"
        
        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would register {prog_id} -> {app_info.executable}",
                previous_default=previous
            )
        
        try:
            # Create ProgID
            self._create_prog_id(prog_id, app_info)
            
            # Associate extension with ProgID
            self._associate_extension(ext, prog_id)
            
            # Notify shell of change
            self._notify_shell()
            
            return OperationResult(
                success=True,
                message=f"Set {app_info.name} as default for {extension}",
                previous_default=previous
            )
        except PermissionError:
            return OperationResult(
                success=False,
                message="Registry access denied. Run as administrator.",
                error_code="VE603"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Registry operation failed: {e}",
                error_code="VE605"
            )
    
    def _create_prog_id(self, prog_id: str, app_info: AppInfo) -> None:
        """Create ProgID entry in registry."""
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
        """Associate extension with ProgID."""
        # HKEY_CURRENT_USER\Software\Classes\{ext}
        key_path = f"Software\\Classes\\{ext}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, prog_id)
        
        # Also set in FileExts for modern Windows
        fe_path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\{ext}\\UserChoice"
        try:
            # UserChoice requires special handling - delete and recreate
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fe_path)
        except WindowsError:
            pass
    
    def _notify_shell(self) -> None:
        """Notify Windows shell of file association change."""
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(
            SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None
        )
    
    def remove_default(
        self, 
        extension: str,
        dry_run: bool = False
    ) -> OperationResult:
        """Remove custom file association."""
        ext = extension if extension.startswith(".") else f".{extension}"
        prog_id = f"vince.{ext[1:]}"
        previous = self.get_current_default(extension)
        
        if dry_run:
            return OperationResult(
                success=True,
                message=f"Would remove {prog_id} association",
                previous_default=previous
            )
        
        try:
            # Remove ProgID
            self._delete_key_recursive(
                winreg.HKEY_CURRENT_USER, 
                f"Software\\Classes\\{prog_id}"
            )
            
            # Remove extension association
            self._delete_key_recursive(
                winreg.HKEY_CURRENT_USER,
                f"Software\\Classes\\{ext}"
            )
            
            # Notify shell
            self._notify_shell()
            
            return OperationResult(
                success=True,
                message=f"Removed custom default for {extension}",
                previous_default=previous
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to remove: {e}",
                error_code="VE605"
            )
    
    def _delete_key_recursive(self, hkey, key_path: str) -> None:
        """Recursively delete a registry key."""
        try:
            with winreg.OpenKey(hkey, key_path, 0, 
                               winreg.KEY_ALL_ACCESS) as key:
                while True:
                    try:
                        subkey = winreg.EnumKey(key, 0)
                        self._delete_key_recursive(hkey, f"{key_path}\\{subkey}")
                    except WindowsError:
                        break
            winreg.DeleteKey(hkey, key_path)
        except WindowsError:
            pass
```

### UTI Mapping Table

```python
# vince/platform/uti_map.py
"""Extension to UTI (Uniform Type Identifier) mapping for macOS."""

from typing import Optional

# Mapping of file extensions to macOS UTIs
UTI_MAP = {
    ".md": "net.daringfireball.markdown",
    ".markdown": "net.daringfireball.markdown",
    ".py": "public.python-script",
    ".python": "public.python-script",
    ".txt": "public.plain-text",
    ".text": "public.plain-text",
    ".js": "com.netscape.javascript-source",
    ".javascript": "com.netscape.javascript-source",
    ".html": "public.html",
    ".htm": "public.html",
    ".css": "public.css",
    ".json": "public.json",
    ".yml": "public.yaml",
    ".yaml": "public.yaml",
    ".xml": "public.xml",
    ".csv": "public.comma-separated-values-text",
    ".sql": "public.sql",
}

def extension_to_uti(extension: str) -> Optional[str]:
    """Convert file extension to macOS UTI."""
    ext = extension.lower()
    if not ext.startswith("."):
        ext = f".{ext}"
    return UTI_MAP.get(ext)

def uti_to_extension(uti: str) -> Optional[str]:
    """Convert UTI back to primary extension."""
    for ext, mapped_uti in UTI_MAP.items():
        if mapped_uti == uti:
            return ext
    return None
```

## Data Models

### Updated DefaultEntry Schema

The existing `defaults.json` schema is extended to track OS sync status:

```json
{
  "version": "1.1.0",
  "defaults": [
    {
      "id": "def-md-000",
      "extension": ".md",
      "application_path": "/Applications/Visual Studio Code.app",
      "application_name": "Visual Studio Code",
      "state": "active",
      "os_synced": true,
      "os_synced_at": "2025-01-01T12:00:00Z",
      "previous_os_default": "/Applications/TextEdit.app",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

New fields:
- `os_synced`: Boolean indicating if the OS has been configured
- `os_synced_at`: Timestamp of last successful OS sync
- `previous_os_default`: The OS default before vince changed it (for rollback)



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Platform Detection Consistency

*For any* execution of vince, the detected platform SHALL remain constant throughout the session and match the actual operating system.

**Validates: Requirements 1.1, 1.2**

### Property 2: Set-Query Round Trip

*For any* valid application path and supported extension, if `set_default(ext, app_path)` succeeds, then `get_current_default(ext)` SHALL return a path that resolves to the same application.

**Validates: Requirements 2.1, 2.4, 3.1, 3.5**

### Property 3: Dry Run Idempotence

*For any* command with the `-dry` flag, the OS state before and after execution SHALL be identical (no side effects).

**Validates: Requirements 7.1, 7.2**

### Property 4: Rollback Restoration

*For any* failed OS operation where rollback is attempted, if rollback succeeds, then `get_current_default(ext)` SHALL return the `previous_default` value recorded before the operation.

**Validates: Requirements 9.1, 9.2**

### Property 5: Sync Completeness

*For any* set of active defaults in the JSON store, after running `sync`, each entry with `os_synced=true` SHALL have a matching OS default (verified via `get_current_default`).

**Validates: Requirements 6.1, 6.2**

### Property 6: Error Code Specificity

*For any* OS operation failure, the returned error code SHALL be in the VE6xx range and SHALL match the specific failure type (platform, bundle ID, registry, etc.).

**Validates: Requirements 8.1, 8.2, 8.3**

### Property 7: Remove Clears Association

*For any* extension with an active vince-set default, after `remove_default(ext)` succeeds, the OS default SHALL either be the `previous_os_default` or the system default (not the vince-set application).

**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

## Error Handling

### New Error Classes

```python
# vince/platform/errors.py
from vince.errors import VinceError

class UnsupportedPlatformError(VinceError):
    """VE601: Platform not supported."""
    def __init__(self, platform: str):
        super().__init__(
            code="VE601",
            message=f"Unsupported platform: {platform}",
            recovery="vince supports macOS and Windows only"
        )

class BundleIdNotFoundError(VinceError):
    """VE602: Cannot determine macOS bundle ID."""
    def __init__(self, app_path: str):
        super().__init__(
            code="VE602",
            message=f"Cannot determine bundle ID for: {app_path}",
            recovery="Ensure the path points to a valid .app bundle"
        )

class RegistryAccessError(VinceError):
    """VE603: Windows registry access denied."""
    def __init__(self, operation: str):
        super().__init__(
            code="VE603",
            message=f"Registry access denied: {operation}",
            recovery="Run vince as administrator or check permissions"
        )

class ApplicationNotFoundError(VinceError):
    """VE604: Application not found or invalid."""
    def __init__(self, app_path: str):
        super().__init__(
            code="VE604",
            message=f"Application not found or invalid: {app_path}",
            recovery="Verify the application path exists and is executable"
        )

class OSOperationError(VinceError):
    """VE605: Generic OS operation failure."""
    def __init__(self, operation: str, details: str):
        super().__init__(
            code="VE605",
            message=f"OS operation failed: {operation} - {details}",
            recovery="Check system logs for details"
        )

class SyncPartialError(VinceError):
    """VE606: Sync completed with some failures."""
    def __init__(self, succeeded: int, failed: int, failures: list):
        super().__init__(
            code="VE606",
            message=f"Sync partially failed: {succeeded} succeeded, {failed} failed",
            recovery=f"Failed extensions: {', '.join(failures)}"
        )
```

### Error Handling Flow

```
┌─────────────────┐
│  OS Operation   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Record Previous │────▶│ Execute Change  │
│    Default      │     └────────┬────────┘
└─────────────────┘              │
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
           ┌───────────────┐         ┌───────────────┐
           │    Success    │         │    Failure    │
           └───────┬───────┘         └───────┬───────┘
                   │                         │
                   ▼                         ▼
           ┌───────────────┐         ┌───────────────┐
           │ Update JSON   │         │ Attempt       │
           │ os_synced=true│         │ Rollback      │
           └───────────────┘         └───────┬───────┘
                                             │
                                ┌────────────┴────────────┐
                                │                         │
                                ▼                         ▼
                       ┌───────────────┐         ┌───────────────┐
                       │   Rollback    │         │   Rollback    │
                       │   Success     │         │   Failed      │
                       └───────┬───────┘         └───────┬───────┘
                               │                         │
                               ▼                         ▼
                       ┌───────────────┐         ┌───────────────┐
                       │ Return Error  │         │ Return Error  │
                       │ (original)    │         │ + Rollback Err│
                       └───────────────┘         └───────────────┘
```

## Testing Strategy

### Unit Tests

- Test platform detection on each OS
- Test UTI mapping completeness
- Test ProgID generation
- Test error class instantiation
- Mock OS calls for handler methods

### Property-Based Tests

Using Hypothesis to generate:
- Random valid extensions from supported set
- Random application paths (mocked to exist)
- Random sequences of set/remove operations

### Integration Tests

- Test actual OS changes on CI runners (macOS and Windows)
- Verify round-trip: set → query → verify match
- Test rollback by forcing failures
- Test sync with mixed success/failure scenarios

### Test Configuration

```python
# tests/conftest.py additions
import pytest
import sys

@pytest.fixture
def mock_macos_handler(mocker):
    """Mock macOS handler for cross-platform testing."""
    if sys.platform != "darwin":
        mocker.patch("vince.platform.macos.subprocess.run")
        mocker.patch("vince.platform.macos.MacOSHandler._get_bundle_id", 
                     return_value="com.test.app")
    return mocker

@pytest.fixture
def mock_windows_handler(mocker):
    """Mock Windows handler for cross-platform testing."""
    if sys.platform != "win32":
        mocker.patch("vince.platform.windows.winreg")
        mocker.patch("vince.platform.windows.ctypes")
    return mocker

@pytest.fixture
def platform_handler(mock_macos_handler, mock_windows_handler):
    """Get appropriate handler with mocks applied."""
    from vince.platform import get_handler
    return get_handler()
```

## Dependencies

### macOS

- **Required**: None (uses built-in `defaults` command)
- **Recommended**: `duti` (install via `brew install duti`) for more reliable operation
- **Optional**: `PyObjC` for direct Launch Services access

### Windows

- **Required**: None (uses built-in `winreg` module)
- **Required**: `ctypes` (built-in) for shell notification

### pyproject.toml Updates

```toml
[project.optional-dependencies]
macos = [
    "pyobjc-framework-LaunchServices>=9.0",
]
```
