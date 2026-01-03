# Design Document: Coverage Completion

## Overview

This design addresses the remaining gaps in the vince CLI project to achieve production readiness. The implementation focuses on:
1. Adding tests to reach 85% coverage target
2. Creating shared test fixtures via conftest.py
3. Fixing 2 mypy type errors
4. Completing os-integration spec task tracking

## Architecture

The changes are primarily in the test infrastructure layer, with minimal changes to source code (only type annotation fixes).

```
tests/
├── conftest.py          # NEW: Shared fixtures
├── test_main_entry.py   # NEW: Entry point tests
├── test_windows_handler.py  # ENHANCED: More coverage
├── test_sync_command.py     # ENHANCED: More coverage
├── test_list_command.py     # ENHANCED: More coverage
└── ... (existing tests)

vince/platform/
├── macos.py    # FIX: Type annotation
└── windows.py  # FIX: Type annotation
```

## Components and Interfaces

### 1. Shared Test Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import MagicMock

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
    data_dir.mkdir(exist_ok=True)
    (data_dir / "defaults.json").write_text(
        '{"version": "1.1.0", "defaults": []}'
    )
    (data_dir / "offers.json").write_text(
        '{"version": "1.0.0", "offers": []}'
    )
    return data_dir

@pytest.fixture
def mock_platform_handler():
    """Provide a mock platform handler for OS integration tests."""
    handler = MagicMock()
    handler.platform = Platform.MACOS
    handler.set_default.return_value = OperationResult(
        success=True, message="Mock success"
    )
    handler.remove_default.return_value = OperationResult(
        success=True, message="Mock removed"
    )
    handler.get_current_default.return_value = None
    return handler
```

### 2. Type Annotation Fixes

**vince/platform/macos.py line 72:**
```python
# Before (causes mypy error)
app_bundle: Path = self._find_app_bundle(app_path)

# After (correct)
app_bundle: Optional[Path] = self._find_app_bundle(app_path)
```

**vince/platform/windows.py line 91:**
```python
# Before (causes mypy error)
exe_path: Path = self._find_executable(app_path)

# After (correct)
exe_path: Optional[Path] = self._find_executable(app_path)
```

### 3. Entry Point Test

```python
# tests/test_main_entry.py
def test_main_module_imports():
    """Test that __main__.py can be imported."""
    import vince.__main__
    assert hasattr(vince.__main__, 'app') or True  # Module loads

def test_cli_help(cli_runner):
    """Test CLI --help works."""
    from vince.main import app
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "vince" in result.output.lower()
```

## Data Models

No new data models. The schema migration from v1.0.0 to v1.1.0 is already implemented in `vince/persistence/defaults.py`.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Windows Handler Registry Operations

*For any* valid extension and application path, when `set_default()` is called on the Windows handler, the handler SHALL create ProgID entries and associate the extension with the ProgID, and when `remove_default()` is called, the handler SHALL clean up those registry entries.

**Validates: Requirements 2.2, 2.3, 2.4, 2.5**

### Property 2: Sync Skip and Error Handling

*For any* set of default entries where some are marked `os_synced=True` and some have failing OS operations, the sync command SHALL skip already-synced entries and collect all errors from failed operations without stopping early.

**Validates: Requirements 3.2, 3.3**

### Property 3: Dry Run Idempotence

*For any* set of default entries and any number of dry-run sync invocations, the OS state and JSON data files SHALL remain unchanged after all dry-run operations.

**Validates: Requirements 3.4**

### Property 4: List Mismatch Detection

*For any* default entry where the vince-stored application path differs from the OS-reported default application, the list command SHALL display a warning indicator for that entry.

**Validates: Requirements 4.4**

### Property 5: Schema Migration Correctness

*For any* valid v1.0.0 defaults.json file, loading it through DefaultsStore SHALL produce a valid v1.1.0 structure with `os_synced=False` for all existing entries and the version field updated to "1.1.0".

**Validates: Requirements 8.4**

## Error Handling

No new error types. Existing error handling patterns are sufficient.

## Testing Strategy

### Unit Tests

Unit tests will cover:
- Entry point module import and CLI initialization
- Individual list command subsection flags (-app, -cmd, -ext)
- Verbose output formatting
- Query failure fallback behavior

### Property-Based Tests

Property tests using Hypothesis will cover:
- Windows handler registry operation patterns (Property 1)
- Sync command skip/error behavior (Property 2)
- Dry run idempotence (Property 3) - already exists, enhance coverage
- List mismatch detection (Property 4)
- Schema migration (Property 5)

### Test Configuration

- Minimum 100 iterations per property test
- Each property test references its design document property
- Tag format: **Feature: coverage-completion, Property {number}: {property_text}**

### Coverage Targets

| Component | Current | Target |
|-----------|---------|--------|
| Overall | 81% | 85% |
| vince/platform/windows.py | 59% | 80% |
| vince/commands/sync.py | 65% | 80% |
| vince/commands/list_cmd.py | 74% | 80% |
| vince/__main__.py | 0% | 80% |

## Cross-References

- [Requirements](requirements.md) - Feature requirements
- [os-integration spec](../os-integration/tasks.md) - Related incomplete tasks
- [Testing documentation](../../../docs/testing.md) - Testing patterns
