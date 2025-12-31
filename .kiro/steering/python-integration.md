# Python Integration Steering Guide

This steering file provides comprehensive context for implementing the complete vince CLI Python application. All specifications, interfaces, and requirements are documented in the `docs/` directory.

## Project Overview

**vince** is a Rich CLI application for setting default applications to file extensions. Built with:
- **Typer** - CLI framework
- **Rich** - Terminal formatting
- **UV** - Package manager
- **JSON** - Data persistence

## Critical Documentation References

All implementation MUST follow these specification documents:

| Document | Purpose | Critical For |
|----------|---------|--------------|
| `#[[file:docs/api.md]]` | Python function signatures, parameters, returns, exceptions | Command implementation |
| `#[[file:docs/schemas.md]]` | JSON schemas for defaults.json, offers.json, config.json | Data persistence |
| `#[[file:docs/errors.md]]` | Error codes VE101-VE501, messages, severity, recovery | Error handling |
| `#[[file:docs/config.md]]` | Configuration options, hierarchy, precedence | Config system |
| `#[[file:docs/states.md]]` | State machines for defaults and offers lifecycle | State management |
| `#[[file:docs/testing.md]]` | Test fixtures, mocks, generators, examples | Testing |
| `#[[file:docs/tables.md]]` | Single Source of Truth for all definitions | Cross-reference |
| `#[[file:docs/overview.md]]` | CLI design, commands, flags, validation rules | Overall design |

## Commands to Implement

7 commands with specific interfaces defined in api.md:

| Command | Function | Purpose |
|---------|----------|---------|
| `slap` | `cmd_slap()` | Set application as default for extension |
| `chop` | `cmd_chop()` | Remove/forget file extension association |
| `set` | `cmd_set()` | Set a default for file extension |
| `forget` | `cmd_forget()` | Forget a default for file extension |
| `offer` | `cmd_offer()` | Create custom shortcut/alias |
| `reject` | `cmd_reject()` | Remove custom offer |
| `list` | `cmd_list()` | Display tracked assets and offers |

## Data Files

Three JSON files with schemas in schemas.md:

| File | Schema | Purpose |
|------|--------|---------|
| `defaults.json` | DefaultEntry[] | Application-extension associations |
| `offers.json` | OfferEntry[] | Custom shortcuts/aliases |
| `config.json` | ConfigOptions | User configuration |

### DefaultEntry Fields
- `id`: Unique identifier
- `extension`: File extension (`.md`, `.py`, etc.)
- `application_path`: Absolute path to executable
- `state`: `pending` | `active` | `removed`
- `created_at`: ISO 8601 timestamp

### OfferEntry Fields
- `offer_id`: Pattern `^[a-z][a-z0-9_-]{0,31}$`
- `default_id`: Reference to default entry
- `state`: `created` | `active` | `rejected`
- `auto_created`: Boolean (true if from `slap -set`)
- `created_at`: ISO 8601 timestamp

### Config Options
- `data_dir`: Default `~/.vince`
- `verbose`: Default `false`
- `color_theme`: `default` | `dark` | `light`
- `backup_enabled`: Default `true`
- `max_backups`: Default `5` (0-100)
- `confirm_destructive`: Default `true`

## Error Codes

All errors follow format `VE{category}{number}`:

| Range | Category | Examples |
|-------|----------|----------|
| VE1xx | Input | VE101 (invalid path), VE102 (invalid extension), VE103 (invalid offer_id) |
| VE2xx | File | VE201 (file not found), VE202 (permission denied), VE203 (corrupted) |
| VE3xx | State | VE301 (default exists), VE302 (no default), VE303 (offer exists) |
| VE4xx | Config | VE401 (invalid option), VE402 (malformed config) |
| VE5xx | System | VE501 (unexpected error) |

## State Machines

### Default Lifecycle
```
none → pending (slap without -set)
none → active (slap -set / set)
pending → active (slap -set / set)
pending → none (chop / forget)
active → removed (chop / forget)
removed → active (slap -set / set)
```

### Offer Lifecycle
```
none → created (offer / auto-create from slap -set)
created → active (first use)
created → rejected (reject)
active → rejected (reject)
```

## Validation Rules

### Path Validation
- Must exist: `Path.exists()` → VE101
- Must be file: `Path.is_file()` → VE101
- Must be executable: `os.access(path, os.X_OK)` → VE202

### Extension Validation
- Pattern: `^\.[a-z0-9]+$` → VE102
- Must be in supported list → VE102

### Offer ID Validation
- Pattern: `^[a-z][a-z0-9_-]{0,31}$` → VE103
- Must be unique → VE303
- Reserved names: `help`, `version`, `list`, `all`, `none`, `default` → VE103

## Persistence Layer

### Atomic Write Pattern
```python
def atomic_write(path: Path, data: dict) -> None:
    temp_path = path.with_suffix('.tmp')
    try:
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
        temp_path.rename(path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
```

### Backup Strategy
- Before each write, copy to `{filename}.{timestamp}.bak`
- Retain up to `max_backups` files
- Delete oldest when limit exceeded

## Rich Theme

```python
VINCE_THEME = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "command": "magenta",
    "path": "blue underline",
    "extension": "cyan bold",
})
```

### Message Formats
- Success: `[success]✓[/] {message}`
- Warning: `[warning]⚠[/] {message}`
- Error: `[error]✗[/] {code}: {message}`
- Info: `[info]ℹ[/] {message}`

## Supported Extensions

12 file types with flags:

| Extension | Flag | Alias |
|-----------|------|-------|
| `.md` | `--md` | `--markdown` |
| `.py` | `--py` | `--python` |
| `.txt` | `--txt` | `--text` |
| `.js` | `--js` | `--javascript` |
| `.html` | `--html` | - |
| `.css` | `--css` | - |
| `.json` | `--json` | - |
| `.yml` | `--yml` | `--yaml` |
| `.yaml` | `--yaml` | - |
| `.xml` | `--xml` | - |
| `.csv` | `--csv` | - |
| `.sql` | `--sql` | - |

## Flag Categories

### Utility Flags
- `-h`/`--help`, `-v`/`--version`, `-vb`/`--verbose`, `-db`/`--debug`, `-tr`/`--trace`

### QOL Flags (mirror commands)
- `-set`, `-forget`, `-slap`, `-chop`, `-offer`, `-reject`

### List Flags
- `-app`, `-cmd`, `-ext`, `-def`, `-off`, `-all`

## Testing Requirements

- **Framework**: pytest + Hypothesis
- **Property tests**: Minimum 100 iterations
- **Coverage targets**: Commands 90%, Persistence 95%, Validation 95%, State Machine 100%

## Project Structure (Recommended)

```
vince/
├── __init__.py
├── main.py              # Typer app entry point
├── commands/
│   ├── __init__.py
│   ├── slap.py
│   ├── chop.py
│   ├── set.py
│   ├── forget.py
│   ├── offer.py
│   ├── reject.py
│   └── list.py
├── persistence/
│   ├── __init__.py
│   ├── defaults.py
│   ├── offers.py
│   └── config.py
├── validation/
│   ├── __init__.py
│   ├── path.py
│   ├── extension.py
│   └── offer_id.py
├── state/
│   ├── __init__.py
│   ├── default_state.py
│   └── offer_state.py
├── output/
│   ├── __init__.py
│   ├── theme.py
│   ├── messages.py
│   └── tables.py
└── errors.py
```

## Implementation Checklist

1. [ ] Set up project with pyproject.toml and UV
2. [ ] Implement error classes (VE101-VE501)
3. [ ] Implement validation functions (path, extension, offer_id)
4. [ ] Implement persistence layer (atomic write, backup, file locking)
5. [ ] Implement state machines (default lifecycle, offer lifecycle)
6. [ ] Implement Rich theme and output formatting
7. [ ] Implement commands (slap, chop, set, forget, offer, reject, list)
8. [ ] Implement config system (hierarchy, precedence, validation)
9. [ ] Write property-based tests with Hypothesis
10. [ ] Write integration tests for command flows
11. [ ] Achieve coverage targets

## Key Design Principles

1. **[PD01] Modular Design**: Commands are space-separated, not underscore-joined
2. **Atomic Operations**: All file writes use temp file + rename pattern
3. **State Validation**: All state transitions are validated before execution
4. **Error Recovery**: Every error has a recovery action documented
5. **Rich Output**: Consistent theming across all output types

## Cross-Reference System

Use the ID system from `#[[file:.kiro/steering/id-system.md]]`:
- `id`: Full identifier for documentation
- `sid`: Short identifier for tables/references
- `rid`: Rule ID format `{sid}{num}` (e.g., `sl01`, `VE101`)
