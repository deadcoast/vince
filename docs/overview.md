# vince - A Rich CLI Application

## Overview

Vince is a simple, sophisticated CLI created with elevated visual ASCII UI delivery to quickly set default applications to file extensions. Its quick, intuitive and visually friendly design sets the new standard for user quality of life and visual CLI UI design.

This document provides comprehensive documentation of the vince CLI including:
- Framework and technology stack
- ID system conventions
- CLI commands, flags, and operators
- Persistence layer architecture
- Validation rules and patterns
- Output formatting with Rich

— *Inspired by Infomercials of the Millennials Age*

> [!NOTE]
> **[PD01] Modular Design Principle**: All vince CLI commands, flags, arguments and options are independent and modular. Commands work interdependently with each other in the CLI. This means space-separated syntax, not underscore-joined subcommands.
>
> **Bad Practice**: `vince sub_command --flag`
>
> **Correct Practice**: `vince sub command --flag`

## Framework

### Python Design

The vince CLI is built on the following technologies:

- [Python](https://www.python.org/) - Core language
  - CLI Framework:
    - [Typer](https://typer.tiangolo.com/) - Command-line interface
    - [Rich](https://rich.readthedocs.io/) - Terminal formatting
  - Package Manager: [UV](https://docs.astral.sh/uv/)
  - Data Format: [JSON](https://www.json.org/)

### Documentation Design

All vince documentation follows a modular, regimented format. The docs define the grammar for the CLI, document tagging, acronyms and functionality in consistent spaces. This ensures that naming conventions are consistent and recognizable as per spec across the framework.

> [!NOTE]
> For complete definition tables and the Single Source of Truth, see [tables.md](tables.md).

## ID System

The identification system uses a three-tier naming convention that mirrors the familiar CLI flag pattern of `-h`/`--help`:

| CLI Pattern | ID System | Purpose |
| --- | --- | --- |
| `-h` | `sid` | Short form, quick to type/reference |
| `--help` | `id` | Long form, self-documenting |

This design makes the documentation system intuitive for CLI users who already understand the short/long duality:

- **CLI flags**: `-h` and `--help` are interchangeable at runtime
- **ID system**: `sid` is for internal references/tables, `id` is the canonical human-readable name

### Identification Types

| Type | Description | Example |
| --- | --- | --- |
| `id` | Main identification of an object (full name) | `application` |
| `sid` | Short identification (2-4 letter abbreviation) | `app` |
| `rid` | Rule ID tag combining sid prefix with number | `app01` |
| `num` | Numerical identification variable | `01` |

> [!NOTE]
> [UID01] `id` and `sid` may use brackets or backticks depending on contextual usage throughout the document.

### SID Naming Rules

- **One-word identifiers**: Use first two letters of the id (e.g., `step` → `st`)
- **Two-word identifiers**: Use first two letters of each word (e.g., `short_id` → `sid`)
- **Collision handling**: If an sid is already in use, use subsequent letters in sequence
- **Priority**: `short_id` > `long_id` > `id`

### RID Format

Rule IDs combine the `sid` with a zero-padded number:

- Format: `{sid}{num}` (e.g., `PD01`, `sl01`, `app01`)
- If collision occurs, use subsequent letters from the sid

> [!NOTE]
> For complete id/sid/rid listings, see the DEFINITIONS table in [tables.md](tables.md).

## CLI Commands

The vince CLI provides 7 commands for managing file extension defaults:

| Command | SID | Description |
| --- | --- | --- |
| `slap` | sl | Set application as default for extension |
| `chop` | ch | Remove/forget a file extension association |
| `set` | se | Set a default for a file extension |
| `forget` | fo | Forget a default for a file extension |
| `offer` | of | Create a custom shortcut/alias |
| `reject` | re | Remove a custom offer |
| `list` | li | Display tracked assets and offers |

> [!NOTE]
> For complete command definitions including rid values, see the COMMANDS table in [tables.md](tables.md).

### Command: slap

Set an application as the default for a file extension.

```sh
# STEP1: Identify an application path to set as default
vince slap <path/to/application/app.exe>

# STEP2: Set S1 as extension
vince slap <path/to/application/app.exe> --md

# STEP3: Set S1 as default for extension
vince slap <path/to/application/app.exe> -set --md
```

> [!NOTE]
> When using `slap` with `-set`, an offer is automatically created for the application-extension pairing.

### Command: chop

Remove or forget a file extension association.

```sh
# Remove an application as a default
vince chop <path/to/application/app.exe> -forget --md

# Use `.` operator to remove default without specifying path
vince chop . -forget --md
```

### Command: set

Set a default for a file extension (used as flag with other commands).

```sh
vince slap <path/to/application/app.exe> -set --md
```

### Command: forget

Forget a default for a file extension (used as flag with other commands).

```sh
vince chop <path/to/application/app.exe> -forget --md
```

### Command: offer

Create a custom shortcut/alias for a file extension default.

```sh
# Create an offer with application path, offer_id, and target extension
vince offer <path/to/application/app.exe> <offer_id> --md
```

### Command: reject

Remove a custom offer.

```sh
# Remove a specific offer
vince reject <path/to/application/app.exe> <offer_id> --md

# Complete-Delete: remove offer, its id, and all connections using `.` operator
vince reject <offer_id> .
```

### Command: list

Display tracked assets and offers.

```sh
# List all tracked applications
vince list -app

# List all available commands
vince list -cmd

# List all tracked extensions
vince list -ext

# List all set defaults
vince list -def

# List all custom offers
vince list -off

# List all subsections
vince list -all
```

## OS Integration

The vince CLI provides cross-platform OS integration to actually set file associations at the operating system level. This means when you set a default with vince, it configures your OS so that double-clicking a file opens it in your chosen application.

### Platform Support

| Platform | Status | Implementation |
| --- | --- | --- |
| macOS | ✓ Supported | Launch Services via duti or PyObjC |
| Windows | ✓ Supported | Windows Registry (winreg) |
| Linux | ✗ Not Supported | Future consideration |

> [!NOTE]
> On unsupported platforms, vince will raise error VE601. The JSON tracking still works, but OS-level changes are not applied.

### macOS Integration

On macOS, vince uses the Launch Services framework to set file associations:

- **Primary method**: `duti` command-line tool (recommended, install via `brew install duti`)
- **Fallback method**: PyObjC Launch Services bindings

**UTI Mapping**: macOS uses Uniform Type Identifiers (UTIs) instead of file extensions. Vince automatically maps extensions to their corresponding UTIs:

| Extension | UTI |
| --- | --- |
| `.md` | `net.daringfireball.markdown` |
| `.py` | `public.python-script` |
| `.txt` | `public.plain-text` |
| `.js` | `com.netscape.javascript-source` |
| `.html` | `public.html` |
| `.css` | `public.css` |
| `.json` | `public.json` |
| `.yml`/`.yaml` | `public.yaml` |
| `.xml` | `public.xml` |
| `.csv` | `public.comma-separated-values-text` |
| `.sql` | `public.sql` |

### Windows Integration

On Windows, vince modifies the Windows Registry to set file associations:

- Creates ProgID entries in `HKEY_CURRENT_USER\Software\Classes`
- Associates extensions with the ProgID
- Notifies the shell of changes via `SHChangeNotify`

> [!NOTE]
> Windows file associations are set at the user level (HKEY_CURRENT_USER), so administrator privileges are not typically required.

### Command: sync

Sync all active defaults to the operating system at once.

```sh
# Sync all active defaults to the OS
vince sync

# Preview changes without applying them
vince sync -dry

# Sync with verbose output
vince sync -vb
```

The `sync` command:
1. Loads all active defaults from the JSON store
2. Checks if each OS default matches the vince configuration
3. Skips entries that are already correctly configured
4. Applies changes for out-of-sync entries
5. Reports success/failure for each extension

### Dry Run Mode

All OS-modifying commands support a `-dry` flag to preview changes without applying them:

```sh
# Preview slap changes
vince slap /path/to/app -set --md -dry

# Preview chop changes
vince chop -forget --md -dry

# Preview sync changes
vince sync -dry
```

**Dry run output shows**:
- Extension being modified
- Current OS default
- Proposed new default
- Required OS operations

### OS Error Codes (VE6xx)

OS integration introduces a new category of error codes:

| Code | Name | Description |
| --- | --- | --- |
| VE601 | UnsupportedPlatformError | Platform not supported (not macOS or Windows) |
| VE602 | BundleIdNotFoundError | Cannot determine macOS bundle ID for application |
| VE603 | RegistryAccessError | Windows registry access denied |
| VE604 | ApplicationNotFoundError | Application not found or invalid |
| VE605 | OSOperationError | Generic OS operation failure |
| VE606 | SyncPartialError | Sync completed with some failures |

> [!NOTE]
> For complete error details and recovery actions, see [errors.md](errors.md).

### Automatic OS Integration

When you use commands that modify defaults, vince automatically applies changes to the OS:

| Command | OS Action |
| --- | --- |
| `slap -set` | Sets OS default for extension |
| `set` | Sets OS default for extension |
| `chop -forget` | Removes OS default for extension |
| `forget` | Removes OS default for extension |

If the OS operation fails but the JSON update succeeded, vince will warn you and suggest running `sync` to retry.

### Rollback Support

Vince records the previous OS default before making changes. If an operation fails after partial changes:

1. Vince attempts to rollback to the previous state
2. Rollback attempts are logged
3. If rollback also fails, both errors are reported

## Flags

Flags are organized into four categories: Utility, QOL (Quality of Life), List, and Extension.

### Utility Flags

Control CLI behavior and output.

| Short | Long | Description |
| --- | --- | --- |
| `-h` | `--help` | Display help information |
| `-v` | `--version` | Display version information |
| `-vb` | `--verbose` | Enable verbose output |
| `-db` | `--debug` | Enable debug mode |
| `-tr` | `--trace` | Enable trace logging |

### QOL Flags

Quality-of-life flags that mirror command functionality. These provide shorthand access to command behaviors when used with other commands.

| Short | Description | Mirrors Command |
| --- | --- | --- |
| `-set` | Set a file extension as default | `set` |
| `-forget` | Forget a file extension as default | `forget` |
| `-slap` | Set a file extension as default | `slap` |
| `-chop` | Forget a file extension as default | `chop` |
| `-offer` | Create a custom offer | `offer` |
| `-reject` | Remove a custom offer | `reject` |

> [!NOTE]
> QOL flags mirror their corresponding commands. For example, `-set` provides the same functionality as the `set` command when used as a modifier.

### List Flags

Subsection flags for the `list` command. These provide cheatsheet-style table views.

| Short | Description |
| --- | --- |
| `-app` | List all tracked applications |
| `-cmd` | List all available commands |
| `-ext` | List all tracked extensions |
| `-def` | List all set defaults |
| `-off` | List all custom offers |
| `-all` | List all subsections |

```sh
# Example: List all applications
vince list -app
```

### Extension Flags

Set file type defaults. Extension flags use the `--` prefix (long flag format).

| Flag | Alias | Sets Default For |
| --- | --- | --- |
| `--md` | `--markdown` | Markdown files (.md) |
| `--py` | `--python` | Python files (.py) |
| `--txt` | `--text` | Text files (.txt) |
| `--js` | `--javascript` | JavaScript files (.js) |
| `--html` | `--html` | HTML files (.html) |
| `--css` | `--css` | CSS files (.css) |
| `--json` | `--json` | JSON files (.json) |
| `--yml` | `--yaml` | YAML files (.yml) |
| `--yaml` | `--yaml` | YAML files (.yaml) |
| `--xml` | `--xml` | XML files (.xml) |
| `--csv` | `--csv` | CSV files (.csv) |
| `--sql` | `--sql` | SQL files (.sql) |

> [!NOTE]
> Extension flags use the double-dash (`--`) prefix for both short and long forms. They do not have single-dash short forms like utility flags.

## CLI Operators

Special symbols with contextual meaning in the CLI.

| Symbol | Name | Usage |
| --- | --- | --- |
| `--` | flag_prefix | Prefix for long flags |
| `-` | short_prefix | Prefix for short flags |
| `.` | wildcard | Signifies 'all' or 'any' in context |

> [!NOTE]
> For complete operator definitions, see the OPERATORS table in [tables.md](tables.md).

### The `.` Operator

The `.` (wildcard) operator is used to signify "all" or "any" in the context of a command:

**With `chop`**: Remove default without specifying the application path

```sh
vince chop . -forget --md
```

**With `reject`**: Complete-delete an offer and all its connections

```sh
vince reject <offer_id> .
```

## CLI Arguments

| Pattern | Name | Description |
| --- | --- | --- |
| `<path/to/application/app.exe>` | path | File system path to the application executable |
| `<file_extension>` | file_extension | The file extension to target (e.g., .md, .py) |
| `<offer_id>` | offer | Custom shortcut/alias identifier |

> [!NOTE]
> For complete argument definitions, see the ARGUMENTS table in [tables.md](tables.md).


## Persistence Layer

The vince CLI uses a JSON-based persistence layer for storing defaults, offers, and configuration data. All data files are stored in the user's data directory.

> [!NOTE]
> For complete JSON schema definitions, see [schemas.md](schemas.md).

### File I/O Patterns

The persistence layer follows a consistent pattern for all file operations:

| Operation | Pattern | Description |
| --- | --- | --- |
| Read | Load → Parse → Validate | Load file, parse JSON, validate against schema |
| Write | Validate → Serialize → Atomic Write | Validate data, serialize to JSON, write atomically |
| Update | Read → Modify → Write | Load existing, apply changes, write back |

```python
# Read pattern
def load_data(path: Path) -> dict:
    """Load and validate JSON data from file."""
    with open(path, 'r') as f:
        data = json.load(f)
    validate_schema(data)
    return data
```

### Atomic Write Operations

To prevent data corruption from interrupted writes, all file modifications use atomic write operations:

```python
def atomic_write(path: Path, data: dict) -> None:
    """Write data atomically using temp file + rename."""
    temp_path = path.with_suffix('.tmp')
    try:
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
        temp_path.rename(path)  # Atomic on POSIX systems
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
```

| Step | Action | Purpose |
| --- | --- | --- |
| 1 | Write to `.tmp` file | Isolate write from original |
| 2 | Rename temp to target | Atomic replacement |
| 3 | Cleanup on failure | Remove partial writes |

### Backup Procedures

Before modifying data files, the persistence layer creates timestamped backups:

| Setting | Default | Description |
| --- | --- | --- |
| `backup_enabled` | `true` | Enable automatic backups |
| `max_backups` | `5` | Maximum backup files to retain |

**Backup Naming Convention**: `{filename}.{timestamp}.bak`

```sh
# Example backup files
defaults.json.20240115_143022.bak
defaults.json.20240115_142015.bak
offers.json.20240115_143022.bak
```

**Backup Workflow**:

1. Before write, copy current file to backup directory
2. Apply timestamp to backup filename
3. If backup count exceeds `max_backups`, delete oldest
4. Proceed with atomic write

> [!NOTE]
> For backup configuration options, see [config.md](config.md).


### File Locking

The persistence layer implements file locking to prevent concurrent access issues when multiple vince processes attempt to modify the same data files.

**Locking Strategy**:

| Lock Type | Scope | Duration |
| --- | --- | --- |
| Exclusive | Per-file | Duration of write operation |
| Advisory | Process-level | Released on process exit |

```python
import fcntl
from contextlib import contextmanager

@contextmanager
def file_lock(path: Path):
    """Acquire exclusive lock on file for write operations."""
    lock_path = path.with_suffix('.lock')
    with open(lock_path, 'w') as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
```

**Concurrent Access Prevention**:

| Scenario | Behavior | Error Code |
| --- | --- | --- |
| Lock acquired | Proceed with operation | - |
| Lock unavailable | Wait with timeout | - |
| Lock timeout | Fail with error | VE501 |

> [!NOTE]
> For error code details, see [errors.md](errors.md).


### Data Migration

The persistence layer supports schema versioning and data migration for backward compatibility when the data format changes.

**Schema Versioning**:

Each data file includes a `version` field following semantic versioning:

```json
{
  "version": "1.0.0",
  "defaults": [...]
}
```

| Version Component | Meaning | Migration Required |
| --- | --- | --- |
| Major (X.0.0) | Breaking changes | Yes - manual review |
| Minor (0.X.0) | New fields added | Yes - automatic |
| Patch (0.0.X) | Bug fixes only | No |

**Migration Patterns**:

```python
MIGRATIONS = {
    "1.0.0": migrate_to_1_0_0,
    "1.1.0": migrate_to_1_1_0,
}

def migrate_data(data: dict, target_version: str) -> dict:
    """Apply migrations to bring data to target version."""
    current = data.get("version", "0.0.0")
    for version, migrator in MIGRATIONS.items():
        if compare_versions(current, version) < 0:
            data = migrator(data)
            data["version"] = version
    return data
```

**Migration Workflow**:

1. Load data file
2. Check `version` field against current schema version
3. If older, apply sequential migrations
4. Validate migrated data against current schema
5. Write updated data with new version

> [!NOTE]
> For complete schema definitions, see [schemas.md](schemas.md).


### File Error Handling

The persistence layer handles file operation errors gracefully with specific error codes and recovery procedures.

**Error Handling Matrix**:

| Error Condition | Error Code | Recovery Action |
| --- | --- | --- |
| File not found | VE201 | Create new file with defaults |
| Permission denied | VE202 | Check file/directory permissions |
| Data file corrupted | VE203 | Restore from backup |
| JSON parse error | VE203 | Restore from backup |
| Disk full | VE501 | Free disk space |
| Lock timeout | VE501 | Retry or wait for other process |

**Recovery Procedures**:

```python
def safe_load(path: Path) -> dict:
    """Load data with automatic recovery from backup."""
    try:
        return load_data(path)
    except FileNotFoundError:
        return create_default_data(path)
    except (json.JSONDecodeError, ValidationError):
        backup = find_latest_backup(path)
        if backup:
            return restore_from_backup(backup, path)
        raise DataCorruptedError(f"VE203: Data file corrupted: {path}")
```

**Automatic Recovery**:

| Scenario | Action | User Notification |
| --- | --- | --- |
| Missing file | Create with defaults | Info message |
| Corrupted file + backup exists | Restore from backup | Warning message |
| Corrupted file + no backup | Fail with error | Error message |

> [!NOTE]
> For complete error code definitions, see [errors.md](errors.md).


## Validation Rules

The vince CLI validates all user input before processing commands. Each validation rule has a corresponding error code for consistent error handling.

### Path Validation

Application paths must meet the following criteria:

| Rule | Check | Error Code |
| --- | --- | --- |
| Exists | `Path.exists()` | VE101 |
| Is File | `Path.is_file()` | VE101 |
| Executable | `os.access(path, os.X_OK)` | VE202 |

```python
from pathlib import Path
import os
from vince.errors import InvalidPathError, PermissionDeniedError

def validate_path(path: Path) -> Path:
    """Validate application path exists and is executable."""
    resolved_path = path.resolve()
    
    if not resolved_path.exists():
        raise InvalidPathError(str(resolved_path))  # VE101
    
    if not resolved_path.is_file():
        raise InvalidPathError(str(resolved_path))  # VE101
    
    if not os.access(resolved_path, os.X_OK):
        raise PermissionDeniedError(str(resolved_path))  # VE202
    
    return resolved_path
```

**Path Normalization**:
- Relative paths are converted to absolute paths
- Symlinks are resolved to their target
- Path separators are normalized for the platform

### Extension Validation

File extensions must follow the supported format:

| Rule | Pattern | Error Code |
| --- | --- | --- |
| Format | `^\.[a-z0-9]+$` | VE102 |
| Supported | In SUPPORTED_EXTENSIONS set | VE102 |

```python
import re
from vince.errors import InvalidExtensionError

EXTENSION_PATTERN = re.compile(r'^\.[a-z0-9]+$')

SUPPORTED_EXTENSIONS = {
    ".md", ".py", ".txt", ".js", ".html", ".css",
    ".json", ".yml", ".yaml", ".xml", ".csv", ".sql"
}

def validate_extension(ext: str) -> str:
    """Validate file extension format and support."""
    ext = ext.lower()  # Auto-convert to lowercase
    
    if not EXTENSION_PATTERN.match(ext):
        raise InvalidExtensionError(ext)  # VE102
    
    if ext not in SUPPORTED_EXTENSIONS:
        raise InvalidExtensionError(ext)  # VE102
    
    return ext
```

**Supported Extensions**:

| Extension | Alias | Description |
| --- | --- | --- |
| `.md` | `.markdown` | Markdown files |
| `.py` | `.python` | Python files |
| `.txt` | `.text` | Text files |
| `.js` | `.javascript` | JavaScript files |
| `.html` | - | HTML files |
| `.css` | - | CSS files |
| `.json` | - | JSON files |
| `.yml` | `.yaml` | YAML files |
| `.yaml` | - | YAML files |
| `.xml` | - | XML files |
| `.csv` | - | CSV files |
| `.sql` | - | SQL files |

> [!NOTE]
> For complete extension list, see the FILE_TYPES table in [tables.md](tables.md).

### Offer ID Validation

Offer IDs must follow strict naming rules:

| Rule | Pattern/Check | Error Code |
| --- | --- | --- |
| Format | `^[a-z][a-z0-9_-]{0,31}$` | VE103 |
| Unique | Not in existing offers | VE303 |
| Reserved | Not in RESERVED_NAMES set | VE103 |

```python
import re
from vince.errors import InvalidOfferIdError

OFFER_ID_PATTERN = re.compile(r'^[a-z][a-z0-9_-]{0,31}$')
RESERVED_NAMES = {'help', 'version', 'list', 'all', 'none', 'default'}

def validate_offer_id(offer_id: str) -> str:
    """Validate offer ID format and availability."""
    if not OFFER_ID_PATTERN.match(offer_id):
        raise InvalidOfferIdError(offer_id)  # VE103
    
    if offer_id in RESERVED_NAMES:
        raise InvalidOfferIdError(offer_id)  # VE103
    
    return offer_id
```

**Reserved Offer Names**: `help`, `version`, `list`, `all`, `none`, `default`

### Flag Combination Rules

Certain flag combinations are invalid or have special behavior:

| Combination | Behavior | Error Code |
| --- | --- | --- |
| `-set` + `-forget` | Conflict | VE105 |
| `-slap` + `-chop` | Conflict | VE105 |
| `-vb` + `-db` | Both enabled | - |
| `-db` + `-tr` | Both enabled | - |

```python
CONFLICTING_FLAGS = [
    ('-set', '-forget'),
    ('-slap', '-chop'),
    ('-offer', '-reject'),
]

def validate_flags(flags: List[str]) -> None:
    """Validate flag combinations."""
    for flag_a, flag_b in CONFLICTING_FLAGS:
        if flag_a in flags and flag_b in flags:
            raise ValidationError(f"VE105: Conflicting flags: {flag_a} and {flag_b}")
```

> [!NOTE]
> For complete flag definitions, see the FLAGS table in [tables.md](tables.md).


### Validation Error Messages

Each validation rule has a corresponding error message with Rich console formatting:

| Error Code | Message Template | Category |
| --- | --- | --- |
| VE101 | Invalid path: {path} does not exist | Input |
| VE102 | Invalid extension: {ext} is not supported | Input |
| VE103 | Invalid offer_id: {id} does not match pattern | Input |
| VE104 | Offer not found: {id} does not exist | Input |
| VE105 | Invalid list subsection: {section} | Input |
| VE201 | File not found: {path} | File |
| VE202 | Permission denied: cannot access {path} | File |
| VE203 | Data file corrupted: {file} | File |
| VE301 | Default already exists for {ext} | State |
| VE302 | No default set for {ext} | State |
| VE303 | Offer already exists: {id} | State |
| VE304 | Cannot reject: offer {id} is in use | State |

**Error Message Format**:

```python
from rich.console import Console

console = Console()

def format_error(code: str, message: str) -> None:
    """Format and display validation error."""
    console.print(f"[error]✗ {code}:[/] {message}")
```

**Example Output**:

```text
✗ VE101: Invalid path: /usr/bin/nonexistent does not exist
✗ VE102: Invalid extension: .xyz is not supported
✗ VE103: Invalid offer_id: 123invalid does not match pattern
```

> [!NOTE]
> For complete error catalog with severity levels and recovery actions, see [errors.md](errors.md).


## CLI Output Formatting

The vince CLI uses [Rich](https://rich.readthedocs.io/) for terminal formatting, providing a consistent and visually appealing output experience across all commands.

### Rich Theme

The vince CLI defines a custom Rich theme for consistent styling across all output:

**Color Palette**:

| Style Name | Color | Usage |
| --- | --- | --- |
| `info` | cyan | Informational messages |
| `success` | green | Success confirmations |
| `warning` | yellow | Warning messages |
| `error` | red bold | Error messages |
| `command` | magenta | Command names |
| `path` | blue underline | File paths |
| `extension` | cyan bold | File extensions |
| `offer` | green italic | Offer IDs |
| `state` | yellow | State indicators |
| `header` | white bold | Table headers |

**Theme Configuration**:

```python
from rich.theme import Theme

VINCE_THEME = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "command": "magenta",
    "path": "blue underline",
    "extension": "cyan bold",
    "offer": "green italic",
    "state": "yellow",
    "header": "white bold",
})
```

**Console Initialization**:

```python
from rich.console import Console

console = Console(theme=VINCE_THEME)
```

> [!NOTE]
> The theme can be customized via the `color_theme` configuration option. See [config.md](config.md) for details.


### Table Formatting

The `list` command outputs data in formatted Rich tables with consistent styling:

**Table Styles**:

| Element | Style | Description |
| --- | --- | --- |
| Box | `ROUNDED` | Rounded corner borders |
| Header | `header` style | Bold white headers |
| Columns | Per-type styling | Extension, path, state columns |
| Padding | 1 space | Cell padding |

**Table Configuration**:

```python
from rich.table import Table
from rich import box

def create_list_table(title: str) -> Table:
    """Create a styled table for list output."""
    table = Table(
        title=title,
        box=box.ROUNDED,
        header_style="header",
        padding=(0, 1),
        collapse_padding=True,
    )
    return table
```

**Defaults Table Example**:

```python
table = create_list_table("Defaults")
table.add_column("Extension", style="extension")
table.add_column("Application", style="path")
table.add_column("State", style="state")

# Add rows
table.add_row(".md", "/usr/bin/code", "active")
table.add_row(".py", "/usr/bin/pycharm", "pending")

console.print(table)
```

**Output**:

```text
╭─────────────────────────────────────────────────╮
│                    Defaults                     │
├───────────┬─────────────────────┬───────────────┤
│ Extension │ Application         │ State         │
├───────────┼─────────────────────┼───────────────┤
│ .md       │ /usr/bin/code       │ active        │
│ .py       │ /usr/bin/pycharm    │ pending       │
╰───────────┴─────────────────────┴───────────────╯
```

**Offers Table Example**:

```python
table = create_list_table("Offers")
table.add_column("Offer ID", style="offer")
table.add_column("Extension", style="extension")
table.add_column("State", style="state")

table.add_row("my-editor", ".md", "active")
table.add_row("py-ide", ".py", "created")

console.print(table)
```

> [!NOTE]
> For list command subsection flags, see the FLAGS section above.


### Message Formatting

The vince CLI uses consistent message formats for different output types:

**Message Types**:

| Type | Icon | Style | Usage |
| --- | --- | --- | --- |
| Success | ✓ | `success` | Operation completed successfully |
| Warning | ⚠ | `warning` | Non-fatal issues or advisories |
| Error | ✗ | `error` | Operation failed |
| Info | ℹ | `info` | Informational messages |

**Message Format Functions**:

```python
def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[success]✓[/] {message}")

def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]⚠[/] {message}")

def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[error]✗[/] {message}")

def print_info(message: str) -> None:
    """Print an informational message."""
    console.print(f"[info]ℹ[/] {message}")
```

**Rich Markup Examples**:

```python
# Success message with styled elements
console.print("[success]✓[/] Default set for [extension].md[/] → [path]/usr/bin/code[/]")

# Warning message
console.print("[warning]⚠[/] Default already exists for [extension].py[/]")

# Error message with error code
console.print("[error]✗ VE101:[/] Invalid path: [path]/nonexistent/app[/] does not exist")

# Info message with command reference
console.print("[info]ℹ[/] Use [command]vince list -def[/] to see all defaults")
```

**Example Output**:

```text
✓ Default set for .md → /usr/bin/code
⚠ Default already exists for .py
✗ VE101: Invalid path: /nonexistent/app does not exist
ℹ Use vince list -def to see all defaults
```

> [!NOTE]
> For complete error message catalog, see [errors.md](errors.md).


### Progress Indicators

For long-running operations, the vince CLI provides visual feedback using Rich progress indicators:

**Progress Bar Pattern**:

Used for operations with known completion percentage (e.g., batch processing):

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

def process_with_progress(items: list) -> None:
    """Process items with progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Processing...", total=len(items))
        for item in items:
            process_item(item)
            progress.advance(task)
```

**Progress Bar Output**:

```text
⠋ Processing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  75%
```

**Spinner Pattern**:

Used for operations with unknown duration (e.g., file discovery):

```python
from rich.console import Console
from rich.status import Status

console = Console(theme=VINCE_THEME)

def operation_with_spinner() -> None:
    """Perform operation with spinner indicator."""
    with console.status("[info]Searching for applications...[/]", spinner="dots"):
        # Long-running operation
        result = search_applications()
    console.print("[success]✓[/] Search complete")
```

**Spinner Styles**:

| Spinner | Usage | Visual |
| --- | --- | --- |
| `dots` | Default operations | ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ |
| `line` | File operations | ⎺⎻⎼⎽⎼⎻ |
| `arc` | Network operations | ◜◠◝◞◡◟ |

**Spinner Output**:

```text
⠋ Searching for applications...
✓ Search complete
```

> [!NOTE]
> Progress indicators are only shown when `verbose` mode is enabled or for operations exceeding 1 second.


### Branding

The vince CLI includes ASCII art branding elements for a distinctive visual identity:

**ASCII Art Banner**:

```text
          _                 
   __   _(_)_ __   ___ ___  
   \ \ / / | '_ \ / __/ _ \ 
    \ V /| | | | | (_|  __/ 
     \_/ |_|_| |_|\___\___| 
                            
   Set defaults with style ✨
```

**Banner Implementation**:

```python
VINCE_BANNER = """
[success]          _                 [/]
[success]   __   _(_)_ __   ___ ___  [/]
[success]   \\ \\ / / | '_ \\ / __/ _ \\ [/]
[success]    \\ V /| | | | | (_|  __/ [/]
[success]     \\_/ |_|_| |_|\\___\\___| [/]
[info]                            [/]
[info]   Set defaults with style ✨[/]
"""

def print_banner() -> None:
    """Print the vince ASCII banner."""
    console.print(VINCE_BANNER)
```

**Branding Elements**:

| Element | Usage | Display |
| --- | --- | --- |
| Banner | `--version`, `--help` | Full ASCII art |
| Tagline | Below banner | "Set defaults with style ✨" |
| Version | `--version` | `vince v1.0.0` |
| Emoji | Success messages | ✨ ✓ ⚠ ✗ ℹ |

**Version Display**:

```python
def print_version() -> None:
    """Print version information with branding."""
    print_banner()
    console.print(f"[info]vince[/] [success]v{__version__}[/]")
    console.print(f"[info]Python {sys.version.split()[0]}[/]")
```

**Version Output**:

```text
          _                 
   __   _(_)_ __   ___ ___  
   \ \ / / | '_ \ / __/ _ \ 
    \ V /| | | | | (_|  __/ 
     \_/ |_|_| |_|\___\___| 
                            
   Set defaults with style ✨

vince v1.0.0
Python 3.11.0
```

> [!NOTE]
> The banner is displayed only for `--version` and `--help` commands to avoid cluttering regular output.


### Rich Markup Examples

Complete examples demonstrating Rich markup for each output type in the vince CLI:

**Success Output Example**:

```python
# After successful slap command
console.print("[success]✓[/] Default set for [extension].md[/]")
console.print("  [info]Application:[/] [path]/usr/bin/code[/]")
console.print("  [info]State:[/] [state]active[/]")
```

Output:
```text
✓ Default set for .md
  Application: /usr/bin/code
  State: active
```

**Warning Output Example**:

```python
# When default already exists
console.print("[warning]⚠[/] Default already exists for [extension].py[/]")
console.print("  [info]Current:[/] [path]/usr/bin/pycharm[/]")
console.print("  [info]Use[/] [command]vince chop[/] [info]to remove first[/]")
```

Output:
```text
⚠ Default already exists for .py
  Current: /usr/bin/pycharm
  Use vince chop to remove first
```

**Error Output Example**:

```python
# When path validation fails
console.print("[error]✗ VE101:[/] Invalid path: [path]/nonexistent/app[/] does not exist")
console.print("  [info]Recovery:[/] Verify the application path exists")
```

Output:
```text
✗ VE101: Invalid path: /nonexistent/app does not exist
  Recovery: Verify the application path exists
```

**Info Output Example**:

```python
# Verbose mode information
console.print("[info]ℹ[/] Verbose mode enabled")
console.print("  [info]Data directory:[/] [path]~/.vince[/]")
console.print("  [info]Config file:[/] [path]~/.vince/config.json[/]")
```

Output:
```text
ℹ Verbose mode enabled
  Data directory: ~/.vince
  Config file: ~/.vince/config.json
```

**Table Output Example**:

```python
from rich.table import Table
from rich import box

# List defaults table
table = Table(title="Defaults", box=box.ROUNDED, header_style="header")
table.add_column("Extension", style="extension")
table.add_column("Application", style="path")
table.add_column("State", style="state")

table.add_row(".md", "/usr/bin/code", "active")
table.add_row(".py", "/usr/bin/pycharm", "pending")
table.add_row(".json", "/usr/bin/jq", "active")

console.print(table)
```

Output:
```text
╭─────────────────────────────────────────────────╮
│                    Defaults                     │
├───────────┬─────────────────────┬───────────────┤
│ Extension │ Application         │ State         │
├───────────┼─────────────────────┼───────────────┤
│ .md       │ /usr/bin/code       │ active        │
│ .py       │ /usr/bin/pycharm    │ pending       │
│ .json     │ /usr/bin/jq         │ active        │
╰───────────┴─────────────────────┴───────────────╯
```

**Progress Output Example**:

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Batch operation with progress
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
) as progress:
    task = progress.add_task("[info]Setting defaults...[/]", total=3)
    for ext in [".md", ".py", ".json"]:
        set_default(ext)
        progress.advance(task)

console.print("[success]✓[/] All defaults set successfully")
```

Output:
```text
⠋ Setting defaults... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
✓ All defaults set successfully
```

**Combined Output Example**:

```python
# Complete slap command output with verbose mode
print_banner()
console.print()
console.print("[info]ℹ[/] Processing [command]slap[/] command...")
console.print()

with console.status("[info]Validating path...[/]", spinner="dots"):
    validate_path(path)

console.print("[success]✓[/] Path validated: [path]/usr/bin/code[/]")
console.print("[success]✓[/] Default set for [extension].md[/]")
console.print("[success]✓[/] Offer created: [offer]code-md[/]")
console.print()
console.print("[info]ℹ[/] Use [command]vince list -def[/] to see all defaults")
```

> [!NOTE]
> For error code details and recovery actions, see [errors.md](errors.md).

## Cross-References

This document is part of the vince CLI documentation system. For related information, see:

| Document | Description |
| --- | --- |
| [tables.md](tables.md) | Single Source of Truth for all definitions (commands, errors, states, extensions) |
| [api.md](api.md) | Python function signatures and command interfaces |
| [schemas.md](schemas.md) | JSON schema definitions for data persistence |
| [errors.md](errors.md) | Complete error catalog with codes, messages, and recovery actions |
| [states.md](states.md) | State machine documentation for defaults and offers |
| [config.md](config.md) | Configuration options and hierarchy |
| [examples.md](examples.md) | Usage examples for all commands |
| [testing.md](testing.md) | Testing patterns and fixtures |
| [README.md](README.md) | Documentation entry point and navigation |
