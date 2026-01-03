"""JSON Schema validation for vince data files."""

import json
from pathlib import Path
from typing import Any

from vince.errors import DataCorruptedError, InvalidConfigOptionError

# Schema directory relative to this file
SCHEMA_DIR = Path(__file__).parent.parent.parent / "schemas"


def load_schema(schema_name: str) -> dict[str, Any]:
    """Load a JSON schema from the schemas directory.
    
    Args:
        schema_name: Name of the schema file (e.g., 'defaults', 'offers', 'config')
        
    Returns:
        The parsed JSON schema as a dictionary
        
    Raises:
        FileNotFoundError: If the schema file doesn't exist
    """
    schema_path = SCHEMA_DIR / f"{schema_name}.schema.json"
    with open(schema_path) as f:
        return json.load(f)


def validate_against_schema(data: dict[str, Any], schema_name: str) -> None:
    """Validate data against a JSON schema.
    
    Args:
        data: The data to validate
        schema_name: Name of the schema to validate against
        
    Raises:
        DataCorruptedError: If validation fails for data files
        InvalidConfigOptionError: If validation fails for config
    """
    try:
        import jsonschema
    except ImportError:
        # jsonschema not installed, skip validation
        return
    
    schema = load_schema(schema_name)
    
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        if schema_name == "config":
            # Extract the field name from the error path
            field = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
            raise InvalidConfigOptionError(field) from e
        else:
            raise DataCorruptedError(f"{schema_name}.json: {e.message}") from e


def validate_defaults(data: dict[str, Any]) -> None:
    """Validate defaults.json data against its schema."""
    validate_against_schema(data, "defaults")


def validate_offers(data: dict[str, Any]) -> None:
    """Validate offers.json data against its schema."""
    validate_against_schema(data, "offers")


def validate_config(data: dict[str, Any]) -> None:
    """Validate config.json data against its schema."""
    validate_against_schema(data, "config")
