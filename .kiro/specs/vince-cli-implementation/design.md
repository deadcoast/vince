# Design Document: Vince CLI Implementation

## Overview

This design specifies the implementation of the vince CLI Python application. The CLI is built with Typer for command handling and Rich for terminal formatting. It provides 7 commands for managing default applications for file extensions, with a JSON-based persistence layer, state machine validation, and comprehensive error handling.

The implementation follows the documentation specifications in `docs/` and the steering files in `.kiro/steering/`.

## Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           VINCE CLI ARCHITECTURE                          │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                         CLI LAYER (Typer)                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │  slap   │ │  chop   │ │   set   │ │ forget  │ │  offer  │       │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │   │
│  │  ┌────┴────┐ ┌────┴────┐                                           │   │
│  │  │ reject  │ │  list   │                                           │   │
│  │  └────┬────┘ └────┬────┘                                           │   │
│  └───────┼──────────┼─────────────────────────────────────────────────┘   │
│          │          │                                                     │
│  ┌───────┴──────────┴─────────────────────────────────────────────────┐   │
│  │                      VALIDATION LAYER                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │    path     │  │  extension  │  │  offer_id   │                 │   │
│  │  │  validator  │  │  validator  │  │  validator  │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                       STATE LAYER                                  │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                  │   │
│  │  │  Default State      │  │  Offer State        │                  │   │
│  │  │  Machine            │  │  Machine            │                  │   │
│  │  │  none→pending→      │  │  none→created→      │                  │   │
│  │  │  active→removed     │  │  active→rejected    │                  │   │
│  │  └─────────────────────┘  └─────────────────────┘                  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                    PERSISTENCE LAYER                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │ DefaultsStore│  │ OffersStore │  │ ConfigLoader│                │   │
│  │  │ defaults.json│  │ offers.json │  │ config.json │                │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  │                                                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  Base: atomic_write, file_lock, create_backup, load_json    │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                      OUTPUT LAYER (Rich)                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │   theme     │  │  messages   │  │   tables    │                 │   │
│  │  │ VINCE_THEME │  │ print_*()   │  │ create_*()  │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                       ERROR LAYER                                  │   │
│  │  VinceError (base) → VE1xx, VE2xx, VE3xx, VE4xx, VE5xx             │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Component 1: Project Structure

```
vince/
├── __init__.py              # Package init with __version__
├── main.py                  # Typer app entry point
├── errors.py                # VinceError and all VE### classes
├── config.py                # Configuration loading and merging
├── commands/
│   ├── __init__.py
│   ├── slap.py              # cmd_slap()
│   ├── chop.py              # cmd_chop()
│   ├── set_cmd.py           # cmd_set()
│   ├── forget.py            # cmd_forget()
│   ├── offer.py             # cmd_offer()
│   ├── reject.py            # cmd_reject()
│   └── list_cmd.py          # cmd_list()
├── validation/
│   ├── __init__.py
│   ├── path.py              # validate_path()
│   ├── extension.py         # validate_extension()
│   └── offer_id.py          # validate_offer_id()
├── persistence/
│   ├── __init__.py
│   ├── base.py              # atomic_write, file_lock, backup
│   ├── defaults.py          # DefaultsStore
│   └── offers.py            # OffersStore
├── state/
│   ├── __init__.py
│   ├── default_state.py     # DefaultState enum, transitions
│   └── offer_state.py       # OfferState enum, transitions
└── output/
    ├── __init__.py
    ├── theme.py             # VINCE_THEME, console
    ├── messages.py          # print_success, print_error, etc.
    └── tables.py            # create_defaults_table, create_offers_table
```

### Component 2: Error System

```python
# vince/errors.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class VinceError(Exception):
    """Base exception for vince CLI errors."""
    code: str
    message: str
    recovery: Optional[str] = None
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

# Input Errors (VE1xx)
class InvalidPathError(VinceError): ...      # VE101
class InvalidExtensionError(VinceError): ... # VE102
class InvalidOfferIdError(VinceError): ...   # VE103
class OfferNotFoundError(VinceError): ...    # VE104
class InvalidSubsectionError(VinceError): ...# VE105

# File Errors (VE2xx)
class FileNotFoundError(VinceError): ...     # VE201
class PermissionDeniedError(VinceError): ... # VE202
class DataCorruptedError(VinceError): ...    # VE203

# State Errors (VE3xx)
class DefaultExistsError(VinceError): ...    # VE301
class NoDefaultError(VinceError): ...        # VE302
class OfferExistsError(VinceError): ...      # VE303
class OfferInUseError(VinceError): ...       # VE304

# Config Errors (VE4xx)
class InvalidConfigOptionError(VinceError): ...# VE401
class ConfigMalformedError(VinceError): ...    # VE402

# System Errors (VE5xx)
class UnexpectedError(VinceError): ...       # VE501
```

### Component 3: Validation System

```python
# vince/validation/path.py
def validate_path(path: Path) -> Path:
    """Validate application path exists and is executable.
    
    Raises:
        InvalidPathError: If path doesn't exist or isn't a file
        PermissionDeniedError: If path isn't executable
    """
    ...

# vince/validation/extension.py
EXTENSION_PATTERN = re.compile(r'^\.[a-z0-9]+$')
SUPPORTED_EXTENSIONS = {".md", ".py", ".txt", ".js", ".html", ".css",
                        ".json", ".yml", ".yaml", ".xml", ".csv", ".sql"}

def validate_extension(ext: str) -> str:
    """Validate file extension format and support.
    
    Raises:
        InvalidExtensionError: If extension is invalid or unsupported
    """
    ...

# vince/validation/offer_id.py
OFFER_ID_PATTERN = re.compile(r'^[a-z][a-z0-9_-]{0,31}$')
RESERVED_NAMES = {'help', 'version', 'list', 'all', 'none', 'default'}

def validate_offer_id(offer_id: str) -> str:
    """Validate offer ID format and availability.
    
    Raises:
        InvalidOfferIdError: If offer_id is invalid or reserved
    """
    ...
```

### Component 4: Persistence Layer

```python
# vince/persistence/base.py
def atomic_write(path: Path, data: Dict[str, Any]) -> None:
    """Write data atomically using temp file + rename."""
    ...

def file_lock(path: Path):
    """Context manager for exclusive file lock."""
    ...

def create_backup(path: Path, backup_dir: Path, max_backups: int = 5) -> None:
    """Create timestamped backup of file."""
    ...

def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    """Load JSON file with fallback to default."""
    ...

# vince/persistence/defaults.py
class DefaultsStore:
    def __init__(self, data_dir: Path): ...
    def load(self) -> Dict[str, Any]: ...
    def save(self, data: Dict[str, Any], max_backups: int = 5) -> None: ...
    def find_by_extension(self, ext: str) -> Optional[Dict[str, Any]]: ...
    def add(self, extension: str, application_path: str, state: str = "pending") -> Dict[str, Any]: ...
    def update_state(self, entry_id: str, new_state: str) -> None: ...

# vince/persistence/offers.py
class OffersStore:
    def __init__(self, data_dir: Path): ...
    def load(self) -> Dict[str, Any]: ...
    def save(self, data: Dict[str, Any], max_backups: int = 5) -> None: ...
    def find_by_id(self, offer_id: str) -> Optional[Dict[str, Any]]: ...
    def add(self, offer_id: str, default_id: str, auto_created: bool = False) -> Dict[str, Any]: ...
    def update_state(self, offer_id: str, new_state: str) -> None: ...
```

### Component 5: State Machine

```python
# vince/state/default_state.py
from enum import Enum

class DefaultState(Enum):
    NONE = "none"
    PENDING = "pending"
    ACTIVE = "active"
    REMOVED = "removed"

VALID_TRANSITIONS: dict[DefaultState, set[DefaultState]] = {
    DefaultState.NONE: {DefaultState.PENDING, DefaultState.ACTIVE},
    DefaultState.PENDING: {DefaultState.ACTIVE, DefaultState.NONE},
    DefaultState.ACTIVE: {DefaultState.REMOVED},
    DefaultState.REMOVED: {DefaultState.ACTIVE},
}

def validate_transition(current: DefaultState, target: DefaultState, extension: str) -> None:
    """Validate state transition is allowed.
    
    Raises:
        DefaultExistsError: If trying to create when active exists
        NoDefaultError: If trying to remove when none exists
    """
    ...

# vince/state/offer_state.py
class OfferState(Enum):
    NONE = "none"
    CREATED = "created"
    ACTIVE = "active"
    REJECTED = "rejected"

VALID_TRANSITIONS: dict[OfferState, set[OfferState]] = {
    OfferState.NONE: {OfferState.CREATED},
    OfferState.CREATED: {OfferState.ACTIVE, OfferState.REJECTED},
    OfferState.ACTIVE: {OfferState.REJECTED},
    OfferState.REJECTED: set(),
}
```

### Component 6: Configuration System

```python
# vince/config.py
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
    """Load and merge configuration from all levels.
    
    Precedence: project > user > default
    """
    ...
```

### Component 7: Output System

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

# vince/output/messages.py
def print_success(message: str) -> None: ...
def print_warning(message: str) -> None: ...
def print_error(code: str, message: str) -> None: ...
def print_info(message: str) -> None: ...

# vince/output/tables.py
def create_defaults_table(defaults: list) -> Table: ...
def create_offers_table(offers: list) -> Table: ...
```

## Data Models

### DefaultEntry

```python
@dataclass
class DefaultEntry:
    id: str                    # Unique identifier (e.g., "def-md-001")
    extension: str             # File extension (e.g., ".md")
    application_path: str      # Absolute path to executable
    state: str                 # "pending" | "active" | "removed"
    created_at: str            # ISO 8601 timestamp
    updated_at: Optional[str]  # ISO 8601 timestamp
```

### OfferEntry

```python
@dataclass
class OfferEntry:
    offer_id: str              # Custom identifier (e.g., "code-md")
    default_id: str            # Reference to DefaultEntry.id
    state: str                 # "created" | "active" | "rejected"
    auto_created: bool         # True if from slap -set
    created_at: str            # ISO 8601 timestamp
    used_at: Optional[str]     # ISO 8601 timestamp
```

### ConfigOptions

```python
@dataclass
class ConfigOptions:
    version: str               # Schema version
    data_dir: str              # Data storage directory
    verbose: bool              # Enable verbose output
    color_theme: str           # "default" | "dark" | "light"
    backup_enabled: bool       # Enable automatic backups
    max_backups: int           # Maximum backup files (0-100)
    confirm_destructive: bool  # Require confirmation
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Path Validation Correctness

*For any* file path, if the path exists, is a file, and is executable, then validate_path SHALL return the resolved path. If any condition fails, validate_path SHALL raise the appropriate error (InvalidPathError for non-existent/non-file, PermissionDeniedError for non-executable).

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 2: Extension Validation Correctness

*For any* string, if it matches the pattern `^\.[a-z0-9]+$` AND is in the supported extensions set, then validate_extension SHALL return the lowercase extension. Otherwise, validate_extension SHALL raise InvalidExtensionError.

**Validates: Requirements 3.5, 3.6, 3.7**

### Property 3: Offer ID Validation Correctness

*For any* string, if it matches the pattern `^[a-z][a-z0-9_-]{0,31}$` AND is not a reserved name, then validate_offer_id SHALL return the offer_id. Otherwise, validate_offer_id SHALL raise InvalidOfferIdError.

**Validates: Requirements 3.8, 3.9, 3.10**

### Property 4: Persistence Round-Trip Consistency

*For any* valid DefaultEntry or OfferEntry, saving to JSON and loading back SHALL produce an equivalent object. Specifically: `load(save(data)) == data` for all valid data.

**Validates: Requirements 4.1, 4.5, 4.7**

### Property 5: DefaultsStore Add-Find Consistency

*For any* valid extension and application path, after calling DefaultsStore.add(), calling find_by_extension() with the same extension SHALL return the added entry.

**Validates: Requirements 4.6**

### Property 6: OffersStore Add-Find Consistency

*For any* valid offer_id and default_id, after calling OffersStore.add(), calling find_by_id() with the same offer_id SHALL return the added entry.

**Validates: Requirements 4.8**

### Property 7: Backup Retention Limit

*For any* sequence of N writes with backup_enabled=true and max_backups=M, the number of backup files SHALL never exceed M. The oldest backups SHALL be deleted when the limit is exceeded.

**Validates: Requirements 4.9, 4.10**

### Property 8: Default State Transition Validity

*For any* default state transition, if the transition is in the VALID_TRANSITIONS map, validate_transition SHALL succeed. If the transition is not valid, validate_transition SHALL raise DefaultExistsError (for active→active) or NoDefaultError (for none→removed).

**Validates: Requirements 5.2, 5.3**

### Property 9: Offer State Transition Validity

*For any* offer state transition, if the transition is in the VALID_TRANSITIONS map, the transition SHALL succeed. If the transition is not valid, the appropriate error SHALL be raised.

**Validates: Requirements 5.5, 5.6**

### Property 10: Config Precedence Correctness

*For any* configuration key that exists at multiple levels (default, user, project), the value from the highest precedence level SHALL be used. Precedence order: project > user > default.

**Validates: Requirements 6.2, 6.3, 6.4**

### Property 11: Config Error Handling

*For any* malformed JSON config file, loading SHALL raise ConfigMalformedError (VE402). *For any* invalid config option value, loading SHALL raise InvalidConfigOptionError (VE401).

**Validates: Requirements 6.5, 6.6**

### Property 12: Error Class Completeness

*For any* VinceError subclass, it SHALL have code, message, and recovery attributes. The code SHALL follow the VE### format and fall within the correct category range.

**Validates: Requirements 2.2**

## Error Handling

### Error Flow

```
┌─────────────────────┐
│ Command Invoked     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│ Validate Inputs     │────►│ VinceError raised   │
│                     │ err └──────────┬──────────┘
└──────────┬──────────┘                │
           │ ok                        │
           ▼                           │
┌─────────────────────┐                │
│ Check State         │────►───────────┤
│                     │ err            │
└──────────┬──────────┘                │
           │ ok                        │
           ▼                           │
┌─────────────────────┐                │
│ Execute Operation   │────►───────────┤
│                     │ err            │
└──────────┬──────────┘                │
           │ ok                        ▼
           ▼                ┌─────────────────────┐
┌─────────────────────┐     │ handle_error()      │
│ Print Success       │     │ - Display formatted │
└─────────────────────┘     │ - Show recovery     │
                            │ - Exit with code 1  │
                            └─────────────────────┘
```

### Error Categories and Handling

| Category | Range | Handling |
|----------|-------|----------|
| Input (VE1xx) | VE101-VE105 | Display error, suggest correct input |
| File (VE2xx) | VE201-VE203 | Display error, suggest file operations |
| State (VE3xx) | VE301-VE304 | Display error, suggest state commands |
| Config (VE4xx) | VE401-VE402 | Display error, suggest config fixes |
| System (VE5xx) | VE501 | Display error, suggest reporting |

## Testing Strategy

### Dual Testing Approach

**Unit Tests**: Verify specific examples and edge cases
- Specific command invocations
- Known error conditions
- Integration between components

**Property-Based Tests**: Verify universal properties across all inputs
- Validation correctness for any input
- Persistence round-trip for any data
- State transition validity for any state

### Property-Based Testing Framework

We will use **Hypothesis** (Python) as the property-based testing library.

**Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: vince-cli-implementation, Property {number}: {property_text}**

### Test Categories

| Category | Type | Properties |
|----------|------|------------|
| Path Validation | Property | Property 1 |
| Extension Validation | Property | Property 2 |
| Offer ID Validation | Property | Property 3 |
| Persistence | Property | Properties 4, 5, 6, 7 |
| State Machine | Property | Properties 8, 9 |
| Configuration | Property | Properties 10, 11 |
| Error System | Property | Property 12 |
| Commands | Unit + Integration | All commands |

### Coverage Targets

| Component | Target |
|-----------|--------|
| Commands | 90% |
| Validation | 95% |
| Persistence | 95% |
| State Machine | 100% |
| Error Handling | 90% |
| Configuration | 85% |

### Test Fixtures

```python
@pytest.fixture
def cli_runner():
    """Provide a Typer CLI test runner."""
    return CliRunner()

@pytest.fixture
def mock_executable(tmp_path):
    """Create a mock executable file for testing."""
    exe = tmp_path / "mock_app"
    exe.write_text("#!/bin/bash\necho 'mock'")
    exe.chmod(0o755)
    return exe

@pytest.fixture
def isolated_data_dir(tmp_path):
    """Provide isolated data directory with empty data files."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()
    (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    (data_dir / "config.json").write_text('{"version": "1.0.0"}')
    return data_dir
```

### Hypothesis Strategies

```python
@st.composite
def valid_extensions(draw):
    """Generate valid file extensions."""
    return draw(st.sampled_from(list(SUPPORTED_EXTENSIONS)))

@st.composite
def valid_offer_ids(draw):
    """Generate valid offer IDs."""
    first = draw(st.sampled_from(string.ascii_lowercase))
    rest = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "_-",
        min_size=0, max_size=31
    ))
    offer_id = first + rest
    if offer_id in RESERVED_NAMES:
        offer_id = f"custom-{offer_id}"
    return offer_id

@st.composite
def invalid_extensions(draw):
    """Generate invalid file extensions."""
    strategies = [
        st.just("md"),           # Missing dot
        st.just(".MD"),          # Uppercase
        st.just(".m d"),         # Space
        st.just("..md"),         # Double dot
    ]
    return draw(st.one_of(*strategies))
```
