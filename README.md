# vince

A Rich CLI for setting default applications to file extensions.

## Installation

```bash
# With uv (recommended)
uv pip install vince

# With pip
pip install vince
```

### Optional Dependencies

Vince includes optional dependencies for enhanced functionality:

```bash
# Install with development/validation dependencies (includes jsonschema)
pip install vince[dev]

# Or install jsonschema separately for schema validation
pip install jsonschema>=4.0.0
```

**Schema Validation**: When `jsonschema` is installed, vince validates data files (`defaults.json`, `offers.json`, `config.json`) against their JSON schemas on load. This catches corrupted or invalid data early. If `jsonschema` is not installed, validation is silently skipped and vince operates normally.

## Quick Start

```bash
# Set VS Code as default for .md files (pending state)
vince slap /path/to/code --md

# Set VS Code as default immediately (active state + creates offer)
vince slap /path/to/code --md -set

# Preview what would happen without making changes
vince slap /path/to/code --md -set -dry

# List all defaults
vince list -def

# List all offers
vince list -off

# Sync all active defaults to OS
vince sync
```

## Commands

| Command | Description |
|---------|-------------|
| `slap` | Set application as default for extension |
| `chop` | Remove file extension association |
| `set` | Set a default for file extension (direct) |
| `forget` | Forget a default for file extension |
| `offer` | Create custom shortcut/alias |
| `reject` | Remove custom offer |
| `list` | Display tracked assets and offers |
| `sync` | Sync all defaults to OS |

## Command Reference

### slap

Set an application as the default for a file extension.

```bash
vince slap <path> [extension-flag] [options]
```

**Arguments:**
- `path` - Path to application executable (required)

**Extension Flags:**
- `--md` - Target .md files
- `--py` - Target .py files
- `--txt` - Target .txt files
- `--js` - Target .js files
- `--html` - Target .html files
- `--css` - Target .css files
- `--json` - Target .json files
- `--yml` - Target .yml files
- `--yaml` - Target .yaml files
- `--xml` - Target .xml files
- `--csv` - Target .csv files
- `--sql` - Target .sql files

**Options:**
- `-set` - Set as default immediately (creates active state and auto-creates offer)
- `-dry` - Preview changes without applying them to the OS
- `-vb, --verbose` - Enable verbose output

**Examples:**
```bash
# Create pending default
vince slap /Applications/Code.app/Contents/MacOS/Electron --md

# Set as active default immediately
vince slap /Applications/Code.app/Contents/MacOS/Electron --md -set

# Preview changes
vince slap /Applications/Code.app/Contents/MacOS/Electron --md -set -dry
```

### chop

Remove or forget a file extension association.

```bash
vince chop [extension-flag] [options]
```

**Options:**
- `-forget` - Forget the default (transition to removed state)
- `-dry` - Preview changes without applying them
- `-vb, --verbose` - Enable verbose output

**Examples:**
```bash
# Show current default info
vince chop --md

# Remove the default
vince chop --md -forget
```

### set

Set a default for a file extension directly.

```bash
vince set <path> [extension-flag] [options]
```

**Arguments:**
- `path` - Path to application executable (required)

**Options:**
- `-dry` - Preview changes without applying them
- `-vb, --verbose` - Enable verbose output

**Examples:**
```bash
vince set /Applications/Code.app/Contents/MacOS/Electron --md
```

### forget

Forget a default for a file extension.

```bash
vince forget [extension-flag] [options]
```

**Options:**
- `-dry` - Preview changes without applying them
- `-vb, --verbose` - Enable verbose output

**Examples:**
```bash
vince forget --md
```

### offer

Create a custom shortcut/alias for a default application.

```bash
vince offer <offer_id> <path> [extension-flag] [options]
```

**Arguments:**
- `offer_id` - Unique identifier (lowercase alphanumeric, hyphens, underscores, max 32 chars)
- `path` - Path to application executable

**Options:**
- `-vb, --verbose` - Enable verbose output

**Examples:**
```bash
vince offer my-editor /Applications/Code.app/Contents/MacOS/Electron --md
```

### reject

Remove a custom offer.

```bash
vince reject <offer_id> [options]
```

**Arguments:**
- `offer_id` - The offer ID to reject

**Options:**
- `-.` - Complete delete (remove offer entirely from data file)
- `-vb, --verbose` - Enable verbose output

**Examples:**
```bash
# Reject an offer (mark as rejected)
vince reject my-editor

# Complete delete
vince reject my-editor -.
```

### list

Display tracked assets and offers.

```bash
vince list [subsection-flag] [extension-filter] [options]
```

**Subsection Flags:**
- `-app` - List applications
- `-cmd` - List commands
- `-ext` - List extensions
- `-def` - List defaults
- `-off` - List offers
- `-all` - List all sections

**Extension Filters:**
- `--md`, `--py`, `--txt`, `--js`, `--html`, `--css`, `--json`, `--yml`, `--yaml`, `--xml`, `--csv`, `--sql`

**Options:**
- `-vb, --verbose` - Enable verbose output

**Examples:**
```bash
# List all defaults
vince list -def

# List all offers
vince list -off

# List everything
vince list -all

# Filter defaults by extension
vince list -def --md
```

### sync

Sync all active defaults to the operating system.

```bash
vince sync [options]
```

**Options:**
- `-dry` - Preview changes without applying them
- `-vb, --verbose` - Enable verbose output

**Examples:**
```bash
# Sync all active defaults
vince sync

# Preview what would be synced
vince sync -dry
```

## Supported Extensions

| Extension | Flag | Description |
|-----------|------|-------------|
| `.md` | `--md` | Markdown files |
| `.py` | `--py` | Python files |
| `.txt` | `--txt` | Text files |
| `.js` | `--js` | JavaScript files |
| `.html` | `--html` | HTML files |
| `.css` | `--css` | CSS files |
| `.json` | `--json` | JSON files |
| `.yml` | `--yml` | YAML files |
| `.yaml` | `--yaml` | YAML files |
| `.xml` | `--xml` | XML files |
| `.csv` | `--csv` | CSV files |
| `.sql` | `--sql` | SQL files |

## OS Integration

Vince can set file associations at the OS level:

| Platform | Status | Requirements |
|----------|--------|--------------|
| macOS | ✓ Supported | `duti` (brew install duti) or PyObjC |
| Windows | ✓ Supported | Built-in (winreg) |
| Linux | ✗ Not Supported | - |

When OS integration is available, commands like `slap -set`, `set`, `chop -forget`, and `forget` will automatically apply changes to the OS. If OS integration fails, vince warns you and suggests running `sync` to retry.

## State Machine

### Default States

| State | Description |
|-------|-------------|
| `none` | No default exists |
| `pending` | Default identified but not active |
| `active` | Default is active |
| `removed` | Default was removed |

### Transitions

```
none → pending (slap without -set)
none → active (slap -set / set)
pending → active (slap -set / set)
pending → none (chop / forget)
active → removed (chop -forget / forget)
removed → active (slap -set / set)
```

## Error Codes

| Code | Description |
|------|-------------|
| VE101 | Invalid path |
| VE102 | Invalid extension |
| VE103 | Invalid offer_id |
| VE104 | Offer not found |
| VE105 | Invalid list subsection |
| VE201 | File not found |
| VE202 | Permission denied |
| VE203 | Data file corrupted |
| VE301 | Default already exists |
| VE302 | No default set |
| VE303 | Offer already exists |
| VE304 | Offer in use |
| VE401 | Invalid config option |
| VE402 | Config malformed |
| VE501 | Unexpected error |
| VE601 | Unsupported platform |
| VE602 | Bundle ID not found (macOS) |
| VE603 | Registry access error (Windows) |
| VE604 | Application not found |
| VE605 | OS operation failed |
| VE606 | Sync partial failure |

## Documentation

- [Overview](docs/overview.md) - Full CLI documentation
- [API](docs/api.md) - Python interface documentation
- [Examples](docs/examples.md) - Usage examples
- [Errors](docs/errors.md) - Error codes and recovery
- [Config](docs/config.md) - Configuration options
- [Schemas](docs/schemas.md) - JSON schema definitions
- [States](docs/states.md) - State machine documentation
- [Tables](docs/tables.md) - Definition tables

## Development

```bash
# Clone and install
git clone https://github.com/deadcoast/vince.git
cd vince
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=vince

# Type check
uv run mypy vince/
```

## License

MIT
