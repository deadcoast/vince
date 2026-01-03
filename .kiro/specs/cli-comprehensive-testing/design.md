# Design Document

## Overview

This design document specifies the comprehensive testing architecture for the vince CLI application. The testing strategy validates all 8 commands, 21 error codes, state machine transitions, and command interactions through a combination of unit tests, property-based tests, and integration tests.

The testing framework uses:
- **pytest**: Test runner and fixtures
- **Hypothesis**: Property-based testing with generators
- **typer.testing.CliRunner**: CLI command invocation
- **monkeypatch**: Dependency injection for isolation

## Architecture

### Test Organization

```
tests/
├── conftest.py                      # Shared fixtures
├── test_errors.py                   # Error class tests (existing)
├── test_state_machines.py           # State machine tests (existing)
├── test_persistence.py              # Persistence tests (existing)
├── test_integration.py              # Integration tests (existing)
├── test_slap_command.py             # Slap command tests (existing)
├── test_chop_command.py             # Chop command tests (existing)
├── test_set_command.py              # Set command tests (existing)
├── test_forget_command.py           # Forget command tests (existing)
├── test_offer_command.py            # Offer command tests (existing)
├── test_reject_command.py           # Reject command tests (existing)
├── test_list_command.py             # List command tests (existing)
├── test_sync_command.py             # Sync command tests (existing)
├── test_dry_run_idempotence.py      # Dry run property tests (existing)
├── test_command_handler_integration.py  # Handler integration tests (existing)
├── test_input_error_coverage.py     # NEW: VE1xx error tests
├── test_file_error_coverage.py      # NEW: VE2xx error tests
├── test_state_error_coverage.py     # NEW: VE3xx error tests
├── test_config_error_coverage.py    # NEW: VE4xx error tests
├── test_os_error_coverage.py        # NEW: VE6xx error tests
├── test_validation_properties.py    # NEW: Validation property tests
├── test_persistence_roundtrip.py    # NEW: Persistence round-trip tests
├── test_backup_retention.py         # NEW: Backup retention tests
├── test_verbose_output.py           # NEW: Verbose output tests
└── test_schema_migration.py         # Schema migration tests (existing)
```

### Test Fixture Architecture

```python
# conftest.py - Shared fixtures

@pytest.fixture
def runner():
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
    return data_dir

def create_mock_config(data_dir):
    """Create a mock config function for testing."""
    def mock_get_config(*args, **kwargs):
        return {
            "version": "1.0.0",
            "data_dir": str(data_dir),
            "verbose": False,
            "backup_enabled": False,
            "max_backups": 5,
        }
    return mock_get_config

def create_mock_data_dir(data_dir):
    """Create a mock data dir function for testing."""
    def mock_get_data_dir(config=None):
        return data_dir
    return mock_get_data_dir
```

### Mock Platform Handler

```python
# tests/mock_platform_handler.py

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple
from vince.platform.base import Platform, AppInfo, OperationResult, PlatformHandler

@dataclass
class MockPlatformHandler:
    """Mock platform handler for testing OS integration."""
    
    platform: Platform = Platform.MACOS
    _defaults: dict = None
    _calls: List[Tuple[str, dict]] = None
    _should_fail: bool = False
    _fail_extensions: set = None
    
    def __post_init__(self):
        self._defaults = {}
        self._calls = []
        self._fail_extensions = set()
    
    def set_default(
        self,
        extension: str,
        app_path: Path,
        dry_run: bool = False,
    ) -> OperationResult:
        self._calls.append(("set_default", {
            "extension": extension,
            "app_path": app_path,
            "dry_run": dry_run,
        }))
        
        if self._should_fail or extension in self._fail_extensions:
            return OperationResult(
                success=False,
                message=f"Mock failure for {extension}",
                error_code="VE605",
            )
        
        if not dry_run:
            previous = self._defaults.get(extension)
            self._defaults[extension] = str(app_path)
            return OperationResult(
                success=True,
                message=f"Set {extension} to {app_path}",
                previous_default=previous,
            )
        
        return OperationResult(
            success=True,
            message=f"Would set {extension} to {app_path}",
        )
    
    def remove_default(
        self,
        extension: str,
        dry_run: bool = False,
    ) -> OperationResult:
        self._calls.append(("remove_default", {
            "extension": extension,
            "dry_run": dry_run,
        }))
        
        if not dry_run:
            previous = self._defaults.pop(extension, None)
            return OperationResult(
                success=True,
                message=f"Removed default for {extension}",
                previous_default=previous,
            )
        
        return OperationResult(
            success=True,
            message=f"Would remove default for {extension}",
        )
    
    def get_current_default(self, extension: str) -> Optional[str]:
        self._calls.append(("get_current_default", {"extension": extension}))
        return self._defaults.get(extension)
    
    def verify_application(self, app_path: Path) -> AppInfo:
        self._calls.append(("verify_application", {"app_path": app_path}))
        return AppInfo(
            path=app_path,
            name=app_path.stem,
            bundle_id=f"com.test.{app_path.stem}",
        )
```

## Components and Interfaces

### Hypothesis Strategies

```python
# tests/strategies.py

from hypothesis import strategies as st
import string
from vince.validation.extension import SUPPORTED_EXTENSIONS
from vince.validation.offer_id import RESERVED_NAMES
from vince.state.default_state import VALID_TRANSITIONS, DefaultState
from vince.state.offer_state import VALID_TRANSITIONS as OFFER_VALID_TRANSITIONS, OfferState

# Extension strategies
@st.composite
def valid_extensions(draw):
    """Generate valid file extensions from the supported set."""
    return draw(st.sampled_from(list(SUPPORTED_EXTENSIONS)))

@st.composite
def unsupported_extensions(draw):
    """Generate extensions that match pattern but are not supported."""
    unsupported = [".exe", ".dll", ".so", ".bin", ".dat", ".log", ".tmp", ".bak"]
    return draw(st.sampled_from(unsupported))

# Offer ID strategies
@st.composite
def valid_offer_ids(draw):
    """Generate valid offer IDs matching the pattern ^[a-z][a-z0-9_-]{0,31}$."""
    first = draw(st.sampled_from(string.ascii_lowercase))
    rest_length = draw(st.integers(min_value=0, max_value=31))
    rest = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "_-",
        min_size=rest_length,
        max_size=rest_length,
    ))
    offer_id = first + rest
    if offer_id in RESERVED_NAMES:
        offer_id = f"custom-{offer_id}"
    return offer_id

@st.composite
def invalid_pattern_offer_ids(draw):
    """Generate offer IDs that don't match the required pattern."""
    strategies = [
        st.just("1abc"),      # Starts with number
        st.just("Abc"),       # Starts with uppercase
        st.just("_abc"),      # Starts with underscore
        st.just("-abc"),      # Starts with hyphen
        st.just(""),          # Empty string
        st.just("a" * 33),    # Too long (33 chars)
        st.just("abc def"),   # Contains space
        st.just("abc.def"),   # Contains dot
    ]
    return draw(st.one_of(*strategies))

# State transition strategies
@st.composite
def valid_default_transitions(draw):
    """Generate valid (current_state, target_state) pairs from VALID_TRANSITIONS."""
    valid_pairs = []
    for from_state, to_states in VALID_TRANSITIONS.items():
        for to_state in to_states:
            valid_pairs.append((from_state, to_state))
    return draw(st.sampled_from(valid_pairs))

@st.composite
def invalid_default_transitions(draw):
    """Generate invalid (current_state, target_state) pairs not in VALID_TRANSITIONS."""
    all_states = list(DefaultState)
    invalid_pairs = []
    for from_state in all_states:
        valid_targets = VALID_TRANSITIONS.get(from_state, set())
        for to_state in all_states:
            if to_state not in valid_targets:
                invalid_pairs.append((from_state, to_state))
    return draw(st.sampled_from(invalid_pairs))

@st.composite
def valid_offer_transitions(draw):
    """Generate valid (current_state, target_state) pairs from OFFER_VALID_TRANSITIONS."""
    valid_pairs = []
    for from_state, to_states in OFFER_VALID_TRANSITIONS.items():
        for to_state in to_states:
            valid_pairs.append((from_state, to_state))
    return draw(st.sampled_from(valid_pairs))

# Application path strategies
@st.composite
def valid_application_paths(draw):
    """Generate valid-looking application paths."""
    app_name = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "_-",
        min_size=1,
        max_size=20,
    ))
    return f"/usr/bin/{app_name}"

# Default entry strategies
@st.composite
def valid_default_entries(draw):
    """Generate valid default entry data."""
    ext = draw(valid_extensions())
    app_path = draw(valid_application_paths())
    state = draw(st.sampled_from(["pending", "active"]))
    return {
        "extension": ext,
        "application_path": app_path,
        "state": state,
    }

# Offer entry strategies
@st.composite
def valid_offer_entries(draw):
    """Generate valid offer entry data."""
    offer_id = draw(valid_offer_ids())
    default_id = f"def-md-{draw(st.integers(min_value=0, max_value=999)):03d}"
    state = draw(st.sampled_from(["created", "active"]))
    return {
        "offer_id": offer_id,
        "default_id": default_id,
        "state": state,
        "auto_created": draw(st.booleans()),
    }
```

## Data Models

### Test Data Structures

The tests use the existing data models from the vince CLI:

- **DefaultEntry**: `{id, extension, application_path, state, created_at, updated_at?, os_synced?}`
- **OfferEntry**: `{offer_id, default_id, state, auto_created, created_at, updated_at?}`
- **ConfigOptions**: `{version, data_dir, verbose, color_theme, backup_enabled, max_backups, confirm_destructive}`

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Invalid Offer ID Pattern Rejection

*For any* string that does not match the pattern `^[a-z][a-z0-9_-]{0,31}$` (starts with number, starts with uppercase, contains spaces, too long, etc.), validate_offer_id SHALL raise InvalidOfferIdError with code VE103.

**Validates: Requirements 1.6, 1.7, 1.8, 1.9, 1.10**

### Property 2: Reserved Name Rejection

*For any* reserved name in {help, version, list, all, none, default}, validate_offer_id SHALL raise InvalidOfferIdError with code VE103.

**Validates: Requirements 1.10**

### Property 3: Unsupported Extension Rejection

*For any* extension not in SUPPORTED_EXTENSIONS, validate_extension SHALL raise InvalidExtensionError with code VE102.

**Validates: Requirements 1.4**

### Property 4: Valid Default State Transitions

*For any* (current_state, target_state) pair in VALID_TRANSITIONS and any extension, validate_transition SHALL succeed without raising an exception.

**Validates: Requirements 6.1**

### Property 5: Invalid Default State Transitions

*For any* extension in SUPPORTED_EXTENSIONS:
- none→removed SHALL raise NoDefaultError (VE302)
- active→active SHALL raise DefaultExistsError (VE301)
- active→pending SHALL raise DefaultExistsError (VE301)
- pending→removed SHALL raise InvalidTransitionError
- removed→pending SHALL raise InvalidTransitionError
- removed→none SHALL raise InvalidTransitionError

**Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**

### Property 6: Valid Offer State Transitions

*For any* (current_state, target_state) pair in OFFER_VALID_TRANSITIONS and any valid offer_id, validate_transition SHALL succeed without raising an exception (when in_use=False).

**Validates: Requirements 7.1**

### Property 7: Invalid Offer State Transitions

*For any* valid offer_id:
- none→rejected SHALL raise OfferNotFoundError (VE104)
- created→created SHALL raise OfferExistsError (VE303)
- active→created SHALL raise OfferExistsError (VE303)
- active→rejected with in_use=True SHALL raise OfferInUseError (VE304)
- rejected→any SHALL raise InvalidOfferTransitionError (terminal state)
- none→active SHALL raise InvalidOfferTransitionError

**Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.7, 7.8**

### Property 8: Dry Run State Preservation

*For any* command supporting -dry flag (slap, chop, set, forget, sync) and any valid inputs, executing with -dry flag SHALL NOT modify defaults.json or offers.json.

**Validates: Requirements 8.4, 9.4, 10.3, 11.3, 15.5, 16.1, 16.2**

### Property 9: Dry Run Idempotence

*For any* command supporting -dry flag and any valid inputs, executing dry run twice SHALL produce identical output.

**Validates: Requirements 16.3**

### Property 10: Commands Work for All Extensions

*For any* extension in SUPPORTED_EXTENSIONS and valid application path, slap, chop, set, forget, and offer commands SHALL work correctly.

**Validates: Requirements 8.7, 9.6, 10.5, 11.5, 12.5**

### Property 11: Persistence Round-Trip Consistency

*For any* valid DefaultEntry, saving to DefaultsStore then loading SHALL return equivalent data. *For any* valid OfferEntry, saving to OffersStore then loading SHALL return equivalent data.

**Validates: Requirements 17.1, 17.2, 17.3, 17.4**

### Property 12: Backup Retention Limit

*For any* combination of num_writes (1-10) and max_backups (1-5), the backup count SHALL never exceed max_backups.

**Validates: Requirements 18.1**

### Property 13: Backup Rotation Order

*For any* backup operation when limit is exceeded, the oldest backup SHALL be deleted first.

**Validates: Requirements 18.2**

### Property 14: Backup Disabled Behavior

*For any* write operation when backup_enabled=False, no backup files SHALL be created.

**Validates: Requirements 18.3**

### Property 15: Error Class Completeness

*For any* VinceError subclass, it SHALL have code, message, and recovery attributes. The code SHALL follow the VE### format and fall within the correct category range.

**Validates: Requirements 22.1, 22.2, 22.3, 22.4**

### Property 16: Verbose Flag Controls Output

*For any* command supporting -vb flag, additional output SHALL be produced when flag is set, and no verbose output SHALL appear when flag is not set.

**Validates: Requirements 23.1, 23.2**

### Property 17: State Persistence Across Commands

*For any* command that modifies state, subsequent commands SHALL see the updated state.

**Validates: Requirements 19.7**

### Property 18: Valid Extension Validation

*For any* extension in SUPPORTED_EXTENSIONS, validate_extension SHALL return the extension unchanged.

**Validates: Requirements 21.2**

### Property 19: Valid Offer ID Validation

*For any* offer_id matching pattern `^[a-z][a-z0-9_-]{0,31}$` and not in RESERVED_NAMES, validate_offer_id SHALL return the offer_id unchanged.

**Validates: Requirements 21.4**

### Property 20: List Extension Filtering

*For any* extension filter (--md, --py, etc.) applied to list command, only entries matching that extension SHALL be displayed.

**Validates: Requirements 14.7**

### Property 21: Schema Migration Data Preservation

*For any* valid data file undergoing schema migration, all existing data SHALL be preserved.

**Validates: Requirements 24.4**

## Error Handling

### Error Test Coverage Matrix

| Error Code | Class | Test File | Test Method |
|------------|-------|-----------|-------------|
| VE101 | InvalidPathError | test_input_error_coverage.py | test_nonexistent_path_* |
| VE102 | InvalidExtensionError | test_input_error_coverage.py | test_unsupported_extension_* |
| VE103 | InvalidOfferIdError | test_input_error_coverage.py | test_invalid_offer_id_* |
| VE104 | OfferNotFoundError | test_input_error_coverage.py | test_offer_not_found_* |
| VE105 | InvalidSubsectionError | test_input_error_coverage.py | test_invalid_subsection_* |
| VE201 | VinceFileNotFoundError | test_file_error_coverage.py | test_file_not_found_* |
| VE202 | PermissionDeniedError | test_file_error_coverage.py | test_permission_denied_* |
| VE203 | DataCorruptedError | test_file_error_coverage.py | test_data_corrupted_* |
| VE301 | DefaultExistsError | test_state_error_coverage.py | test_default_exists_* |
| VE302 | NoDefaultError | test_state_error_coverage.py | test_no_default_* |
| VE303 | OfferExistsError | test_state_error_coverage.py | test_offer_exists_* |
| VE304 | OfferInUseError | test_state_error_coverage.py | test_offer_in_use_* |
| VE401 | InvalidConfigOptionError | test_config_error_coverage.py | test_invalid_config_* |
| VE402 | ConfigMalformedError | test_config_error_coverage.py | test_config_malformed_* |
| VE501 | UnexpectedError | test_errors.py | test_unexpected_error_* |
| VE601 | UnsupportedPlatformError | test_os_error_coverage.py | test_unsupported_platform_* |
| VE602 | BundleIdNotFoundError | test_os_error_coverage.py | test_bundle_id_not_found_* |
| VE603 | RegistryAccessError | test_os_error_coverage.py | test_registry_access_* |
| VE604 | ApplicationNotFoundError | test_os_error_coverage.py | test_application_not_found_* |
| VE605 | OSOperationError | test_os_error_coverage.py | test_os_operation_* |
| VE606 | SyncPartialError | test_os_error_coverage.py | test_sync_partial_* |

## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs using Hypothesis

Both are complementary and necessary for comprehensive coverage.

### Property-Based Testing Configuration

- **Framework**: Hypothesis
- **Minimum iterations**: 100 per property test
- **Tag format**: `Feature: cli-comprehensive-testing, Property {number}: {property_text}`

### Test Configuration

```python
# pytest.ini or pyproject.toml
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

### Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Commands | 90% | ~90% |
| Persistence | 95% | ~95% |
| Validation | 95% | ~95% |
| State Machine | 100% | 100% |
| Error Handling | 90% | ~85% |
| Configuration | 85% | ~85% |
| **Overall** | **85%** | **85.31%** |

### Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vince --cov-report=html

# Run specific test file
pytest tests/test_input_error_coverage.py

# Run property tests only
pytest -k "property"

# Run with verbose output
pytest -v
```

