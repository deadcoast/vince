"""OffersStore for managing offers.json persistence.

This module provides the OffersStore class for managing
custom shortcut/alias definitions.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from vince.persistence.base import (atomic_write, create_backup, file_lock,
                                    load_json)

# Default schema for offers.json
DEFAULT_SCHEMA: Dict[str, Any] = {"version": "1.0.0", "offers": []}


class OffersStore:
    """Store for managing custom offer/alias definitions.

    Handles persistence of offers.json with atomic writes,
    file locking, and backup support.

    Attributes:
        path: Path to offers.json file
        backup_dir: Path to backup directory
    """

    def __init__(self, data_dir: Path) -> None:
        """Initialize OffersStore with data directory.

        Args:
            data_dir: Base directory for data storage
        """
        self.path = data_dir / "offers.json"
        self.backup_dir = data_dir / "backups"

    def load(self) -> Dict[str, Any]:
        """Load offers data from JSON file.

        Returns:
            Dictionary containing version and offers array.
            Returns default schema if file doesn't exist.

        Raises:
            DataCorruptedError: If file contains invalid JSON
        """
        return load_json(self.path, DEFAULT_SCHEMA)

    def save(
        self, data: Dict[str, Any], backup_enabled: bool = True, max_backups: int = 5
    ) -> None:
        """Save offers data to JSON file atomically.

        Args:
            data: Dictionary containing version and offers array
            backup_enabled: Whether to create backup before write
            max_backups: Maximum number of backups to retain
        """
        with file_lock(self.path):
            if backup_enabled:
                create_backup(self.path, self.backup_dir, max_backups)
            atomic_write(self.path, data)

    def find_by_id(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Find offer entry by offer_id.

        Args:
            offer_id: Unique offer identifier

        Returns:
            Offer entry dictionary if found and not rejected, None otherwise
        """
        data = self.load()
        for entry in data["offers"]:
            if entry["offer_id"] == offer_id and entry["state"] != "rejected":
                return entry
        return None

    def find_all(self) -> List[Dict[str, Any]]:
        """Get all offer entries.

        Returns:
            List of all offer entry dictionaries
        """
        data = self.load()
        return data["offers"]

    def add(
        self,
        offer_id: str,
        default_id: str,
        auto_created: bool = False,
        description: Optional[str] = None,
        backup_enabled: bool = True,
        max_backups: int = 5,
    ) -> Dict[str, Any]:
        """Add a new offer entry.

        Args:
            offer_id: Unique offer identifier
            default_id: Reference to associated default entry ID
            auto_created: Whether this offer was auto-created by slap -set
            description: Optional human-readable description
            backup_enabled: Whether to create backup before write
            max_backups: Maximum number of backups to retain

        Returns:
            The created offer entry dictionary
        """
        data = self.load()

        # Create entry
        entry: Dict[str, Any] = {
            "offer_id": offer_id,
            "default_id": default_id,
            "state": "created",
            "auto_created": auto_created,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if description:
            entry["description"] = description

        data["offers"].append(entry)
        self.save(data, backup_enabled, max_backups)

        return entry

    def update_state(
        self,
        offer_id: str,
        new_state: str,
        backup_enabled: bool = True,
        max_backups: int = 5,
    ) -> Optional[Dict[str, Any]]:
        """Update the state of an offer entry.

        Args:
            offer_id: Unique offer identifier
            new_state: New state value ("created", "active", or "rejected")
            backup_enabled: Whether to create backup before write
            max_backups: Maximum number of backups to retain

        Returns:
            Updated entry dictionary if found, None otherwise
        """
        data = self.load()

        for entry in data["offers"]:
            if entry["offer_id"] == offer_id:
                entry["state"] = new_state
                if new_state == "active":
                    entry["used_at"] = datetime.now(timezone.utc).isoformat()
                self.save(data, backup_enabled, max_backups)
                return entry

        return None

    def find_by_default_id(self, default_id: str) -> List[Dict[str, Any]]:
        """Find all offers associated with a default entry.

        Args:
            default_id: Reference to default entry ID

        Returns:
            List of offer entries associated with the default
        """
        data = self.load()
        return [entry for entry in data["offers"] if entry["default_id"] == default_id]
