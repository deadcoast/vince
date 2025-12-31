"""Vince CLI Error System.

This module defines all error classes for the vince CLI application.
Error codes follow the format VE{category}{number}:
- VE1xx: Input errors
- VE2xx: File errors
- VE3xx: State errors
- VE4xx: Config errors
- VE5xx: System errors
"""

from dataclasses import dataclass
from typing import Optional

from rich.console import Console

console = Console()


@dataclass
class VinceError(Exception):
    """Base exception for vince CLI errors.

    Attributes:
        code: Error code in format VE{category}{number}
        message: Human-readable error message
        recovery: Optional recovery action suggestion
    """

    code: str
    message: str
    recovery: Optional[str] = None

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


# =============================================================================
# Input Errors (VE1xx)
# =============================================================================


class InvalidPathError(VinceError):
    """VE101: Invalid path - path does not exist or is not a file."""

    def __init__(self, path: str):
        super().__init__(
            code="VE101",
            message=f"Invalid path: {path} does not exist",
            recovery="Verify the application path exists and is accessible",
        )


class InvalidExtensionError(VinceError):
    """VE102: Invalid extension - extension is not supported."""

    def __init__(self, ext: str):
        super().__init__(
            code="VE102",
            message=f"Invalid extension: {ext} is not supported",
            recovery="Use a supported extension (--md, --py, etc.)",
        )


class InvalidOfferIdError(VinceError):
    """VE103: Invalid offer_id - does not match required pattern."""

    def __init__(self, offer_id: str):
        super().__init__(
            code="VE103",
            message=f"Invalid offer_id: {offer_id} does not match pattern",
            recovery="Use lowercase alphanumeric with hyphens/underscores (max 32 chars)",
        )


class OfferNotFoundError(VinceError):
    """VE104: Offer not found - the specified offer does not exist."""

    def __init__(self, offer_id: str):
        super().__init__(
            code="VE104",
            message=f"Offer not found: {offer_id} does not exist",
            recovery="Use `list -off` to see available offers",
        )


class InvalidSubsectionError(VinceError):
    """VE105: Invalid list subsection."""

    def __init__(self, section: str):
        super().__init__(
            code="VE105",
            message=f"Invalid list subsection: {section}",
            recovery="Use -app, -cmd, -ext, -def, -off, or -all",
        )


# =============================================================================
# File Errors (VE2xx)
# =============================================================================


class VinceFileNotFoundError(VinceError):
    """VE201: File not found."""

    def __init__(self, path: str):
        super().__init__(
            code="VE201",
            message=f"File not found: {path}",
            recovery="Check file path and ensure the file exists",
        )


class PermissionDeniedError(VinceError):
    """VE202: Permission denied - cannot access file."""

    def __init__(self, path: str):
        super().__init__(
            code="VE202",
            message=f"Permission denied: cannot access {path}",
            recovery="Check file permissions and ownership",
        )


class DataCorruptedError(VinceError):
    """VE203: Data file corrupted."""

    def __init__(self, file: str):
        super().__init__(
            code="VE203",
            message=f"Data file corrupted: {file}",
            recovery="Restore from backup or delete and recreate the data file",
        )


# =============================================================================
# State Errors (VE3xx)
# =============================================================================


class DefaultExistsError(VinceError):
    """VE301: Default already exists for extension."""

    def __init__(self, ext: str):
        super().__init__(
            code="VE301",
            message=f"Default already exists for {ext}",
            recovery="Use `chop` to remove existing default first",
        )


class NoDefaultError(VinceError):
    """VE302: No default set for extension."""

    def __init__(self, ext: str):
        super().__init__(
            code="VE302",
            message=f"No default set for {ext}",
            recovery="Use `slap` or `set` to create a default",
        )


class OfferExistsError(VinceError):
    """VE303: Offer already exists."""

    def __init__(self, offer_id: str):
        super().__init__(
            code="VE303",
            message=f"Offer already exists: {offer_id}",
            recovery="Use a different offer_id or reject existing offer",
        )


class OfferInUseError(VinceError):
    """VE304: Cannot reject offer that is in use."""

    def __init__(self, offer_id: str):
        super().__init__(
            code="VE304",
            message=f"Cannot reject: offer {offer_id} is in use",
            recovery="Remove dependencies before rejecting",
        )


# =============================================================================
# Config Errors (VE4xx)
# =============================================================================


class InvalidConfigOptionError(VinceError):
    """VE401: Invalid config option."""

    def __init__(self, key: str):
        super().__init__(
            code="VE401",
            message=f"Invalid config option: {key}",
            recovery="Check config.md for valid configuration options",
        )


class ConfigMalformedError(VinceError):
    """VE402: Config file malformed."""

    def __init__(self, file: str):
        super().__init__(
            code="VE402",
            message=f"Config file malformed: {file}",
            recovery="Fix JSON syntax errors or restore default config",
        )


# =============================================================================
# System Errors (VE5xx)
# =============================================================================


class UnexpectedError(VinceError):
    """VE501: Unexpected error."""

    def __init__(self, message: str):
        super().__init__(
            code="VE501",
            message=f"Unexpected error: {message}",
            recovery="Report issue with full error details to maintainers",
        )


# =============================================================================
# Error Handler
# =============================================================================


def handle_error(error: VinceError) -> None:
    """Display error and exit with appropriate code.

    Args:
        error: The VinceError to display

    Raises:
        SystemExit: Always exits with code 1
    """
    console.print(f"[red bold]✗ {error.code}:[/] {error.message}")
    if error.recovery:
        console.print(f"[cyan]ℹ[/] {error.recovery}")
    raise SystemExit(1)
