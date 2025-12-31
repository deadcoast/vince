"""Path validation for vince CLI.

This module provides validation functions for application paths.
Validates that paths exist, are files, and are executable.
"""

import os
from pathlib import Path

from vince.errors import InvalidPathError, PermissionDeniedError


def validate_path(path: Path) -> Path:
    """Validate application path exists and is executable.

    Performs three checks:
    1. Path exists (using Path.exists())
    2. Path is a file (using Path.is_file())
    3. Path is executable (using os.access with X_OK)

    Args:
        path: Path to the application executable

    Returns:
        The resolved absolute path if validation passes

    Raises:
        InvalidPathError: If path doesn't exist or isn't a file (VE101)
        PermissionDeniedError: If path isn't executable (VE202)
    """
    # Resolve to absolute path
    resolved_path = path.resolve()

    # Check if path exists
    if not resolved_path.exists():
        raise InvalidPathError(str(resolved_path))

    # Check if path is a file (not a directory)
    if not resolved_path.is_file():
        raise InvalidPathError(str(resolved_path))

    # Check if path is executable
    if not os.access(resolved_path, os.X_OK):
        raise PermissionDeniedError(str(resolved_path))

    return resolved_path
