# Data Model Schemas

This document provides formal JSON schema definitions for all persistent data structures used by the vince CLI. These schemas serve as the definitive reference for implementing consistent data handling, validation, and storage.

> [!NOTE]
> For definition tables and the Single Source of Truth, see [tables.md](tables.md).

## Overview

The vince CLI persists data in JSON files stored within the data directory. Each file follows a strict schema that defines required fields, optional fields, types, and validation constraints.

### Schema Conventions

| Convention | Description |
| --- | --- |
| JSON Schema | All schemas use [JSON Schema Draft-07](https://json-schema.org/draft-07/schema) |
| Versioning | Each file includes a `version` field for schema migration |
| Timestamps | All timestamps use ISO 8601 format (`date-time`) |
| Identifiers | IDs follow specific patterns for validation |

### Data Files Summary

| File | Purpose | Location |
| --- | --- | --- |
| `defaults.json` | Default application associations | `{data_dir}/defaults.json` |
| `offers.json` | Custom shortcut/alias definitions | `{data_dir}/offers.json` |
| `config.json` | User configuration options | `{data_dir}/config.json` |

## Defaults Schema

The defaults schema defines the structure for storing application-to-extension associations.

### JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://vince.cli/schemas/defaults.json",
  "title": "Vince Defaults",
  "description": "Schema for storing default application associations",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Schema version in semver format"
    },
    "defaults": {
      "type": "array",
      "description": "Array of default entries",
      "items": {
        "$ref": "#/definitions/DefaultEntry"
      }
    }
  },
  "required": ["version", "defaults"],
  "additionalProperties": false,
  "definitions": {
    "DefaultEntry": {
      "type": "object",
      "description": "A single default application association",
      "properties": {
        "id": {
          "type": "string",
          "minLength": 1,
          "maxLength": 64,
          "description": "Unique identifier for this default entry"
        },
        "extension": {
          "type": "string",
          "pattern": "^\\.[a-z0-9]+$",
          "description": "File extension including leading dot (e.g., .md, .py)"
        },
        "application_path": {
          "type": "string",
          "minLength": 1,
          "description": "Absolute path to the application executable"
        },
        "application_name": {
          "type": "string",
          "minLength": 1,
          "description": "Human-readable application name"
        },
        "state": {
          "type": "string",
          "enum": ["pending", "active", "removed"],
          "description": "Current lifecycle state of the default"
        },
        "os_synced": {
          "type": "boolean",
          "default": false,
          "description": "Whether OS has been configured with this default"
        },
        "os_synced_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp of last successful OS sync"
        },
        "previous_os_default": {
          "type": "string",
          "description": "Previous OS default before vince changed it"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when entry was created"
        },
        "updated_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when entry was last updated"
        }
      },
      "required": ["id", "extension", "application_path", "state", "created_at"],
      "additionalProperties": false
    }
  }
}
```

### DefaultEntry Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | Yes | Unique identifier (1-64 chars) |
| `extension` | string | Yes | File extension with dot (pattern: `^\.[a-z0-9]+$`) |
| `application_path` | string | Yes | Absolute path to executable |
| `application_name` | string | No | Human-readable app name |
| `state` | enum | Yes | One of: `pending`, `active`, `removed` |
| `os_synced` | boolean | No | Whether OS has been configured with this default |
| `os_synced_at` | date-time | No | Timestamp of last successful OS sync |
| `previous_os_default` | string | No | Previous OS default before vince changed it |
| `created_at` | date-time | Yes | Creation timestamp |
| `updated_at` | date-time | No | Last update timestamp |

### Validation Constraints

| Constraint | Field | Rule |
| --- | --- | --- |
| Pattern | `version` | Must match semver: `^\d+\.\d+\.\d+$` |
| Pattern | `extension` | Must match: `^\.[a-z0-9]+$` |
| Enum | `state` | Must be one of: `pending`, `active`, `removed` |
| Length | `id` | 1-64 characters |
| Format | `created_at` | ISO 8601 date-time |
| Format | `updated_at` | ISO 8601 date-time |

### Example defaults.json

```json
{
  "version": "1.0.0",
  "defaults": [
    {
      "id": "def-md-vscode-001",
      "extension": ".md",
      "application_path": "/usr/bin/code",
      "application_name": "Visual Studio Code",
      "state": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "def-py-pycharm-002",
      "extension": ".py",
      "application_path": "/opt/pycharm/bin/pycharm.sh",
      "application_name": "PyCharm",
      "state": "pending",
      "created_at": "2024-01-16T14:20:00Z"
    },
    {
      "id": "def-json-vscode-003",
      "extension": ".json",
      "application_path": "/usr/bin/code",
      "application_name": "Visual Studio Code",
      "state": "removed",
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-17T09:15:00Z"
    }
  ]
}
```

## Offers Schema

The offers schema defines the structure for storing custom shortcuts/aliases that reference defaults.

### JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://vince.cli/schemas/offers.json",
  "title": "Vince Offers",
  "description": "Schema for storing custom shortcut/alias definitions",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Schema version in semver format"
    },
    "offers": {
      "type": "array",
      "description": "Array of offer entries",
      "items": {
        "$ref": "#/definitions/OfferEntry"
      }
    }
  },
  "required": ["version", "offers"],
  "additionalProperties": false,
  "definitions": {
    "OfferEntry": {
      "type": "object",
      "description": "A single offer/alias definition",
      "properties": {
        "offer_id": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_-]{0,31}$",
          "description": "Unique offer identifier (lowercase, alphanumeric, hyphens, underscores)"
        },
        "default_id": {
          "type": "string",
          "minLength": 1,
          "description": "Reference to the associated default entry ID"
        },
        "state": {
          "type": "string",
          "enum": ["created", "active", "rejected"],
          "description": "Current lifecycle state of the offer"
        },
        "auto_created": {
          "type": "boolean",
          "default": false,
          "description": "Whether this offer was auto-created by slap -set"
        },
        "description": {
          "type": "string",
          "maxLength": 256,
          "description": "Optional human-readable description"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when entry was created"
        },
        "used_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when offer was last used"
        }
      },
      "required": ["offer_id", "default_id", "state", "created_at"],
      "additionalProperties": false
    }
  }
}
```

### OfferEntry Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `offer_id` | string | Yes | Unique identifier (pattern: `^[a-z][a-z0-9_-]{0,31}$`) |
| `default_id` | string | Yes | Reference to associated default entry |
| `state` | enum | Yes | One of: `created`, `active`, `rejected` |
| `auto_created` | boolean | No | `true` if auto-created by `slap -set` |
| `description` | string | No | Human-readable description (max 256 chars) |
| `created_at` | date-time | Yes | Creation timestamp |
| `used_at` | date-time | No | Last usage timestamp |

### Validation Constraints

| Constraint | Field | Rule |
| --- | --- | --- |
| Pattern | `version` | Must match semver: `^\d+\.\d+\.\d+$` |
| Pattern | `offer_id` | Must match: `^[a-z][a-z0-9_-]{0,31}$` |
| Enum | `state` | Must be one of: `created`, `active`, `rejected` |
| Length | `offer_id` | 1-32 characters, starts with lowercase letter |
| Length | `description` | Maximum 256 characters |
| Format | `created_at` | ISO 8601 date-time |
| Format | `used_at` | ISO 8601 date-time |

### Reserved Offer Names

The following offer IDs are reserved and cannot be used:

- `help`
- `version`
- `list`
- `all`
- `none`
- `default`

### Example offers.json

```json
{
  "version": "1.0.0",
  "offers": [
    {
      "offer_id": "code-md",
      "default_id": "def-md-vscode-001",
      "state": "active",
      "auto_created": true,
      "description": "VS Code for Markdown files",
      "created_at": "2024-01-15T10:30:00Z",
      "used_at": "2024-01-18T16:45:00Z"
    },
    {
      "offer_id": "pycharm-py",
      "default_id": "def-py-pycharm-002",
      "state": "created",
      "auto_created": false,
      "description": "PyCharm for Python development",
      "created_at": "2024-01-16T14:25:00Z"
    },
    {
      "offer_id": "old-json-editor",
      "default_id": "def-json-vscode-003",
      "state": "rejected",
      "auto_created": false,
      "created_at": "2024-01-10T08:05:00Z"
    }
  ]
}
```

## Config Schema

The config schema defines the structure for user configuration options.

### JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://vince.cli/schemas/config.json",
  "title": "Vince Configuration",
  "description": "Schema for user configuration options",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Schema version in semver format"
    },
    "data_dir": {
      "type": "string",
      "default": "~/.vince",
      "description": "Data storage directory path"
    },
    "verbose": {
      "type": "boolean",
      "default": false,
      "description": "Enable verbose output by default"
    },
    "color_theme": {
      "type": "string",
      "enum": ["default", "dark", "light"],
      "default": "default",
      "description": "Console color theme"
    },
    "backup_enabled": {
      "type": "boolean",
      "default": true,
      "description": "Enable automatic backups before writes"
    },
    "max_backups": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "default": 5,
      "description": "Maximum number of backup files to retain"
    },
    "confirm_destructive": {
      "type": "boolean",
      "default": true,
      "description": "Require confirmation for destructive operations"
    }
  },
  "required": ["version"],
  "additionalProperties": false
}
```

### Config Options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `version` | string | Required | Schema version in semver format |
| `data_dir` | string | `~/.vince` | Data storage directory path |
| `verbose` | boolean | `false` | Enable verbose output by default |
| `color_theme` | enum | `default` | Console theme: `default`, `dark`, `light` |
| `backup_enabled` | boolean | `true` | Enable automatic backups |
| `max_backups` | integer | `5` | Max backup files (0-100) |
| `confirm_destructive` | boolean | `true` | Require confirmation for destructive ops |

### Validation Constraints

| Constraint | Field | Rule |
| --- | --- | --- |
| Pattern | `version` | Must match semver: `^\d+\.\d+\.\d+$` |
| Enum | `color_theme` | Must be one of: `default`, `dark`, `light` |
| Range | `max_backups` | Integer between 0 and 100 |

### Example config.json

#### Minimal Configuration

```json
{
  "version": "1.0.0"
}
```

#### Full Configuration

```json
{
  "version": "1.0.0",
  "data_dir": "~/.vince",
  "verbose": false,
  "color_theme": "default",
  "backup_enabled": true,
  "max_backups": 5,
  "confirm_destructive": true
}
```

#### Custom Configuration

```json
{
  "version": "1.0.0",
  "data_dir": "~/my-vince-data",
  "verbose": true,
  "color_theme": "dark",
  "backup_enabled": true,
  "max_backups": 10,
  "confirm_destructive": false
}
```

## File Locations

### Data Directory Structure

The vince CLI stores all persistent data within a configurable data directory:

```text
{data_dir}/
├── defaults.json      # Default application associations
├── offers.json        # Custom shortcut/alias definitions
├── config.json        # User configuration (user-level)
└── backups/           # Backup files directory
    ├── defaults.2024-01-15T10-30-00Z.bak
    ├── defaults.2024-01-16T14-20-00Z.bak
    ├── offers.2024-01-15T10-30-00Z.bak
    └── ...
```

### Default Locations

| Location Type | Path | Purpose |
| --- | --- | --- |
| Default data_dir | `~/.vince` | Default data storage location |
| User config | `~/.vince/config.json` | User-level configuration |
| Project config | `./.vince/config.json` | Project-level configuration |
| Backups | `{data_dir}/backups/` | Backup file storage |

### File Naming Conventions

| File Type | Pattern | Example |
| --- | --- | --- |
| Data files | `{name}.json` | `defaults.json` |
| Backup files | `{name}.{timestamp}.bak` | `defaults.2024-01-15T10-30-00Z.bak` |
| Temp files | `{name}.tmp` | `defaults.tmp` |

### Backup File Naming

Backup files follow a strict naming convention for easy identification and cleanup:

```text
{original_name}.{ISO8601_timestamp}.bak
```

Where:
- `{original_name}` is the base filename without extension (e.g., `defaults`)
- `{ISO8601_timestamp}` is the backup creation time with colons replaced by hyphens for filesystem compatibility
- `.bak` is the backup extension

Examples:
- `defaults.2024-01-15T10-30-00Z.bak`
- `offers.2024-01-16T14-20-00Z.bak`
- `config.2024-01-17T09-15-00Z.bak`

### Path Resolution

| Input | Resolution |
| --- | --- |
| `~/.vince` | Expands to user home directory |
| `./vince` | Relative to current working directory |
| `/absolute/path` | Used as-is |

### File Permissions

| File Type | Recommended Mode | Description |
| --- | --- | --- |
| Data files | `0600` | Read/write for owner only |
| Backup files | `0600` | Read/write for owner only |
| Data directory | `0700` | Full access for owner only |


## Cross-References

This document relates to other vince CLI documentation:

| Document | Relationship |
| --- | --- |
| [states.md](states.md) | State enum values for `DefaultEntry.state` and `OfferEntry.state` fields |
| [config.md](config.md) | Configuration options including `data_dir` location |
| [tables.md](tables.md) | Single Source of Truth for all definitions |
| [api.md](api.md) | Command interfaces that create and modify schema entries |
| [errors.md](errors.md) | Error codes for schema validation failures |
