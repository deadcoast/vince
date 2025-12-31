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
    extension: Optional[str] = Option(None, "--md", "--py", help="File extension"),
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
    extension: Optional[str] = Option(
        None,
        "--md", "--py", "--txt", "--js", "--html", "--css",
        "--json", "--yml", "--yaml", "--xml", "--csv", "--sql",
        help="Target file extension",
    ),
    set_default: bool = Option(
        False,
        "-set",
        help="Set as default immediately",
    ),
    verbose: bool = Option(
        False,
        "-vb", "--verbose",
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
| `extension` | `Optional[str]` | `None` | Target file extension (e.g., `--md`, `--py`). |
| `set_default` | `bool` | `False` | If `True`, sets the application as default immediately. |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Semantics

1. Validates that `path` exists and is an executable file
2. If `extension` is provided, associates the application with that extension
3. If `set_default` is `True`, marks the association as active
4. When `set_default` is used, an offer is automatically created for the pairing

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE101` | Path does not exist | Invalid path: {path} does not exist |
| `VE201` | File not found | File not found: {path} |
| `VE301` | Default already exists | Default already exists for {ext} |

---

### chop

Remove or forget a file extension association.

#### Function Signature

```python
@app.command(name="chop")
def cmd_chop(
    extension: Optional[str] = Option(
        None,
        "--md", "--py", "--txt", "--js", "--html", "--css",
        "--json", "--yml", "--yaml", "--xml", "--csv", "--sql",
        help="Target file extension to remove",
    ),
    forget: bool = Option(
        False,
        "-forget",
        help="Forget the default association",
    ),
    verbose: bool = Option(
        False,
        "-vb", "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Remove or forget a file extension association."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `extension` | `Optional[str]` | `None` | Target file extension to remove (e.g., `--md`). |
| `forget` | `bool` | `False` | If `True`, forgets the default association. |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE102` | Invalid extension | Invalid extension: {ext} is not supported |
| `VE202` | Permission denied | Permission denied: cannot access {path} |
| `VE302` | No default set | No default set for {ext} |

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
    extension: Optional[str] = Option(
        None,
        "--md", "--py", "--txt", "--js", "--html", "--css",
        "--json", "--yml", "--yaml", "--xml", "--csv", "--sql",
        help="Target file extension",
    ),
    verbose: bool = Option(
        False,
        "-vb", "--verbose",
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
| `extension` | `Optional[str]` | `None` | Target file extension (e.g., `--md`, `--py`). |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE101` | Path does not exist | Invalid path: {path} does not exist |
| `VE201` | File not found | File not found: {path} |
| `VE301` | Default already exists | Default already exists for {ext} |

---

### forget

Forget a default for a file extension.

#### Function Signature

```python
@app.command(name="forget")
def cmd_forget(
    extension: Optional[str] = Option(
        None,
        "--md", "--py", "--txt", "--js", "--html", "--css",
        "--json", "--yml", "--yaml", "--xml", "--csv", "--sql",
        help="Target file extension to forget",
    ),
    verbose: bool = Option(
        False,
        "-vb", "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Forget a default for a file extension."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `extension` | `Optional[str]` | `None` | Target file extension to forget (e.g., `--md`). |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE102` | Invalid extension | Invalid extension: {ext} is not supported |
| `VE302` | No default set | No default set for {ext} |

---

### offer

Create a custom shortcut/alias for a file extension default.

#### Function Signature

```python
@app.command(name="offer")
def cmd_offer(
    offer_id: str = Argument(
        ...,
        help="Custom shortcut/alias identifier",
    ),
    path: Path = Argument(
        ...,
        help="Path to application executable",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    extension: Optional[str] = Option(
        None,
        "--md", "--py", "--txt", "--js", "--html", "--css",
        "--json", "--yml", "--yaml", "--xml", "--csv", "--sql",
        help="Target file extension",
    ),
    verbose: bool = Option(
        False,
        "-vb", "--verbose",
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
| `extension` | `Optional[str]` | `None` | Target file extension (e.g., `--md`, `--py`). |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE103` | Invalid offer_id format | Invalid offer_id: {id} does not match pattern |
| `VE201` | File not found | File not found: {path} |
| `VE303` | Offer already exists | Offer already exists: {id} |

---

### reject

Remove a custom offer.

#### Function Signature

```python
@app.command(name="reject")
def cmd_reject(
    offer_id: str = Argument(
        ...,
        help="Custom shortcut/alias identifier to remove",
    ),
    complete_delete: bool = Option(
        False,
        ".",
        help="Complete-delete: remove offer, its id, and all connections",
    ),
    verbose: bool = Option(
        False,
        "-vb", "--verbose",
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
| `complete_delete` | `bool` | `False` | If `True` (using `.`), removes offer, its id, and all connections. |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE104` | Offer not found | Offer not found: {id} does not exist |
| `VE304` | Cannot reject | Cannot reject: offer {id} is in use |

---

### list

Display tracked assets and offers.

#### Function Signature

```python
@app.command(name="list")
def cmd_list(
    subsection: Optional[str] = Option(
        None,
        "-app", "-cmd", "-ext", "-def", "-off", "-all",
        help="Subsection to display",
    ),
    extension: Optional[str] = Option(
        None,
        "--md", "--py", "--txt", "--js", "--html", "--css",
        "--json", "--yml", "--yaml", "--xml", "--csv", "--sql",
        help="Filter by file extension",
    ),
    verbose: bool = Option(
        False,
        "-vb", "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Display tracked assets and offers."""
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `subsection` | `Optional[str]` | `None` | Subsection to display: `-app`, `-cmd`, `-ext`, `-def`, `-off`, or `-all`. |
| `extension` | `Optional[str]` | `None` | Filter results by file extension. |
| `verbose` | `bool` | `False` | If `True`, enables detailed output. |

#### Return Type

Returns `None`. Output is displayed via Rich console as formatted tables.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE105` | Invalid subsection | Invalid list subsection: {section} |

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
    console.print(f"[error]✗[/] [{error.code}] {error.message}")
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

Extension flags use a consistent pattern across commands:

```python
# Extension options are defined as multiple option names
extension: Optional[str] = Option(
    None,
    "--md", "--py", "--txt", "--js", "--html", "--css",
    "--json", "--yml", "--yaml", "--xml", "--csv", "--sql",
    help="Target file extension",
)
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

## Usage Examples

### Basic slap Usage

```python
# Set an application for markdown files
vince slap /usr/bin/code --md

# Set as default immediately
vince slap /usr/bin/code -set --md

# With verbose output
vince slap /usr/bin/code -set --md -vb
```

### Basic chop Usage

```python
# Remove default for markdown files
vince chop --md -forget

# Using wildcard operator
vince chop . -forget --md
```

### Basic set/forget Usage

```python
# Set a default
vince set /usr/bin/code --md

# Forget a default
vince forget --md
```

### Basic offer/reject Usage

```python
# Create an offer
vince offer mycode /usr/bin/code --md

# Reject an offer
vince reject mycode

# Complete-delete an offer
vince reject mycode .
```

### Basic list Usage

```python
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

### Programmatic Usage

```python
from pathlib import Path
from vince.commands import cmd_slap, cmd_list

# Set a default programmatically
cmd_slap(
    path=Path("/usr/bin/code"),
    extension="--md",
    set_default=True,
    verbose=True,
)

# List defaults
cmd_list(
    subsection="-def",
    extension=None,
    verbose=False,
)
```
