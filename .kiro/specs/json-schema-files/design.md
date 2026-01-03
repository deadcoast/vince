# Design Document

## Overview

This design extracts JSON Schema definitions from `docs/schemas.md` into actual `.json` schema files and integrates schema validation into the vince CLI persistence layer. The implementation uses the `jsonschema` library for validation with graceful degradation when not installed.

Reference: #[[file:docs/schemas.md]]

## Architecture

```
schemas/                          # Schema files directory
├── defaults.schema.json          # DefaultEntry schema (from docs/schemas.md)
├── offers.schema.json            # OfferEntry schema (from docs/schemas.md)
└── config.schema.json            # Config schema (from docs/schemas.md)

vince/
├── validation/
│   ├── __init__.py
│   ├── schema.py                 # NEW: Schema validation module
│   ├── extension.py
│   ├── offer_id.py
│   └── path.py
└── persistence/
    ├── base.py                   # MODIFIED: Add schema_name param to load_json()
    ├── defaults.py               # MODIFIED: Pass schema_name to load_json()
    └── offers.py                 # MODIFIED: Pass schema_name to load_json()
```

## Components and Interfaces

### Schema Files

Three JSON Schema Draft-07 files extracted verbatim from `docs/schemas.md`:

#### schemas/defaults.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://vince.cli/schemas/defaults.json",
  "title": "Vince Defaults",
  "type": "object",
  "properties": {
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "defaults": { "type": "array", "items": { "$ref": "#/definitions/DefaultEntry" } }
  },
  "required": ["version", "defaults"],
  "additionalProperties": false,
  "definitions": {
    "DefaultEntry": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "minLength": 1, "maxLength": 64 },
        "extension": { "type": "string", "pattern": "^\\.[a-z0-9]+$" },
        "application_path": { "type": "string", "minLength": 1 },
        "application_name": { "type": "string", "minLength": 1 },
        "state": { "type": "string", "enum": ["pending", "active", "removed"] },
        "os_synced": { "type": "boolean", "default": false },
        "os_synced_at": { "type": "string", "format": "date-time" },
        "previous_os_default": { "type": "string" },
        "created_at": { "type": "string", "format": "date-time" },
        "updated_at": { "type": "string", "format": "date-time" }
      },
      "required": ["id", "extension", "application_path", "state", "created_at"],
      "additionalProperties": false
    }
  }
}
```

#### schemas/offers.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://vince.cli/schemas/offers.json",
  "title": "Vince Offers",
  "type": "object",
  "properties": {
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "offers": { "type": "array", "items": { "$ref": "#/definitions/OfferEntry" } }
  },
  "required": ["version", "offers"],
  "additionalProperties": false,
  "definitions": {
    "OfferEntry": {
      "type": "object",
      "properties": {
        "offer_id": { "type": "string", "pattern": "^[a-z][a-z0-9_-]{0,31}$" },
        "default_id": { "type": "string", "minLength": 1 },
        "state": { "type": "string", "enum": ["created", "active", "rejected"] },
        "auto_created": { "type": "boolean", "default": false },
        "description": { "type": "string", "maxLength": 256 },
        "created_at": { "type": "string", "format": "date-time" },
        "used_at": { "type": "string", "format": "date-time" }
      },
      "required": ["offer_id", "default_id", "state", "created_at"],
      "additionalProperties": false
    }
  }
}
```

#### schemas/config.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://vince.cli/schemas/config.json",
  "title": "Vince Configuration",
  "type": "object",
  "properties": {
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "data_dir": { "type": "string", "default": "~/.vince" },
    "verbose": { "type": "boolean", "default": false },
    "color_theme": { "type": "string", "enum": ["default", "dark", "light"], "default": "default" },
    "backup_enabled": { "type": "boolean", "default": true },
    "max_backups": { "type": "integer", "minimum": 0, "maximum": 100, "default": 5 },
    "confirm_destructive": { "type": "boolean", "default": true }
  },
  "required": ["version"],
  "additionalProperties": false
}
```

### Schema Validation Module

#### vince/validation/schema.py

```python
"""JSON Schema validation for vince data files."""

import json
from pathlib import Path
from typing import Any

from vince.errors import DataCorruptedError, InvalidConfigOptionError

SCHEMA_DIR = Path(__file__).parent.parent.parent / "schemas"

def load_schema(schema_name: str) -> dict[str, Any]:
    """Load a JSON schema from the schemas directory."""
    schema_path = SCHEMA_DIR / f"{schema_name}.schema.json"
    with open(schema_path) as f:
        return json.load(f)

def validate_against_schema(data: dict[str, Any], schema_name: str) -> None:
    """Validate data against a JSON schema."""
    try:
        import jsonschema
    except ImportError:
        return  # Skip validation if jsonschema not installed
    
    schema = load_schema(schema_name)
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        if schema_name == "config":
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
```

### Persistence Layer Changes

#### vince/persistence/base.py - load_json() modification

```python
def load_json(
    path: Path,
    default: Dict[str, Any],
    schema_name: str | None = None,
) -> Dict[str, Any]:
    """Load JSON file with fallback to default and optional schema validation."""
    if not path.exists():
        return copy.deepcopy(default)

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        raise DataCorruptedError(str(path))

    if schema_name:
        try:
            from vince.validation.schema import validate_against_schema
            validate_against_schema(data, schema_name)
        except ImportError:
            pass  # jsonschema not installed

    return data
```

#### vince/persistence/defaults.py - load() modification

```python
def load(self) -> Dict[str, Any]:
    """Load defaults data from JSON file with schema validation."""
    data = load_json(self.path, DEFAULT_SCHEMA, schema_name="defaults")
    # ... migration logic ...
    return data
```

#### vince/persistence/offers.py - load() modification

```python
def load(self) -> Dict[str, Any]:
    """Load offers data from JSON file with schema validation."""
    return load_json(self.path, DEFAULT_SCHEMA, schema_name="offers")
```

## Data Models

Data models are defined by the JSON schemas. See `docs/schemas.md` for complete field definitions:

- **DefaultEntry**: id, extension, application_path, application_name, state, os_synced, os_synced_at, previous_os_default, created_at, updated_at
- **OfferEntry**: offer_id, default_id, state, auto_created, description, created_at, used_at
- **Config**: version, data_dir, verbose, color_theme, backup_enabled, max_backups, confirm_destructive

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system.*

### Property 1: Schema round-trip consistency

*For any* valid data dictionary that passes schema validation, serializing to JSON and deserializing back SHALL produce an equivalent dictionary that also passes validation.

**Validates: Requirements 1.1, 2.1, 3.1**

### Property 2: Invalid data rejection

*For any* data dictionary with a field violating schema constraints (wrong type, invalid pattern, out of range), validation SHALL raise the appropriate error.

**Validates: Requirements 4.5, 4.6**

### Property 3: Graceful degradation without jsonschema

*For any* call to validation functions when jsonschema is not installed, the function SHALL return without error and without modifying data.

**Validates: Requirements 4.7, 6.2, 6.3**

### Property 4: Schema file validity

*For any* schema file in `schemas/`, loading and parsing as JSON SHALL succeed and the schema SHALL be valid JSON Schema Draft-07.

**Validates: Requirements 1.1, 2.1, 3.1**

## Error Handling

| Condition | Error Code | Error Class | Recovery |
|-----------|------------|-------------|----------|
| Invalid defaults.json data | VE203 | DataCorruptedError | Restore from backup |
| Invalid offers.json data | VE203 | DataCorruptedError | Restore from backup |
| Invalid config.json data | VE401 | InvalidConfigOptionError | Fix config file |
| Schema file not found | VE201 | VinceFileNotFoundError | Reinstall vince |
| jsonschema not installed | - | (skip validation) | Install jsonschema |

## Testing Strategy

### Unit Tests

- Test each schema file loads as valid JSON
- Test validation passes for valid data matching docs/schemas.md examples
- Test validation fails for invalid data (wrong types, missing required fields, invalid patterns)
- Test graceful handling when jsonschema not installed

### Property-Based Tests

- **Property 1**: Generate valid data, serialize/deserialize, verify still valid
- **Property 2**: Generate data with constraint violations, verify rejection
- **Property 3**: Mock jsonschema import failure, verify no crash
- **Property 4**: Load each schema file, verify valid JSON Schema

### Test Configuration

- Framework: pytest + hypothesis
- Minimum 100 iterations per property test
- Tag format: **Feature: json-schema-files, Property N: {property_text}**
