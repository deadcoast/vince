# Vince CLI Implementation Guide

This guide provides detailed implementation specifications for building the vince CLI Python application. Use this alongside the documentation in `docs/`.

---
inclusion: manual
---

## Quick Start

```bash
# Initialize project
uv init vince
cd vince
uv add typer rich

# Run CLI
uv run python -m vince --help
```

## Entry Point Implementation

```python
# vince/main.py
from typer import Typer, Option, Argument
from typing import Optional
from pathlib import Path

app = Typer(
    name="vince",
    help="A Rich CLI for setting default applications to file extensions.",
    add_completion=False,
    rich_markup_mode="rich",
)

# Import and register commands
from vince.commands import slap, chop, set_cmd, forget, offer, reject, list_cmd

app.command(name="slap")(slap.cmd_slap)
app.command(name="chop")(chop.cmd_chop)
app.command(name="set")(set_cmd.cmd_set)
app.command(name="forget")(forget.cmd_forget)
app.command(name="offer")(offer.cmd_offer)
app.command(name="reject")(reject.cmd_reject)
app.command(name="list")(list_cmd.cmd_list)

if __name__ == "__main__":
    app()
```

## Error System Implementation

```python
# vince/errors.py
from dataclasses import dataclass
from typing import Optional
from rich.console import Console

console = Console()

@dataclass
class VinceError(Exception):
    """Base exception for vince CLI errors."""
    code: str
    message: str
    recovery: Optional[str] = None
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

# Input Errors (VE1xx)
class InvalidPathError(VinceError):
    def __init__(self, path: str):
        super().__init__(
            code="VE101",
            message=f"Invalid path: {path} does not exist",
            recovery="Verify the application path exists and is accessible"
        )

class InvalidExtensionError(VinceError):
    def __init__(self, ext: str):
        super().__init__(
            code="VE102",
            message=f"Invalid extension: {ext} is not supported",
            recovery="Use a supported extension (--md, --py, etc.)"
        )

class InvalidOfferIdError(VinceError):
    def __init__(self, offer_id: str):
        super().__init__(
            code="VE103",
            message=f"Invalid offer_id: {offer_id} does not match pattern",
            recovery="Use lowercase alphanumeric with hyphens/underscores (max 32 chars)"
        )

class OfferNotFoundError(VinceError):
    def __init__(self, offer_id: str):
        super().__init__(
            code="VE104",
            message=f"Offer not found: {offer_id} does not exist",
            recovery="Use `list -off` to see available offers"
        )

class InvalidSubsectionError(VinceError):
    def __init__(self, section: str):
        super().__init__(
            code="VE105",
            message=f"Invalid list subsection: {section}",
            recovery="Use -app, -cmd, -ext, -def, -off, or -all"
        )

# File Errors (VE2xx)
class FileNotFoundError(VinceError):
    def __init__(self, path: str):
        super().__init__(
            code="VE201",
            message=f"File not found: {path}",
            recovery="Check file path and ensure the file exists"
        )

class PermissionDeniedError(VinceError):
    def __init__(self, path: str):
        super().__init__(
            code="VE202",
            message=f"Permission denied: cannot access {path}",
            recovery="Check file permissions and ownership"
        )

class DataCorruptedError(VinceError):
    def __init__(self, file: str):
        super().__init__(
            code="VE203",
            message=f"Data file corrupted: {file}",
            recovery="Restore from backup or delete and recreate the data file"
        )

# State Errors (VE3xx)
class DefaultExistsError(VinceError):
    def __init__(self, ext: str):
        super().__init__(
            code="VE301",
            message=f"Default already exists for {ext}",
            recovery="Use `chop` to remove existing default first"
        )

class NoDefaultError(VinceError):
    def __init__(self, ext: str):
        super().__init__(
            code="VE302",
            message=f"No default set for {ext}",
            recovery="Use `slap` or `set` to create a default"
        )

class OfferExistsError(VinceError):
    def __init__(self, offer_id: str):
        super().__init__(
            code="VE303",
            message=f"Offer already exists: {offer_id}",
            recovery="Use a different offer_id or reject existing offer"
        )

class OfferInUseError(VinceError):
    def __init__(self, offer_id: str):
        super().__init__(
            code="VE304",
            message=f"Cannot reject: offer {offer_id} is in use",
            recovery="Remove dependencies before rejecting"
        )

# Config Errors (VE4xx)
class InvalidConfigOptionError(VinceError):
    def __init__(self, key: str):
        super().__init__(
            code="VE401",
            message=f"Invalid config option: {key}",
            recovery="Check config.md for valid configuration options"
        )

class ConfigMalformedError(VinceError):
    def __init__(self, file: str):
        super().__init__(
            code="VE402",
            message=f"Config file malformed: {file}",
            recovery="Fix JSON syntax errors or restore default config"
        )

# System Errors (VE5xx)
class UnexpectedError(VinceError):
    def __init__(self, message: str):
        super().__init__(
            code="VE501",
            message=f"Unexpected error: {message}",
            recovery="Report issue with full error details to maintainers"
        )

def handle_error(error: VinceError) -> None:
    """Display error and exit with appropriate code."""
    console.print(f"[red bold]✗ {error.code}:[/] {error.message}")
    if error.recovery:
        console.print(f"[cyan]ℹ[/] {error.recovery}")
    raise SystemExit(1)
```

## Validation Implementation

```python
# vince/validation/path.py
import os
from pathlib import Path
from vince.errors import InvalidPathError, PermissionDeniedError

def validate_path(path: Path) -> Path:
    """Validate application path exists and is executable."""
    path = path.resolve()
    
    if not path.exists():
        raise InvalidPathError(str(path))
    
    if not path.is_file():
        raise InvalidPathError(str(path))
    
    if not os.access(path, os.X_OK):
        raise PermissionDeniedError(str(path))
    
    return path
```

```python
# vince/validation/extension.py
import re
from vince.errors import InvalidExtensionError

EXTENSION_PATTERN = re.compile(r'^\.[a-z0-9]+$')

SUPPORTED_EXTENSIONS = {
    ".md", ".py", ".txt", ".js", ".html", ".css",
    ".json", ".yml", ".yaml", ".xml", ".csv", ".sql"
}

def validate_extension(ext: str) -> str:
    """Validate file extension format and support."""
    ext = ext.lower()
    
    if not EXTENSION_PATTERN.match(ext):
        raise InvalidExtensionError(ext)
    
    if ext not in SUPPORTED_EXTENSIONS:
        raise InvalidExtensionError(ext)
    
    return ext

def flag_to_extension(flag: str) -> str:
    """Convert CLI flag to extension (--md -> .md)."""
    if flag.startswith("--"):
        return f".{flag[2:]}"
    return flag
```

```python
# vince/validation/offer_id.py
import re
from vince.errors import InvalidOfferIdError

OFFER_ID_PATTERN = re.compile(r'^[a-z][a-z0-9_-]{0,31}$')
RESERVED_NAMES = {'help', 'version', 'list', 'all', 'none', 'default'}

def validate_offer_id(offer_id: str) -> str:
    """Validate offer ID format and availability."""
    if not OFFER_ID_PATTERN.match(offer_id):
        raise InvalidOfferIdError(offer_id)
    
    if offer_id in RESERVED_NAMES:
        raise InvalidOfferIdError(offer_id)
    
    return offer_id
```

## Persistence Implementation

```python
# vince/persistence/base.py
import json
import fcntl
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, Any

@contextmanager
def file_lock(path: Path):
    """Acquire exclusive lock on file for write operations."""
    lock_path = path.with_suffix('.lock')
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(lock_path, 'w') as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

def atomic_write(path: Path, data: Dict[str, Any]) -> None:
    """Write data atomically using temp file + rename."""
    temp_path = path.with_suffix('.tmp')
    try:
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
        temp_path.rename(path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

def create_backup(path: Path, backup_dir: Path, max_backups: int = 5) -> None:
    """Create timestamped backup of file."""
    if not path.exists():
        return
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}.{timestamp}.bak"
    backup_path = backup_dir / backup_name
    
    # Copy current file to backup
    backup_path.write_text(path.read_text())
    
    # Cleanup old backups
    backups = sorted(backup_dir.glob(f"{path.stem}.*.bak"))
    while len(backups) > max_backups:
        backups[0].unlink()
        backups.pop(0)

def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    """Load JSON file with fallback to default."""
    if not path.exists():
        return default.copy()
    
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        from vince.errors import DataCorruptedError
        raise DataCorruptedError(str(path))
```

```python
# vince/persistence/defaults.py
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from vince.persistence.base import load_json, atomic_write, create_backup, file_lock

DEFAULT_SCHEMA = {
    "version": "1.0.0",
    "defaults": []
}

class DefaultsStore:
    def __init__(self, data_dir: Path):
        self.path = data_dir / "defaults.json"
        self.backup_dir = data_dir / "backups"
    
    def load(self) -> Dict[str, Any]:
        return load_json(self.path, DEFAULT_SCHEMA)
    
    def save(self, data: Dict[str, Any], max_backups: int = 5) -> None:
        with file_lock(self.path):
            create_backup(self.path, self.backup_dir, max_backups)
            atomic_write(self.path, data)
    
    def find_by_extension(self, ext: str) -> Optional[Dict[str, Any]]:
        data = self.load()
        for entry in data["defaults"]:
            if entry["extension"] == ext and entry["state"] != "removed":
                return entry
        return None
    
    def add(self, extension: str, application_path: str, state: str = "pending") -> Dict[str, Any]:
        data = self.load()
        entry = {
            "id": f"def-{extension[1:]}-{len(data['defaults']):03d}",
            "extension": extension,
            "application_path": application_path,
            "state": state,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        data["defaults"].append(entry)
        self.save(data)
        return entry
    
    def update_state(self, entry_id: str, new_state: str) -> None:
        data = self.load()
        for entry in data["defaults"]:
            if entry["id"] == entry_id:
                entry["state"] = new_state
                entry["updated_at"] = datetime.now(timezone.utc).isoformat()
                break
        self.save(data)
```

## State Machine Implementation

```python
# vince/state/default_state.py
from enum import Enum
from typing import Set
from vince.errors import DefaultExistsError, NoDefaultError

class DefaultState(Enum):
    NONE = "none"
    PENDING = "pending"
    ACTIVE = "active"
    REMOVED = "removed"

# Valid transitions: from_state -> set of valid to_states
VALID_TRANSITIONS: dict[DefaultState, Set[DefaultState]] = {
    DefaultState.NONE: {DefaultState.PENDING, DefaultState.ACTIVE},
    DefaultState.PENDING: {DefaultState.ACTIVE, DefaultState.NONE},
    DefaultState.ACTIVE: {DefaultState.REMOVED},
    DefaultState.REMOVED: {DefaultState.ACTIVE},
}

def validate_transition(current: DefaultState, target: DefaultState, extension: str) -> None:
    """Validate state transition is allowed."""
    if target not in VALID_TRANSITIONS.get(current, set()):
        if current == DefaultState.NONE and target in {DefaultState.REMOVED}:
            raise NoDefaultError(extension)
        if current == DefaultState.ACTIVE and target in {DefaultState.PENDING, DefaultState.ACTIVE}:
            raise DefaultExistsError(extension)
        raise ValueError(f"Invalid transition: {current.value} -> {target.value}")
```

## Output Implementation

```python
# vince/output/theme.py
from rich.theme import Theme
from rich.console import Console

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

console = Console(theme=VINCE_THEME)
```

```python
# vince/output/messages.py
from vince.output.theme import console

def print_success(message: str) -> None:
    console.print(f"[success]✓[/] {message}")

def print_warning(message: str) -> None:
    console.print(f"[warning]⚠[/] {message}")

def print_error(code: str, message: str) -> None:
    console.print(f"[error]✗ {code}:[/] {message}")

def print_info(message: str) -> None:
    console.print(f"[info]ℹ[/] {message}")
```

```python
# vince/output/tables.py
from rich.table import Table
from rich import box
from vince.output.theme import console

def create_defaults_table(defaults: list) -> Table:
    table = Table(title="Defaults", box=box.ROUNDED, header_style="header")
    table.add_column("Extension", style="extension")
    table.add_column("Application", style="path")
    table.add_column("State", style="state")
    
    for d in defaults:
        table.add_row(d["extension"], d["application_path"], d["state"])
    
    return table

def create_offers_table(offers: list) -> Table:
    table = Table(title="Offers", box=box.ROUNDED, header_style="header")
    table.add_column("Offer ID", style="offer")
    table.add_column("Default ID", style="info")
    table.add_column("State", style="state")
    
    for o in offers:
        table.add_row(o["offer_id"], o["default_id"], o["state"])
    
    return table
```

## Command Implementation Example

```python
# vince/commands/slap.py
from typer import Argument, Option
from pathlib import Path
from typing import Optional

from vince.validation.path import validate_path
from vince.validation.extension import validate_extension, flag_to_extension
from vince.persistence.defaults import DefaultsStore
from vince.persistence.offers import OffersStore
from vince.state.default_state import DefaultState, validate_transition
from vince.output.messages import print_success, print_info
from vince.errors import handle_error, DefaultExistsError
from vince.config import get_config

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
    try:
        config = get_config()
        verbose = verbose or config.get("verbose", False)
        
        # Validate inputs
        validated_path = validate_path(path)
        ext = flag_to_extension(extension) if extension else None
        
        if ext:
            ext = validate_extension(ext)
        
        if verbose:
            print_info(f"Processing path: {validated_path}")
        
        # Get stores
        data_dir = Path(config.get("data_dir", "~/.vince")).expanduser()
        defaults_store = DefaultsStore(data_dir)
        
        # Check existing default
        existing = defaults_store.find_by_extension(ext)
        current_state = DefaultState(existing["state"]) if existing else DefaultState.NONE
        target_state = DefaultState.ACTIVE if set_default else DefaultState.PENDING
        
        # Validate transition
        validate_transition(current_state, target_state, ext)
        
        # Create or update default
        if existing:
            defaults_store.update_state(existing["id"], target_state.value)
            entry = existing
        else:
            entry = defaults_store.add(ext, str(validated_path), target_state.value)
        
        # Auto-create offer if setting default
        if set_default:
            offers_store = OffersStore(data_dir)
            offer_id = f"{path.stem}-{ext[1:]}"
            offers_store.add(offer_id, entry["id"], auto_created=True)
            print_success(f"Offer created: [offer]{offer_id}[/]")
        
        print_success(f"Default {'set' if set_default else 'identified'} for [extension]{ext}[/]")
        
        if verbose:
            print_info(f"Application: {validated_path}")
            print_info(f"State: {target_state.value}")
    
    except Exception as e:
        from vince.errors import VinceError
        if isinstance(e, VinceError):
            handle_error(e)
        raise
```

## Config Implementation

```python
# vince/config.py
import json
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "data_dir": "~/.vince",
    "verbose": False,
    "color_theme": "default",
    "backup_enabled": True,
    "max_backups": 5,
    "confirm_destructive": True,
}

def get_config() -> Dict[str, Any]:
    """Load and merge configuration from all levels."""
    config = DEFAULT_CONFIG.copy()
    
    # User config
    user_config_path = Path("~/.vince/config.json").expanduser()
    if user_config_path.exists():
        try:
            user_config = json.loads(user_config_path.read_text())
            config.update(user_config)
        except json.JSONDecodeError:
            pass
    
    # Project config (highest priority)
    project_config_path = Path("./.vince/config.json")
    if project_config_path.exists():
        try:
            project_config = json.loads(project_config_path.read_text())
            config.update(project_config)
        except json.JSONDecodeError:
            pass
    
    return config
```

## Testing Example

```python
# tests/test_slap.py
import pytest
from typer.testing import CliRunner
from pathlib import Path
import json

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_executable(tmp_path):
    exe = tmp_path / "mock_app"
    exe.write_text("#!/bin/bash\necho 'mock'")
    exe.chmod(0o755)
    return exe

@pytest.fixture
def isolated_data_dir(tmp_path):
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()
    (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    (data_dir / "config.json").write_text('{"version": "1.0.0"}')
    return data_dir

class TestSlapCommand:
    def test_slap_creates_pending_default(self, runner, mock_executable, isolated_data_dir):
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["slap", str(mock_executable), "--md"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code == 0
        
        defaults = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults["defaults"]) == 1
        assert defaults["defaults"][0]["state"] == "pending"
    
    def test_slap_with_set_creates_active_default(self, runner, mock_executable, isolated_data_dir):
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["slap", str(mock_executable), "-set", "--md"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code == 0
        
        defaults = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults["defaults"][0]["state"] == "active"
```

## Property-Based Testing Example

```python
# tests/test_validation_properties.py
from hypothesis import given, settings
from hypothesis import strategies as st
import string

from vince.validation.extension import validate_extension, SUPPORTED_EXTENSIONS
from vince.validation.offer_id import validate_offer_id, RESERVED_NAMES
from vince.errors import InvalidExtensionError, InvalidOfferIdError

# Strategies
@st.composite
def valid_extensions(draw):
    return draw(st.sampled_from(list(SUPPORTED_EXTENSIONS)))

@st.composite
def valid_offer_ids(draw):
    first = draw(st.sampled_from(string.ascii_lowercase))
    rest = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "_-",
        min_size=0, max_size=31
    ))
    offer_id = first + rest
    if offer_id in RESERVED_NAMES:
        offer_id = f"custom-{offer_id}"
    return offer_id

# Property tests
class TestExtensionValidation:
    @given(valid_extensions())
    @settings(max_examples=100)
    def test_valid_extensions_pass(self, ext):
        """Property: All supported extensions should validate successfully."""
        result = validate_extension(ext)
        assert result == ext.lower()
    
    @given(st.text(min_size=1, max_size=10).filter(lambda x: not x.startswith(".")))
    @settings(max_examples=100)
    def test_extensions_without_dot_fail(self, ext):
        """Property: Extensions without leading dot should fail."""
        try:
            validate_extension(ext)
            assert False, "Should have raised InvalidExtensionError"
        except InvalidExtensionError:
            pass

class TestOfferIdValidation:
    @given(valid_offer_ids())
    @settings(max_examples=100)
    def test_valid_offer_ids_pass(self, offer_id):
        """Property: Valid offer IDs should validate successfully."""
        result = validate_offer_id(offer_id)
        assert result == offer_id
    
    @given(st.sampled_from(list(RESERVED_NAMES)))
    @settings(max_examples=100)
    def test_reserved_names_fail(self, name):
        """Property: Reserved names should fail validation."""
        try:
            validate_offer_id(name)
            assert False, "Should have raised InvalidOfferIdError"
        except InvalidOfferIdError:
            pass
```

## pyproject.toml

```toml
[project]
name = "vince"
version = "1.0.0"
description = "A Rich CLI for setting default applications to file extensions"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "hypothesis>=6.0.0",
]

[project.scripts]
vince = "vince.main:app"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=vince --cov-report=term-missing"

[tool.coverage.run]
source = ["vince"]
branch = true

[tool.coverage.report]
fail_under = 85
show_missing = true
```
