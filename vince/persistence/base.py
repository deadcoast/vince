"""Base persistence functions for vince CLI.

This module provides core file operations with atomic writes,
file locking, backup management, and JSON loading with defaults.
"""

import copy
import fcntl
import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator

from vince.errors import DataCorruptedError


@contextmanager
def file_lock(path: Path) -> Generator[None, None, None]:
    """Acquire exclusive lock on file for write operations.

    Uses fcntl for POSIX-compliant file locking to prevent
    concurrent writes from corrupting data.

    Args:
        path: Path to the file to lock

    Yields:
        None - context manager for lock scope

    Example:
        with file_lock(data_path):
            atomic_write(data_path, data)
    """
    lock_path = path.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with open(lock_path, "w") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def atomic_write(path: Path, data: Dict[str, Any]) -> None:
    """Write data atomically using temp file + rename pattern.

    This ensures data integrity by writing to a temporary file
    first, then atomically renaming it to the target path.
    If the write fails, the original file remains unchanged.

    Args:
        path: Target file path
        data: Dictionary data to write as JSON

    Raises:
        Exception: Re-raises any exception after cleanup
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")

    try:
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        temp_path.rename(path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def create_backup(path: Path, backup_dir: Path, max_backups: int = 5) -> None:
    """Create timestamped backup of file.

    Creates a backup copy with ISO 8601 timestamp in the filename.
    Automatically cleans up old backups when max_backups is exceeded.

    Args:
        path: Path to the file to backup
        backup_dir: Directory to store backup files
        max_backups: Maximum number of backups to retain (default: 5)

    Note:
        If the source file doesn't exist, no backup is created.
        Backup filename format: {stem}.{timestamp}.bak
        Timestamp format uses hyphens instead of colons for filesystem compatibility.
    """
    if not path.exists():
        return

    backup_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamp with filesystem-safe format (replace colons with hyphens)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%SZ")
    backup_name = f"{path.stem}.{timestamp}.bak"
    backup_path = backup_dir / backup_name

    # Copy current file to backup
    backup_path.write_text(path.read_text())

    # Cleanup old backups - keep only max_backups most recent
    backups = sorted(backup_dir.glob(f"{path.stem}.*.bak"))
    while len(backups) > max_backups:
        backups[0].unlink()
        backups.pop(0)


def load_json(
    path: Path,
    default: Dict[str, Any],
    schema_name: str | None = None,
) -> Dict[str, Any]:
    """Load JSON file with fallback to default and optional schema validation.

    Attempts to load and parse a JSON file. If the file doesn't exist,
    returns a deep copy of the default schema. If the file is corrupted
    (invalid JSON), raises DataCorruptedError.

    Args:
        path: Path to the JSON file
        default: Default schema to return if file doesn't exist
        schema_name: Optional schema name for validation (e.g., 'defaults', 'offers', 'config')

    Returns:
        Parsed JSON data or deep copy of default schema

    Raises:
        DataCorruptedError: If file exists but contains invalid JSON or fails schema validation
    """
    if not path.exists():
        return copy.deepcopy(default)

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        raise DataCorruptedError(str(path))

    # Validate against schema if specified
    if schema_name:
        try:
            from vince.validation.schema import validate_against_schema

            validate_against_schema(data, schema_name)
        except ImportError:
            # jsonschema not installed, skip validation
            pass

    return data
