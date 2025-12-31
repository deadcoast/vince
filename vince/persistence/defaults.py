"""DefaultsStore for managing defaults.json persistence.

This module provides the DefaultsStore class for managing
application-to-extension default associations.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from vince.persistence.base import atomic_write, create_backup, file_lock, load_json


# Default schema for defaults.json
DEFAULT_SCHEMA: Dict[str, Any] = {
    "version": "1.0.0",
    "defaults": []
}


class DefaultsStore:
    """Store for managing default application associations.
    
    Handles persistence of defaults.json with atomic writes,
    file locking, and backup support.
    
    Attributes:
        path: Path to defaults.json file
        backup_dir: Path to backup directory
    """
    
    def __init__(self, data_dir: Path) -> None:
        """Initialize DefaultsStore with data directory.
        
        Args:
            data_dir: Base directory for data storage
        """
        self.path = data_dir / "defaults.json"
        self.backup_dir = data_dir / "backups"
    
    def load(self) -> Dict[str, Any]:
        """Load defaults data from JSON file.
        
        Returns:
            Dictionary containing version and defaults array.
            Returns default schema if file doesn't exist.
            
        Raises:
            DataCorruptedError: If file contains invalid JSON
        """
        return load_json(self.path, DEFAULT_SCHEMA)
    
    def save(self, data: Dict[str, Any], backup_enabled: bool = True, max_backups: int = 5) -> None:
        """Save defaults data to JSON file atomically.
        
        Args:
            data: Dictionary containing version and defaults array
            backup_enabled: Whether to create backup before write
            max_backups: Maximum number of backups to retain
        """
        with file_lock(self.path):
            if backup_enabled:
                create_backup(self.path, self.backup_dir, max_backups)
            atomic_write(self.path, data)
    
    def find_by_extension(self, ext: str) -> Optional[Dict[str, Any]]:
        """Find active or pending default entry by extension.
        
        Args:
            ext: File extension including dot (e.g., ".md")
            
        Returns:
            Default entry dictionary if found and not removed, None otherwise
        """
        data = self.load()
        for entry in data["defaults"]:
            if entry["extension"] == ext and entry["state"] != "removed":
                return entry
        return None
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Get all default entries.
        
        Returns:
            List of all default entry dictionaries
        """
        data = self.load()
        return data["defaults"]
    
    def add(
        self,
        extension: str,
        application_path: str,
        state: str = "pending",
        application_name: Optional[str] = None,
        backup_enabled: bool = True,
        max_backups: int = 5
    ) -> Dict[str, Any]:
        """Add a new default entry.
        
        Args:
            extension: File extension including dot (e.g., ".md")
            application_path: Absolute path to application executable
            state: Initial state ("pending" or "active")
            application_name: Optional human-readable application name
            backup_enabled: Whether to create backup before write
            max_backups: Maximum number of backups to retain
            
        Returns:
            The created default entry dictionary
        """
        data = self.load()
        
        # Generate unique ID
        entry_id = f"def-{extension[1:]}-{len(data['defaults']):03d}"
        
        # Create entry
        entry: Dict[str, Any] = {
            "id": entry_id,
            "extension": extension,
            "application_path": application_path,
            "state": state,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        if application_name:
            entry["application_name"] = application_name
        
        data["defaults"].append(entry)
        self.save(data, backup_enabled, max_backups)
        
        return entry
    
    def update_state(
        self,
        entry_id: str,
        new_state: str,
        backup_enabled: bool = True,
        max_backups: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Update the state of a default entry.
        
        Args:
            entry_id: Unique identifier of the entry to update
            new_state: New state value ("pending", "active", or "removed")
            backup_enabled: Whether to create backup before write
            max_backups: Maximum number of backups to retain
            
        Returns:
            Updated entry dictionary if found, None otherwise
        """
        data = self.load()
        
        for entry in data["defaults"]:
            if entry["id"] == entry_id:
                entry["state"] = new_state
                entry["updated_at"] = datetime.now(timezone.utc).isoformat()
                self.save(data, backup_enabled, max_backups)
                return entry
        
        return None
    
    def find_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Find default entry by ID.
        
        Args:
            entry_id: Unique identifier of the entry
            
        Returns:
            Default entry dictionary if found, None otherwise
        """
        data = self.load()
        for entry in data["defaults"]:
            if entry["id"] == entry_id:
                return entry
        return None
