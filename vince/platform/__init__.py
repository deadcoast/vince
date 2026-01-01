"""OS Integration Layer for vince.

This module provides a unified interface for platform-specific file association
operations. It detects the current platform and provides the appropriate handler.

Exports:
    - Platform: Enum of supported platforms
    - AppInfo: Application metadata dataclass
    - OperationResult: Operation result dataclass
    - PlatformHandler: Protocol for platform handlers
    - get_platform(): Detect current platform
    - get_handler(): Get platform-specific handler (singleton)

Requirements: 1.1, 1.2, 1.3
"""

import sys
from typing import Optional

from vince.platform.base import (
    AppInfo,
    OperationResult,
    Platform,
    PlatformHandler,
)
from vince.platform.errors import UnsupportedPlatformError
from vince.platform.uti_map import (
    UTI_MAP,
    extension_to_uti,
    get_all_utis,
    get_extensions_for_uti,
    uti_to_extension,
)

__all__ = [
    "Platform",
    "AppInfo",
    "OperationResult",
    "PlatformHandler",
    "get_platform",
    "get_handler",
    # UTI mapping exports
    "UTI_MAP",
    "extension_to_uti",
    "uti_to_extension",
    "get_all_utis",
    "get_extensions_for_uti",
]

# Singleton handler instance
_handler: Optional[PlatformHandler] = None


def get_platform() -> Platform:
    """Detect and return the current platform.

    Returns:
        Platform enum value for the current operating system:
        - Platform.MACOS for macOS (darwin)
        - Platform.WINDOWS for Windows (win32)
        - Platform.UNSUPPORTED for any other platform

    Requirements: 1.1, 1.3
    """
    if sys.platform == "darwin":
        return Platform.MACOS
    elif sys.platform == "win32":
        return Platform.WINDOWS
    return Platform.UNSUPPORTED


def get_handler() -> PlatformHandler:
    """Get the platform-specific handler (singleton).

    Returns a cached handler instance for the current platform.
    The handler is created on first call and reused thereafter.

    Returns:
        PlatformHandler implementation for the current platform

    Raises:
        UnsupportedPlatformError: If running on an unsupported platform

    Requirements: 1.1, 1.2
    """
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


def _reset_handler() -> None:
    """Reset the singleton handler (for testing only).

    This function is intended for use in tests to reset the
    singleton state between test cases.
    """
    global _handler
    _handler = None
