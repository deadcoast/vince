"""JSON Schema validation for vince data files.

This module provides schema validation using the jsonschema library.
Validation is optional - if jsonschema is not installed, validation
is silently skipped.
"""

import json
from pathlib import Path
from typing import Any, Dict

from vince.errors import DataCorruptedError, InvalidConfigOptionError

# Schema directory relative to this file
SCHEMA_DIR = Path(__file__).parent.parent.parent / "schemas"


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load a JSON schema from the schemas directory.

    Args:
        schema_name: Name of the schema (without .schema.json extension)
                     e.g., 'defaults', 'offers', 'config'

    Returns:
        Parsed JSON schema dictionary

    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file contains invalid JSON
    """
    schema_path = SCHEMA_DIR / f"{schema_name}.schema.json"
    with open(schema_path) as f:
        return json.load(f)


def validate_against_schema(data: Dict[str, Any], schema_name: str) -> None:
    """Validate data against a JSON schema.

    Uses the jsonschema library for validation. If jsonschema is not
    installed, validation is silently skipped.

    Args:
        data: Dictionary data to validate
        schema_name: Name of the schema to validate against
                     ('defaults', 'offers', or 'config')

    Raises:
        DataCorruptedError: If validation fails for defaults or offers schema
        InvalidConfigOptionError: If validation fails for config schema

    Note:
        If jsonschema library is not installed, this function returns
        without performing validation (graceful degradation).
    """
    try:
        import jsonschema
    except ImportError:
        # Skip validation if jsonschema not installed
        return

    schema = load_schema(schema_name)
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        if schema_name == "config":
            # Extract field path for config errors
            field = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
            raise InvalidConfigOptionError(field) from e
        else:
            # For defaults/offers, raise DataCorruptedError
            raise DataCorruptedError(f"{schema_name}.json: {e.message}") from e


def validate_defaults(data: Dict[str, Any]) -> None:
    """Validate defaults.json data against its schema.

    Args:
        data: Dictionary containing version and defaults array

    Raises:
        DataCorruptedError: If validation fails
    """
    validate_against_schema(data, "defaults")


def validate_offers(data: Dict[str, Any]) -> None:
    """Validate offers.json data against its schema.

    Args:
        data: Dictionary containing version and offers array

    Raises:
        DataCorruptedError: If validation fails
    """
    validate_against_schema(data, "offers")


def validate_config(data: Dict[str, Any]) -> None:
    """Validate config.json data against its schema.

    Args:
        data: Dictionary containing configuration options

    Raises:
        InvalidConfigOptionError: If validation fails
    """
    validate_against_schema(data, "config")
