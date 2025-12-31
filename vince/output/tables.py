"""Vince CLI table output functions."""

from typing import Any, Dict, List

from rich import box
from rich.table import Table


def create_defaults_table(defaults: List[Dict[str, Any]]) -> Table:
    """Create a Rich table for displaying defaults.

    Args:
        defaults: List of default entries with extension, application_path, and state

    Returns:
        A Rich Table configured for displaying defaults
    """
    table = Table(title="Defaults", box=box.ROUNDED, header_style="header")
    table.add_column("Extension", style="extension")
    table.add_column("Application", style="path")
    table.add_column("State", style="state")

    for d in defaults:
        table.add_row(
            d.get("extension", ""), d.get("application_path", ""), d.get("state", "")
        )

    return table


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
