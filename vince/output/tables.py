"""Vince CLI table output functions."""

from typing import Any, Dict, List, Optional

from rich import box
from rich.table import Table
from rich.text import Text


def create_defaults_table(
    defaults: List[Dict[str, Any]],
    os_defaults: Optional[Dict[str, Optional[str]]] = None,
) -> Table:
    """Create a Rich table for displaying defaults.

    Args:
        defaults: List of default entries with extension, application_path, and state
        os_defaults: Optional dict mapping extension to OS default path.
                     If provided, adds "OS Default" column with mismatch indicators.

    Returns:
        A Rich Table configured for displaying defaults

    Requirements: 4.2, 4.3
    """
    table = Table(title="Defaults", box=box.ROUNDED, header_style="header")
    table.add_column("Extension", style="extension")
    table.add_column("Application", style="path")
    table.add_column("State", style="state")

    # Add OS Default column if os_defaults provided
    if os_defaults is not None:
        table.add_column("OS Default", style="path")
        table.add_column("Sync", justify="center")

    for d in defaults:
        extension = d.get("extension", "")
        app_path = d.get("application_path", "")
        state = d.get("state", "")

        if os_defaults is not None:
            os_default = os_defaults.get(extension)
            os_default_display = os_default if os_default else "unknown"

            # Determine sync status with mismatch indicator
            sync_status = _get_sync_status(app_path, os_default)

            table.add_row(extension, app_path, state, os_default_display, sync_status)
        else:
            table.add_row(extension, app_path, state)

    return table


def _get_sync_status(vince_path: str, os_default: Optional[str]) -> Text:
    """Get sync status indicator for vince vs OS default comparison.

    Args:
        vince_path: The application path set in vince
        os_default: The current OS default path (None if unknown)

    Returns:
        Rich Text with styled sync indicator:
        - "✓" (green) if paths match
        - "⚠" (yellow/warning) if paths differ (mismatch)
        - "?" (dim) if OS default is unknown

    Requirements: 4.3
    """
    if os_default is None:
        return Text("?", style="dim")

    # Normalize paths for comparison (handle trailing slashes, case on Windows, etc.)
    vince_normalized = _normalize_path(vince_path)
    os_normalized = _normalize_path(os_default)

    if vince_normalized == os_normalized:
        return Text("✓", style="success")
    else:
        return Text("⚠", style="warning")


def _normalize_path(path: str) -> str:
    """Normalize a path for comparison.

    Args:
        path: Path string to normalize

    Returns:
        Normalized path string (lowercase, no trailing slash)
    """
    if not path:
        return ""
    # Remove trailing slashes and normalize
    normalized = path.rstrip("/\\")
    # On macOS/Linux paths are case-sensitive, but we do basic normalization
    return normalized


def create_offers_table(offers: List[Dict[str, Any]]) -> Table:
    """Create a Rich table for displaying offers.

    Args:
        offers: List of offer entries with offer_id, default_id, and state

    Returns:
        A Rich Table configured for displaying offers
    """
    table = Table(title="Offers", box=box.ROUNDED, header_style="header")
    table.add_column("Offer ID", style="offer")
    table.add_column("Default ID", style="info")
    table.add_column("State", style="state")

    for o in offers:
        table.add_row(
            o.get("offer_id", ""), o.get("default_id", ""), o.get("state", "")
        )

    return table
