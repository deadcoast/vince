"""Vince CLI Configuration System.

This module provides configuration loading and merging with hierarchy support.
Configuration precedence: project > user > default.

Config files are loaded from:
- Built-in defaults (hardcoded)
- User config: ~/.vince/config.json
- Project config: ./.vince/config.json
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from vince.errors import ConfigMalformedError, InvalidConfigOptionError

# =============================================================================
# Default Configuration
# =============================================================================

DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "1.0.0",
    "data_dir": "~/.vince",
    "verbose": False,
    "color_theme": "default",
    "backup_enabled": True,
    "max_backups": 5,
    "confirm_destructive": True,
}

# Valid values for enum options
VALID_COLOR_THEMES = {"default", "dark", "light"}

# Valid config keys
VALID_CONFIG_KEYS = set(DEFAULT_CONFIG.keys())

# Version pattern for validation
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


# =============================================================================
# Config Validation
# =============================================================================


def validate_config_option(key: str, value: Any) -> None:
    """Validate a single configuration option.

    Args:
        key: Configuration key name
        value: Configuration value to validate

    Raises:
        InvalidConfigOptionError: If key is unknown or value is invalid
    """
    if key not in VALID_CONFIG_KEYS:
        raise InvalidConfigOptionError(key)

    # Type validation based on key
    if key == "version":
        if not isinstance(value, str):
            raise InvalidConfigOptionError(
                f"{key} (expected string, got {type(value).__name__})"
            )
        if not VERSION_PATTERN.match(value):
            raise InvalidConfigOptionError(f"{key} (must match pattern X.Y.Z)")

    elif key == "data_dir":
        if not isinstance(value, str):
            raise InvalidConfigOptionError(
                f"{key} (expected string, got {type(value).__name__})"
            )

    elif key == "verbose":
        if not isinstance(value, bool):
            raise InvalidConfigOptionError(
                f"{key} (expected boolean, got {type(value).__name__})"
            )

    elif key == "color_theme":
        if not isinstance(value, str):
            raise InvalidConfigOptionError(
                f"{key} (expected string, got {type(value).__name__})"
            )
        if value not in VALID_COLOR_THEMES:
            raise InvalidConfigOptionError(
                f"{key} (must be one of: {', '.join(sorted(VALID_COLOR_THEMES))})"
            )

    elif key == "backup_enabled":
        if not isinstance(value, bool):
            raise InvalidConfigOptionError(
                f"{key} (expected boolean, got {type(value).__name__})"
            )

    elif key == "max_backups":
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidConfigOptionError(
                f"{key} (expected integer, got {type(value).__name__})"
            )
        if value < 0 or value > 100:
            raise InvalidConfigOptionError(f"{key} (must be between 0 and 100)")

    elif key == "confirm_destructive":
        if not isinstance(value, bool):
            raise InvalidConfigOptionError(
                f"{key} (expected boolean, got {type(value).__name__})"
            )


def validate_config(config: Dict[str, Any]) -> None:
    """Validate all options in a configuration dictionary.

    Args:
        config: Configuration dictionary to validate

    Raises:
        InvalidConfigOptionError: If any option is invalid
    """
    for key, value in config.items():
        validate_config_option(key, value)


# =============================================================================
# Config Loading
# =============================================================================


def load_config_file(path: Path, validate: bool = True) -> Optional[Dict[str, Any]]:
    """Load a configuration file from disk.

    Args:
        path: Path to the configuration file
        validate: Whether to validate the loaded config

    Returns:
        Configuration dictionary if file exists, None otherwise

    Raises:
        ConfigMalformedError: If file contains invalid JSON or is not a dict
        InvalidConfigOptionError: If validation is enabled and config is invalid
    """
    if not path.exists():
        return None

    try:
        content = path.read_text()
        config = json.loads(content)
    except json.JSONDecodeError:
        raise ConfigMalformedError(str(path))

    # Config must be a dictionary
    if not isinstance(config, dict):
        raise ConfigMalformedError(str(path))

    if validate:
        validate_config(config)

    return config


def merge_configs(*configs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries.

    Later configs override earlier ones (shallow merge).
    None values are skipped.

    Args:
        *configs: Configuration dictionaries to merge (lowest to highest priority)

    Returns:
        Merged configuration dictionary
    """
    result = {}
    for config in configs:
        if config is not None:
            result.update(config)
    return result


def get_config(
    user_config_path: Optional[Path] = None,
    project_config_path: Optional[Path] = None,
    validate: bool = True,
) -> Dict[str, Any]:
    """Load and merge configuration from all levels.

    Configuration is loaded and merged with precedence:
    project > user > default

    Args:
        user_config_path: Override path for user config (default: ~/.vince/config.json)
        project_config_path: Override path for project config (default: ./.vince/config.json)
        validate: Whether to validate loaded configs

    Returns:
        Merged configuration dictionary with all options

    Raises:
        ConfigMalformedError: If any config file contains invalid JSON
        InvalidConfigOptionError: If validation is enabled and any config is invalid
    """
    # Determine config paths
    if user_config_path is None:
        user_config_path = Path("~/.vince/config.json").expanduser()

    if project_config_path is None:
        project_config_path = Path("./.vince/config.json")

    # Load configs (lowest to highest priority)
    user_config = load_config_file(user_config_path, validate=validate)
    project_config = load_config_file(project_config_path, validate=validate)

    # Merge with precedence: project > user > default
    merged = merge_configs(DEFAULT_CONFIG, user_config, project_config)

    return merged


def get_data_dir(config: Optional[Dict[str, Any]] = None) -> Path:
    """Get the data directory path from config.

    Args:
        config: Configuration dictionary (loads default if None)

    Returns:
        Expanded Path to the data directory
    """
    if config is None:
        config = get_config()

    data_dir = config.get("data_dir", DEFAULT_CONFIG["data_dir"])
    return Path(data_dir).expanduser()
