# API Interface Documentation

This document provides complete Python interface specifications for all vince CLI commands. It serves as the definitive reference for implementing the CLI with clear contracts, type hints, and behavioral documentation.

> [!NOTE]
> For definition tables and the Single Source of Truth, see [tables.md](tables.md).

## Overview

The vince CLI is built using [Typer](https://typer.tiangolo.com/) for command-line interface handling and [Rich](https://rich.readthedocs.io/) for terminal formatting. Each command is implemented as a decorated function with full type annotations.

### Interface Conventions

| Convention | Description |
| --- | --- |
| Type Hints | All parameters and return types use Python type annotations |
| Optional | Parameters with defaults use `Optional[T]` or union syntax |
| Exceptions | All raised exceptions are documented with error codes |
| Return | Commands return `None`; output is via Rich console |

## Command Registry

The command registry pattern establishes how commands are registered and organized within the Typer application.

### Typer App Initialization

```python
from typer import Typer, Option, Argument
from typing import Optional
from pathlib import Path

app = Typer(
    name="vince",
    help="A Rich CLI for setting default applications to file extensions.",
    add_completion=False,
    rich_markup_mode="rich",
)
```

### @app.command() Decorator Usage

Each command is registered using the `@app.command()` decorator:

```python
@app.command()
def slap(
    path: Path = Argument(..., help="Path to application executable"),
    md: bool = Option(False, "--md", help="Target .md files"),
    set_default: bool = Option(False, "-set", help="Set as default"),
    verbose: bool = Option(False, "-vb", "--verbose", help="Verbose output"),
) -> None:
    """Set an application as the default for a file extension."""
    ...
```

### Registry Pattern

```python
from typer import Typer

# Main application instance
app = Typer(name="vince")

# Command registration
@app.command(name="slap")
def cmd_slap(...) -> None: ...

@app.command(name="chop")
def cmd_chop(...) -> None: ...

@app.command(name="set")
def cmd_set(...) -> None: ...

@app.command(name="forget")
def cmd_forget(...) -> None: ...

@app.command(name="offer")
def cmd_offer(...) -> None: ...

@app.command(name="reject")
def cmd_reject(...) -> None: ...

@app.command(name="list")
def cmd_list(...) -> None: ...

@app.command(name="sync")
def cmd_sync(...) -> None: ...

# Entry point
if __name__ == "__main__":
    app()
```

## Command Interfaces

### slap

Set an application as the default for a file extension.

#### Function Signature

```python
@app.command(name="slap")
def cmd_slap(
    path: Path = Argument(
        ...,
        help="Path to application executable",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    md: bool = Option(False, "--md", help="Target .md files"),
    py: bool = Option(False, "--py", help="Target .py files"),
    txt: bool = Option(False, "--txt", help="Target .txt files"),
    js: bool = Option(False, "--js", help="Target .js files"),
    html: bool = Option(False, "--html", help="Target .html files"),
    css: bool = Option(False, "--css", help="Target .css files"),
    json_ext: bool = Option(False, "--json", help="Target .json files"),
    yml: bool = Option(False, "--yml", help="Target .yml files"),
    yaml: bool = Option(False, "--yaml", help="Target .yaml files"),
    xml: bool = Option(False, "--xml", help="Target .xml files"),
    csv: bool = Option(False, "--csv", help="Target .csv files"),
    sql: bool = Option(False, "--sql", help="Target .sql files"),
    set_default: bool = Option(
        False,
        "-set",
        help="Set as default immediately (creates active state and auto-creates offer)",
    ),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Set an application as the default for a file extension."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `Path` | Required | Path to the application executable. Must exist and be a file. |
| `md` | `bool` | `False` | Target .md files |
| `py` | `bool` | `False` | Target .py files |
| `txt` | `bool` | `False` | Target .txt files |
| `js` | `bool` | `False` | Target .js files |
| `html` | `bool` | `False` | Target .html files |
| `css` | `bool` | `False` | Target .css files |
| `json_ext` | `bool` | `False` | Target .json files |
| `yml` | `bool` | `False` | Target .yml files |
| `yaml` | `bool` | `False` | Target .yaml files |
| `xml` | `bool` | `False` | Target .xml files |
| `csv` | `bool` | `False` | Target .csv files |
| `sql` | `bool` | `False` | Target .sql files |
| `set_default` | `bool` | `False` | If `True`, sets the application as default immediately. |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Semantics

1. Validates that `path` exists and is an executable file
2. Determines extension from the boolean flags (first True flag wins)
3. If `set_default` is `True`, marks the association as active
4. When `set_default` is used, an offer is automatically created for the pairing

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE101` | Path does not exist | Invalid path: {path} does not exist |
| `VE102` | No extension specified or invalid | Invalid extension: {ext} is not supported |
| `VE301` | Default already exists (active state) | Default already exists for {ext} |
| `VE501` | Unexpected error | Unexpected error: {message} |

---

### chop

Remove or forget a file extension association.

#### Function Signature

```python
@app.command(name="chop")
def cmd_chop(
    md: bool = Option(False, "--md", help="Target .md files"),
    py: bool = Option(False, "--py", help="Target .py files"),
    txt: bool = Option(False, "--txt", help="Target .txt files"),
    js: bool = Option(False, "--js", help="Target .js files"),
    html: bool = Option(False, "--html", help="Target .html files"),
    css: bool = Option(False, "--css", help="Target .css files"),
    json_ext: bool = Option(False, "--json", help="Target .json files"),
    yml: bool = Option(False, "--yml", help="Target .yml files"),
    yaml: bool = Option(False, "--yaml", help="Target .yaml files"),
    xml: bool = Option(False, "--xml", help="Target .xml files"),
    csv: bool = Option(False, "--csv", help="Target .csv files"),
    sql: bool = Option(False, "--sql", help="Target .sql files"),
    forget: bool = Option(
        False,
        "-forget",
        help="Forget the default (transition to removed state)",
    ),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Remove or forget a file extension association."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `md` | `bool` | `False` | Target .md files |
| `py` | `bool` | `False` | Target .py files |
| `txt` | `bool` | `False` | Target .txt files |
| `js` | `bool` | `False` | Target .js files |
| `html` | `bool` | `False` | Target .html files |
| `css` | `bool` | `False` | Target .css files |
| `json_ext` | `bool` | `False` | Target .json files |
| `yml` | `bool` | `False` | Target .yml files |
| `yaml` | `bool` | `False` | Target .yaml files |
| `xml` | `bool` | `False` | Target .xml files |
| `csv` | `bool` | `False` | Target .csv files |
| `sql` | `bool` | `False` | Target .sql files |
| `forget` | `bool` | `False` | If `True`, forgets the default association. |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE102` | No extension specified or invalid | Invalid extension: {ext} is not supported |
| `VE302` | No default set | No default set for {ext} |
| `VE501` | Unexpected error | Unexpected error: {message} |

---

### set

Set a default for a file extension.

#### Function Signature

```python
@app.command(name="set")
def cmd_set(
    path: Path = Argument(
        ...,
        help="Path to application executable",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    md: bool = Option(False, "--md", help="Target .md files"),
    py: bool = Option(False, "--py", help="Target .py files"),
    txt: bool = Option(False, "--txt", help="Target .txt files"),
    js: bool = Option(False, "--js", help="Target .js files"),
    html: bool = Option(False, "--html", help="Target .html files"),
    css: bool = Option(False, "--css", help="Target .css files"),
    json_ext: bool = Option(False, "--json", help="Target .json files"),
    yml: bool = Option(False, "--yml", help="Target .yml files"),
    yaml: bool = Option(False, "--yaml", help="Target .yaml files"),
    xml: bool = Option(False, "--xml", help="Target .xml files"),
    csv: bool = Option(False, "--csv", help="Target .csv files"),
    sql: bool = Option(False, "--sql", help="Target .sql files"),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Set a default for a file extension."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `Path` | Required | Path to the application executable. Must exist and be a file. |
| `md` | `bool` | `False` | Target .md files |
| `py` | `bool` | `False` | Target .py files |
| `txt` | `bool` | `False` | Target .txt files |
| `js` | `bool` | `False` | Target .js files |
| `html` | `bool` | `False` | Target .html files |
| `css` | `bool` | `False` | Target .css files |
| `json_ext` | `bool` | `False` | Target .json files |
| `yml` | `bool` | `False` | Target .yml files |
| `yaml` | `bool` | `False` | Target .yaml files |
| `xml` | `bool` | `False` | Target .xml files |
| `csv` | `bool` | `False` | Target .csv files |
| `sql` | `bool` | `False` | Target .sql files |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE101` | Path does not exist | Invalid path: {path} does not exist |
| `VE102` | No extension specified or invalid | Invalid extension: {ext} is not supported |
| `VE301` | Default already exists (active state) | Default already exists for {ext} |
| `VE501` | Unexpected error | Unexpected error: {message} |

---

### forget

Forget a default for a file extension.

#### Function Signature

```python
@app.command(name="forget")
def cmd_forget(
    md: bool = Option(False, "--md", help="Target .md files"),
    py: bool = Option(False, "--py", help="Target .py files"),
    txt: bool = Option(False, "--txt", help="Target .txt files"),
    js: bool = Option(False, "--js", help="Target .js files"),
    html: bool = Option(False, "--html", help="Target .html files"),
    css: bool = Option(False, "--css", help="Target .css files"),
    json_ext: bool = Option(False, "--json", help="Target .json files"),
    yml: bool = Option(False, "--yml", help="Target .yml files"),
    yaml: bool = Option(False, "--yaml", help="Target .yaml files"),
    xml: bool = Option(False, "--xml", help="Target .xml files"),
    csv: bool = Option(False, "--csv", help="Target .csv files"),
    sql: bool = Option(False, "--sql", help="Target .sql files"),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Forget a default for a file extension."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `md` | `bool` | `False` | Target .md files |
| `py` | `bool` | `False` | Target .py files |
| `txt` | `bool` | `False` | Target .txt files |
| `js` | `bool` | `False` | Target .js files |
| `html` | `bool` | `False` | Target .html files |
| `css` | `bool` | `False` | Target .css files |
| `json_ext` | `bool` | `False` | Target .json files |
| `yml` | `bool` | `False` | Target .yml files |
| `yaml` | `bool` | `False` | Target .yaml files |
| `xml` | `bool` | `False` | Target .xml files |
| `csv` | `bool` | `False` | Target .csv files |
| `sql` | `bool` | `False` | Target .sql files |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE102` | No extension specified or invalid | Invalid extension: {ext} is not supported |
| `VE302` | No default set | No default set for {ext} |
| `VE501` | Unexpected error | Unexpected error: {message} |

---

### offer

Create a custom shortcut/alias for a file extension default.

#### Function Signature

```python
@app.command(name="offer")
def cmd_offer(
    offer_id: str = Argument(
        ...,
        help="Unique identifier for the offer (lowercase alphanumeric, hyphens, underscores)",
    ),
    path: Path = Argument(
        ...,
        help="Path to application executable",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    md: bool = Option(False, "--md", help="Target .md files"),
    py: bool = Option(False, "--py", help="Target .py files"),
    txt: bool = Option(False, "--txt", help="Target .txt files"),
    js: bool = Option(False, "--js", help="Target .js files"),
    html: bool = Option(False, "--html", help="Target .html files"),
    css: bool = Option(False, "--css", help="Target .css files"),
    json_ext: bool = Option(False, "--json", help="Target .json files"),
    yml: bool = Option(False, "--yml", help="Target .yml files"),
    yaml: bool = Option(False, "--yaml", help="Target .yaml files"),
    xml: bool = Option(False, "--xml", help="Target .xml files"),
    csv: bool = Option(False, "--csv", help="Target .csv files"),
    sql: bool = Option(False, "--sql", help="Target .sql files"),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Create a custom shortcut/alias for a file extension default."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `offer_id` | `str` | Required | Custom shortcut/alias identifier. Must match pattern `^[a-z][a-z0-9_-]{0,31}$`. |
| `path` | `Path` | Required | Path to the application executable. Must exist and be a file. |
| `md` | `bool` | `False` | Target .md files |
| `py` | `bool` | `False` | Target .py files |
| `txt` | `bool` | `False` | Target .txt files |
| `js` | `bool` | `False` | Target .js files |
| `html` | `bool` | `False` | Target .html files |
| `css` | `bool` | `False` | Target .css files |
| `json_ext` | `bool` | `False` | Target .json files |
| `yml` | `bool` | `False` | Target .yml files |
| `yaml` | `bool` | `False` | Target .yaml files |
| `xml` | `bool` | `False` | Target .xml files |
| `csv` | `bool` | `False` | Target .csv files |
| `sql` | `bool` | `False` | Target .sql files |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE101` | Path does not exist | Invalid path: {path} does not exist |
| `VE102` | No extension specified or invalid | Invalid extension: {ext} is not supported |
| `VE103` | Invalid offer_id format | Invalid offer_id: {id} does not match pattern |
| `VE303` | Offer already exists | Offer already exists: {id} |
| `VE501` | Unexpected error | Unexpected error: {message} |

---

### reject

Remove a custom offer.

#### Function Signature

```python
@app.command(name="reject")
def cmd_reject(
    offer_id: str = Argument(
        ...,
        help="The offer ID to reject",
    ),
    complete_delete: bool = Option(
        False,
        "-.",
        help="Complete delete - remove offer entirely from data file",
    ),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Remove a custom offer."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `offer_id` | `str` | Required | Custom shortcut/alias identifier to remove. |
| `complete_delete` | `bool` | `False` | If `True` (using `-.`), removes offer entirely from data file. |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE104` | Offer not found | Offer not found: {id} does not exist |
| `VE501` | Unexpected error | Unexpected error: {message} |

---

### list

Display tracked assets and offers.

#### Function Signature

```python
@app.command(name="list")
def cmd_list(
    app: bool = Option(False, "-app", help="List applications"),
    cmd: bool = Option(False, "-cmd", help="List commands"),
    ext: bool = Option(False, "-ext", help="List extensions"),
    defaults: bool = Option(False, "-def", help="List defaults"),
    offers: bool = Option(False, "-off", help="List offers"),
    all_sections: bool = Option(False, "-all", help="List all sections"),
    md: bool = Option(False, "--md", help="Filter by .md extension"),
    py: bool = Option(False, "--py", help="Filter by .py extension"),
    txt: bool = Option(False, "--txt", help="Filter by .txt extension"),
    js: bool = Option(False, "--js", help="Filter by .js extension"),
    html: bool = Option(False, "--html", help="Filter by .html extension"),
    css: bool = Option(False, "--css", help="Filter by .css extension"),
    json_ext: bool = Option(False, "--json", help="Filter by .json extension"),
    yml: bool = Option(False, "--yml", help="Filter by .yml extension"),
    yaml: bool = Option(False, "--yaml", help="Filter by .yaml extension"),
    xml: bool = Option(False, "--xml", help="Filter by .xml extension"),
    csv: bool = Option(False, "--csv", help="Filter by .csv extension"),
    sql: bool = Option(False, "--sql", help="Filter by .sql extension"),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Display tracked assets and offers."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `app` | `bool` | `False` | List applications |
| `cmd` | `bool` | `False` | List commands |
| `ext` | `bool` | `False` | List extensions |
| `defaults` | `bool` | `False` | List defaults |
| `offers` | `bool` | `False` | List offers |
| `all_sections` | `bool` | `False` | List all sections |
| `md` | `bool` | `False` | Filter by .md extension |
| `py` | `bool` | `False` | Filter by .py extension |
| `txt` | `bool` | `False` | Filter by .txt extension |
| `js` | `bool` | `False` | Filter by .js extension |
| `html` | `bool` | `False` | Filter by .html extension |
| `css` | `bool` | `False` | Filter by .css extension |
| `json_ext` | `bool` | `False` | Filter by .json extension |
| `yml` | `bool` | `False` | Filter by .yml extension |
| `yaml` | `bool` | `False` | Filter by .yaml extension |
| `xml` | `bool` | `False` | Filter by .xml extension |
| `csv` | `bool` | `False` | Filter by .csv extension |
| `sql` | `bool` | `False` | Filter by .sql extension |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console as formatted tables.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE102` | Invalid extension filter | Invalid extension: {ext} is not supported |
| `VE105` | Invalid subsection | Invalid list subsection: {section} |
| `VE501` | Unexpected error | Unexpected error: {message} |

---

### sync

Sync all active defaults to the operating system.

#### Function Signature

```python
@app.command(name="sync")
def cmd_sync(
    dry_run: bool = Option(
        False,
        "-dry",
        help="Preview changes without applying them to the OS",
    ),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Sync all active defaults to the OS."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `dry_run` | `bool` | `False` | If `True`, previews changes without applying them. |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Semantics

1. Loads all active defaults from the JSON store
2. For each active default, checks if the OS default matches
3. Skips entries that are already correctly configured
4. Applies changes for out-of-sync entries
5. Reports success/failure for each extension
6. Continues processing remaining entries even if some fail

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE601` | Unsupported platform | Unsupported platform: {platform} |
| `VE606` | Partial sync failure | Sync partially failed: {succeeded} succeeded, {failed} failed |
| `VE501` | Unexpected error | Unexpected error: {message} |

## Common Patterns

### Error Handling Pattern

All commands follow a consistent error handling pattern:

```python
from rich.console import Console
from typing import NoReturn

console = Console()

class VinceError(Exception):
    """Base exception for vince CLI errors."""
    
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

def handle_error(error: VinceError) -> NoReturn:
    """Display error and exit with appropriate code."""
    console.print(f"[red bold]✗ {error.code}:[/] {error.message}")
    if error.recovery:
        console.print(f"[cyan]ℹ[/] {error.recovery}")
    raise SystemExit(1)
```

### Verbose Output Pattern

Commands support verbose output via the `-vb`/`--verbose` flag:

```python
def cmd_slap(
    path: Path,
    verbose: bool = False,
) -> None:
    if verbose:
        console.print(f"[info]ℹ[/] Processing path: {path}")
    
    # ... command logic ...
    
    if verbose:
        console.print(f"[info]ℹ[/] Operation completed successfully")
```

### Extension Flag Pattern

Extension flags use individual boolean options for each supported extension:

```python
# Extension options are defined as individual boolean flags
md: bool = Option(False, "--md", help="Target .md files"),
py: bool = Option(False, "--py", help="Target .py files"),
txt: bool = Option(False, "--txt", help="Target .txt files"),
js: bool = Option(False, "--js", help="Target .js files"),
html: bool = Option(False, "--html", help="Target .html files"),
css: bool = Option(False, "--css", help="Target .css files"),
json_ext: bool = Option(False, "--json", help="Target .json files"),
yml: bool = Option(False, "--yml", help="Target .yml files"),
yaml: bool = Option(False, "--yaml", help="Target .yaml files"),
xml: bool = Option(False, "--xml", help="Target .xml files"),
csv: bool = Option(False, "--csv", help="Target .csv files"),
sql: bool = Option(False, "--sql", help="Target .sql files"),
```

### Path Validation Pattern

Path arguments include built-in validation:

```python
path: Path = Argument(
    ...,
    help="Path to application executable",
    exists=True,        # Must exist on filesystem
    file_okay=True,     # Can be a file
    dir_okay=False,     # Cannot be a directory
    resolve_path=True,  # Convert to absolute path
)
```

## Supported Extensions

All 12 supported file extensions from `SUPPORTED_EXTENSIONS`:

| Extension | Flag | Description |
| --- | --- | --- |
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

## Usage Examples

### Basic slap Usage

```bash
# Set an application for markdown files
vince slap /usr/bin/code --md

# Set as default immediately
vince slap /usr/bin/code -set --md

# With verbose output
vince slap /usr/bin/code -set --md -vb
```

### Basic chop Usage

```bash
# Remove default for markdown files
vince chop --md -forget

# Show current default info (no state change)
vince chop --md
```

### Basic set/forget Usage

```bash
# Set a default
vince set /usr/bin/code --md

# Forget a default
vince forget --md
```

### Basic offer/reject Usage

```bash
# Create an offer
vince offer mycode /usr/bin/code --md

# Reject an offer
vince reject mycode

# Complete-delete an offer
vince reject mycode -.
```

### Basic list Usage

```bash
# List all applications
vince list -app

# List all defaults
vince list -def

# List all offers
vince list -off

# List everything
vince list -all

# Filter by extension
vince list -def --md
```

### Basic sync Usage

```bash
# Sync all active defaults to the OS
vince sync

# Preview changes without applying
vince sync -dry

# Sync with verbose output
vince sync -vb
```

### Programmatic Usage

```python
from pathlib import Path
from vince.commands.slap import cmd_slap
from vince.commands.list_cmd import cmd_list

# Set a default programmatically
cmd_slap(
    path=Path("/usr/bin/code"),
    md=True,
    set_default=True,
    verbose=True,
)

# List defaults
cmd_list(
    defaults=True,
    verbose=False,
)
```

## Cross-References

- [tables.md](tables.md) - Single Source of Truth for command definitions (COMMANDS table)
- [errors.md](errors.md) - Complete error catalog with codes VE101-VE501
- [states.md](states.md) - State machine documentation for defaults and offers
- [schemas.md](schemas.md) - JSON schema definitions for data persistence
- [config.md](config.md) - Configuration options and hierarchy
- [examples.md](examples.md) - Additional usage examples
