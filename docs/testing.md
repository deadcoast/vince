# Testing Patterns Documentation

This document provides comprehensive testing patterns and guidelines for the vince CLI application. It covers test fixtures, mocking strategies, property-based testing generators, integration testing, and coverage requirements.

> [!NOTE]
> For definition tables and the Single Source of Truth, see [tables.md](tables.md).

## Overview

The vince CLI testing strategy employs a dual approach combining unit tests and property-based tests to ensure comprehensive coverage and correctness.

### Testing Philosophy

| Approach | Purpose | Framework |
| --- | --- | --- |
| Unit Tests | Verify specific examples and edge cases | pytest |
| Property-Based Tests | Verify universal properties across all inputs | Hypothesis |
| Integration Tests | Verify end-to-end command flows | pytest + CliRunner |

### Test Organization

```text
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_commands.py         # Command unit tests
├── test_validators.py       # Validation property tests
├── test_persistence.py      # File I/O tests
├── test_integration.py      # End-to-end tests
└── generators/
    └── __init__.py          # Hypothesis strategies
```


## Fixtures

Test fixtures provide reusable setup and teardown logic for consistent test environments.

### CLI Test Fixture

The CLI test fixture provides an isolated environment for testing Typer commands:

```python
import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def cli_runner():
    """Provide a Typer CLI test runner."""
    return CliRunner()

@pytest.fixture
def app():
    """Provide the vince Typer application instance."""
    from vince.main import app
    return app

@pytest.fixture
def isolated_cli(cli_runner, app, tmp_path):
    """Provide CLI runner with isolated data directory."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()
    
    # Initialize empty data files
    (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    (data_dir / "config.json").write_text('{"version": "1.0.0"}')
    
    class IsolatedCLI:
        def __init__(self):
            self.runner = cli_runner
            self.app = app
            self.data_dir = data_dir
        
        def invoke(self, *args, **kwargs):
            return self.runner.invoke(self.app, *args, env={"VINCE_DATA_DIR": str(data_dir)}, **kwargs)
    
    return IsolatedCLI()
```

### Data File Fixtures

Fixtures for creating and managing test data files:

```python
import pytest
import json
from datetime import datetime

@pytest.fixture
def sample_defaults():
    """Provide sample defaults data."""
    return {
        "version": "1.0.0",
        "defaults": [
            {
                "id": "def-md-vscode-001",
                "extension": ".md",
                "application_path": "/usr/bin/code",
                "application_name": "Visual Studio Code",
                "state": "active",
                "created_at": "2024-01-15T10:30:00Z"
            }
        ]
    }

@pytest.fixture
def sample_offers():
    """Provide sample offers data."""
    return {
        "version": "1.0.0",
        "offers": [
            {
                "offer_id": "code-md",
                "default_id": "def-md-vscode-001",
                "state": "active",
                "auto_created": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        ]
    }

@pytest.fixture
def populated_data_dir(tmp_path, sample_defaults, sample_offers):
    """Provide a data directory with pre-populated test data."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()
    
    (data_dir / "defaults.json").write_text(json.dumps(sample_defaults, indent=2))
    (data_dir / "offers.json").write_text(json.dumps(sample_offers, indent=2))
    (data_dir / "config.json").write_text('{"version": "1.0.0"}')
    
    return data_dir

@pytest.fixture
def mock_executable(tmp_path):
    """Create a mock executable file for testing."""
    exe_path = tmp_path / "mock_app"
    exe_path.write_text("#!/bin/bash\necho 'mock'")
    exe_path.chmod(0o755)
    return exe_path
```

### Temporary Directory Fixture

```python
@pytest.fixture
def clean_data_dir(tmp_path):
    """Provide a clean temporary data directory."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()
    (data_dir / "backups").mkdir()
    return data_dir
```


## Mocks

Mock patterns for isolating tests from external dependencies.

### File System Mocking

Mock file system operations to test without actual file I/O:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

@pytest.fixture
def mock_filesystem():
    """Mock file system operations."""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.is_file') as mock_is_file, \
         patch('pathlib.Path.read_text') as mock_read, \
         patch('pathlib.Path.write_text') as mock_write:
        
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        yield {
            'exists': mock_exists,
            'is_file': mock_is_file,
            'read_text': mock_read,
            'write_text': mock_write
        }

def test_file_not_found_error(mock_filesystem):
    """Test error handling when file does not exist."""
    mock_filesystem['exists'].return_value = False
    
    # Test code that should raise VE201
    ...
```

### Atomic Write Mocking

Mock atomic write operations for testing persistence:

```python
@pytest.fixture
def mock_atomic_write():
    """Mock atomic write operations."""
    written_data = {}
    
    def capture_write(path, data):
        written_data[str(path)] = data
    
    with patch('vince.persistence.atomic_write', side_effect=capture_write):
        yield written_data

def test_data_persistence(mock_atomic_write):
    """Test that data is written correctly."""
    # Perform operation that writes data
    ...
    
    # Verify written data
    assert "defaults.json" in str(list(mock_atomic_write.keys())[0])
```

### Config Mocking

Mock configuration loading for testing different config scenarios:

```python
@pytest.fixture
def mock_config():
    """Mock configuration with customizable values."""
    default_config = {
        "version": "1.0.0",
        "data_dir": "~/.vince",
        "verbose": False,
        "color_theme": "default",
        "backup_enabled": True,
        "max_backups": 5,
        "confirm_destructive": True
    }
    
    class ConfigMock:
        def __init__(self):
            self.config = default_config.copy()
        
        def set(self, key, value):
            self.config[key] = value
        
        def get(self, key, default=None):
            return self.config.get(key, default)
    
    return ConfigMock()

@pytest.fixture
def verbose_config(mock_config):
    """Config with verbose mode enabled."""
    mock_config.set("verbose", True)
    return mock_config

@pytest.fixture
def no_backup_config(mock_config):
    """Config with backups disabled."""
    mock_config.set("backup_enabled", False)
    return mock_config
```

### Console Output Mocking

Mock Rich console output for testing CLI messages:

```python
from io import StringIO
from rich.console import Console

@pytest.fixture
def capture_console():
    """Capture Rich console output."""
    output = StringIO()
    console = Console(file=output, force_terminal=True)
    
    class ConsoleCapturer:
        def __init__(self):
            self.console = console
            self.output = output
        
        def get_output(self):
            return self.output.getvalue()
        
        def contains(self, text):
            return text in self.get_output()
    
    return ConsoleCapturer()
```


## Generators

Hypothesis strategies for generating test data in property-based tests.

### Path Strategies

Generate valid and invalid file paths for testing:

```python
from hypothesis import strategies as st
from pathlib import Path
import string

# Valid path characters (excluding problematic ones)
PATH_CHARS = string.ascii_letters + string.digits + "_-."

@st.composite
def valid_paths(draw):
    """Generate valid file paths."""
    # Generate path components
    num_parts = draw(st.integers(min_value=1, max_value=4))
    parts = []
    
    for _ in range(num_parts):
        part = draw(st.text(
            alphabet=PATH_CHARS,
            min_size=1,
            max_size=20
        ))
        if part:  # Ensure non-empty
            parts.append(part)
    
    if not parts:
        parts = ["default"]
    
    # Build path
    path_str = "/tmp/" + "/".join(parts)
    return Path(path_str)

@st.composite
def executable_paths(draw):
    """Generate paths that look like executables."""
    base_dirs = ["/usr/bin", "/usr/local/bin", "/opt", "/Applications"]
    base = draw(st.sampled_from(base_dirs))
    
    name = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "-_",
        min_size=1,
        max_size=20
    ))
    
    return Path(base) / (name or "app")

@st.composite
def invalid_paths(draw):
    """Generate invalid file paths (with illegal characters)."""
    # Include characters that are invalid in paths
    invalid_chars = '\x00\n\r'
    name = draw(st.text(min_size=1, max_size=10))
    invalid_char = draw(st.sampled_from(list(invalid_chars)))
    
    return f"/tmp/{name}{invalid_char}file"
```

### Extension Strategies

Generate valid and invalid file extensions:

```python
# Supported extensions from the vince CLI
SUPPORTED_EXTENSIONS = [
    ".md", ".py", ".txt", ".js", ".html", ".css",
    ".json", ".yml", ".yaml", ".xml", ".csv", ".sql"
]

@st.composite
def valid_extensions(draw):
    """Generate valid file extensions."""
    return draw(st.sampled_from(SUPPORTED_EXTENSIONS))

@st.composite
def extension_flags(draw):
    """Generate extension flags as used in CLI (--md, --py, etc.)."""
    ext = draw(st.sampled_from(SUPPORTED_EXTENSIONS))
    return f"--{ext[1:]}"  # Remove dot, add dashes

@st.composite
def invalid_extensions(draw):
    """Generate invalid file extensions."""
    strategies = [
        st.just("md"),           # Missing dot
        st.just("..md"),         # Double dot
        st.just(".MD"),          # Uppercase
        st.just(".m d"),         # Space in extension
        st.just(".123"),         # Starts with number
        st.text(min_size=1, max_size=5).map(lambda x: f".{x.upper()}")  # Random uppercase
    ]
    return draw(st.one_of(*strategies))

@st.composite
def any_extension(draw):
    """Generate any extension matching the pattern ^\\.[a-z0-9]+$."""
    chars = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits,
        min_size=1,
        max_size=10
    ))
    return f".{chars}" if chars else ".txt"
```

### Offer ID Strategies

Generate valid and invalid offer identifiers:

```python
# Reserved offer names that cannot be used
RESERVED_OFFER_NAMES = ["help", "version", "list", "all", "none", "default"]

@st.composite
def valid_offer_ids(draw):
    """Generate valid offer IDs matching pattern ^[a-z][a-z0-9_-]{0,31}$."""
    # First character must be lowercase letter
    first_char = draw(st.sampled_from(string.ascii_lowercase))
    
    # Remaining characters: lowercase, digits, underscore, hyphen
    remaining_chars = string.ascii_lowercase + string.digits + "_-"
    rest_length = draw(st.integers(min_value=0, max_value=31))
    rest = draw(st.text(alphabet=remaining_chars, min_size=rest_length, max_size=rest_length))
    
    offer_id = first_char + rest
    
    # Ensure not reserved
    if offer_id in RESERVED_OFFER_NAMES:
        offer_id = f"custom-{offer_id}"
    
    return offer_id

@st.composite
def invalid_offer_ids(draw):
    """Generate invalid offer IDs."""
    strategies = [
        # Starts with number
        st.text(alphabet=string.digits, min_size=1, max_size=1).map(lambda x: x + "offer"),
        # Starts with uppercase
        st.text(alphabet=string.ascii_uppercase, min_size=1, max_size=1).map(lambda x: x + "offer"),
        # Contains invalid characters
        st.just("offer@name"),
        st.just("offer name"),
        st.just("offer.name"),
        # Too long (> 32 chars)
        st.just("a" * 33),
        # Empty
        st.just(""),
        # Reserved names
        st.sampled_from(RESERVED_OFFER_NAMES)
    ]
    return draw(st.one_of(*strategies))

@st.composite
def offer_entries(draw):
    """Generate complete offer entry objects."""
    from datetime import datetime, timezone
    
    offer_id = draw(valid_offer_ids())
    default_id = f"def-{draw(valid_extensions())[1:]}-{draw(st.integers(min_value=1, max_value=999)):03d}"
    state = draw(st.sampled_from(["created", "active", "rejected"]))
    auto_created = draw(st.booleans())
    created_at = datetime.now(timezone.utc).isoformat()
    
    return {
        "offer_id": offer_id,
        "default_id": default_id,
        "state": state,
        "auto_created": auto_created,
        "created_at": created_at
    }
```

### Default Entry Strategies

```python
@st.composite
def default_entries(draw):
    """Generate complete default entry objects."""
    from datetime import datetime, timezone
    
    ext = draw(valid_extensions())
    path = draw(executable_paths())
    state = draw(st.sampled_from(["pending", "active", "removed"]))
    created_at = datetime.now(timezone.utc).isoformat()
    
    entry_id = f"def-{ext[1:]}-app-{draw(st.integers(min_value=1, max_value=999)):03d}"
    
    return {
        "id": entry_id,
        "extension": ext,
        "application_path": str(path),
        "state": state,
        "created_at": created_at
    }
```


## Integration

End-to-end integration test patterns for testing complete command flows.

### End-to-End Test Setup

```python
import pytest
from typer.testing import CliRunner
from pathlib import Path
import json
import os

class IntegrationTestBase:
    """Base class for integration tests with common setup."""
    
    @pytest.fixture(autouse=True)
    def setup_integration(self, tmp_path):
        """Set up isolated environment for each test."""
        self.data_dir = tmp_path / ".vince"
        self.data_dir.mkdir()
        (self.data_dir / "backups").mkdir()
        
        # Initialize empty data files
        self._init_data_files()
        
        # Create mock executable
        self.mock_app = tmp_path / "mock_app"
        self.mock_app.write_text("#!/bin/bash\necho 'mock'")
        self.mock_app.chmod(0o755)
        
        # Set environment
        self.env = {"VINCE_DATA_DIR": str(self.data_dir)}
        
        # CLI runner
        self.runner = CliRunner()
        
        yield
        
        # Cleanup is automatic with tmp_path
    
    def _init_data_files(self):
        """Initialize empty data files."""
        (self.data_dir / "defaults.json").write_text(
            '{"version": "1.0.0", "defaults": []}'
        )
        (self.data_dir / "offers.json").write_text(
            '{"version": "1.0.0", "offers": []}'
        )
        (self.data_dir / "config.json").write_text(
            '{"version": "1.0.0"}'
        )
    
    def invoke(self, *args):
        """Invoke CLI command with isolated environment."""
        from vince.main import app
        return self.runner.invoke(app, args, env=self.env)
    
    def read_defaults(self):
        """Read current defaults data."""
        return json.loads((self.data_dir / "defaults.json").read_text())
    
    def read_offers(self):
        """Read current offers data."""
        return json.loads((self.data_dir / "offers.json").read_text())
```

### Complete Flow Test Example

```python
class TestSlapChopFlow(IntegrationTestBase):
    """Test complete slap -> chop workflow."""
    
    def test_slap_creates_default_and_chop_removes(self):
        """Test that slap creates a default and chop removes it."""
        # Step 1: Slap to create default
        result = self.invoke("slap", str(self.mock_app), "-set", "--md")
        assert result.exit_code == 0
        
        # Verify default was created
        defaults = self.read_defaults()
        assert len(defaults["defaults"]) == 1
        assert defaults["defaults"][0]["extension"] == ".md"
        assert defaults["defaults"][0]["state"] == "active"
        
        # Step 2: Chop to remove default
        result = self.invoke("chop", "--md", "-forget")
        assert result.exit_code == 0
        
        # Verify default was removed
        defaults = self.read_defaults()
        removed = [d for d in defaults["defaults"] if d["state"] == "removed"]
        assert len(removed) == 1
```

### Cleanup Procedures

```python
@pytest.fixture
def cleanup_after_test(tmp_path):
    """Ensure cleanup after test completion."""
    yield tmp_path
    
    # Force cleanup of any remaining files
    import shutil
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)

def cleanup_data_files(data_dir: Path):
    """Reset data files to initial state."""
    (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')

def cleanup_backups(data_dir: Path):
    """Remove all backup files."""
    backup_dir = data_dir / "backups"
    if backup_dir.exists():
        for backup_file in backup_dir.glob("*.bak"):
            backup_file.unlink()
```

### State Verification Helpers

```python
def assert_default_exists(data_dir: Path, extension: str, state: str = None):
    """Assert that a default exists for the given extension."""
    defaults = json.loads((data_dir / "defaults.json").read_text())
    matching = [d for d in defaults["defaults"] if d["extension"] == extension]
    assert len(matching) > 0, f"No default found for {extension}"
    if state:
        assert matching[0]["state"] == state, f"Expected state {state}, got {matching[0]['state']}"

def assert_offer_exists(data_dir: Path, offer_id: str, state: str = None):
    """Assert that an offer exists with the given ID."""
    offers = json.loads((data_dir / "offers.json").read_text())
    matching = [o for o in offers["offers"] if o["offer_id"] == offer_id]
    assert len(matching) > 0, f"No offer found with id {offer_id}"
    if state:
        assert matching[0]["state"] == state, f"Expected state {state}, got {matching[0]['state']}"

def assert_no_default(data_dir: Path, extension: str):
    """Assert that no active default exists for the given extension."""
    defaults = json.loads((data_dir / "defaults.json").read_text())
    active = [d for d in defaults["defaults"] 
              if d["extension"] == extension and d["state"] == "active"]
    assert len(active) == 0, f"Active default found for {extension}"
```


## Coverage

Test coverage requirements and targets for the vince CLI.

### Coverage Targets by Component

| Component | Target | Critical Paths |
| --- | --- | --- |
| Commands (slap, chop, etc.) | 90% | All command entry points |
| Persistence Layer | 95% | atomic_write, backup, restore |
| Validation | 95% | Path, extension, offer_id validation |
| State Machine | 100% | All state transitions |
| Error Handling | 90% | All VE### error codes |
| Configuration | 85% | Config loading, merging, validation |

### Critical Path Coverage

The following paths must have 100% test coverage:

| Path | Description | Tests Required |
| --- | --- | --- |
| Default Creation | slap/set → defaults.json write | Unit + Integration |
| Default Removal | chop/forget → state transition | Unit + Integration |
| Offer Creation | offer → offers.json write | Unit + Integration |
| Offer Rejection | reject → state transition | Unit + Integration |
| Atomic Write | temp file → rename | Unit + Error cases |
| Backup Creation | pre-write backup | Unit + Rotation |
| Config Loading | hierarchy merge | Unit + Precedence |

### Coverage Configuration

```ini
# pytest.ini or pyproject.toml
[tool.coverage.run]
source = ["vince"]
branch = true
omit = [
    "tests/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
fail_under = 85
show_missing = true
```

### Running Coverage

```sh
# Run tests with coverage
pytest --cov=vince --cov-report=html --cov-report=term-missing

# Check coverage threshold
pytest --cov=vince --cov-fail-under=85

# Generate detailed HTML report
pytest --cov=vince --cov-report=html:coverage_html
```

### Property Test Coverage

Property-based tests should cover:

| Property | Min Examples | Coverage Target |
| --- | --- | --- |
| Path validation | 100 | All valid/invalid patterns |
| Extension validation | 100 | All supported + invalid |
| Offer ID validation | 100 | Pattern + reserved names |
| State transitions | 100 | All valid + invalid transitions |
| Round-trip persistence | 100 | Serialize → deserialize |


## Examples

Example test cases for each vince CLI command.

### slap Command Tests

```python
import pytest
from typer.testing import CliRunner
from hypothesis import given, settings
from hypothesis import strategies as st

class TestSlapCommand:
    """Test cases for the slap command."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_slap_with_valid_path_and_extension(self, runner, mock_executable, isolated_data_dir):
        """Test slap with valid arguments creates a default."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["slap", str(mock_executable), "--md"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code == 0
        assert "default" in result.output.lower() or "set" in result.output.lower()
    
    def test_slap_with_set_flag_activates_default(self, runner, mock_executable, isolated_data_dir):
        """Test slap -set creates an active default."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["slap", str(mock_executable), "-set", "--md"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code == 0
        
        # Verify state is active
        import json
        defaults = json.loads((isolated_data_dir / "defaults.json").read_text())
        active = [d for d in defaults["defaults"] if d["state"] == "active"]
        assert len(active) == 1
    
    def test_slap_with_nonexistent_path_fails(self, runner, isolated_data_dir):
        """Test slap with nonexistent path returns VE101."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["slap", "/nonexistent/path", "--md"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code != 0
        assert "VE101" in result.output or "does not exist" in result.output.lower()
    
    def test_slap_verbose_output(self, runner, mock_executable, isolated_data_dir):
        """Test slap -vb provides verbose output."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["slap", str(mock_executable), "--md", "-vb"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code == 0
        # Verbose output should contain more details
        assert len(result.output) > 0
```

### chop Command Tests

```python
class TestChopCommand:
    """Test cases for the chop command."""
    
    def test_chop_removes_existing_default(self, runner, populated_data_dir):
        """Test chop removes an existing default."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["chop", "--md", "-forget"],
            env={"VINCE_DATA_DIR": str(populated_data_dir)}
        )
        
        assert result.exit_code == 0
    
    def test_chop_nonexistent_extension_fails(self, runner, isolated_data_dir):
        """Test chop on nonexistent extension returns VE302."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["chop", "--md", "-forget"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code != 0
        assert "VE302" in result.output or "no default" in result.output.lower()
    
    def test_chop_invalid_extension_fails(self, runner, isolated_data_dir):
        """Test chop with invalid extension returns VE102."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["chop", "--xyz"],  # Unsupported extension
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        # Should fail with invalid extension error
        assert result.exit_code != 0
```

### set/forget Command Tests

```python
class TestSetForgetCommands:
    """Test cases for set and forget commands."""
    
    def test_set_creates_active_default(self, runner, mock_executable, isolated_data_dir):
        """Test set creates an active default directly."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["set", str(mock_executable), "--py"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code == 0
        
        import json
        defaults = json.loads((isolated_data_dir / "defaults.json").read_text())
        py_defaults = [d for d in defaults["defaults"] if d["extension"] == ".py"]
        assert len(py_defaults) == 1
    
    def test_forget_removes_default(self, runner, populated_data_dir):
        """Test forget removes an existing default."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["forget", "--md"],
            env={"VINCE_DATA_DIR": str(populated_data_dir)}
        )
        
        assert result.exit_code == 0
    
    def test_forget_nonexistent_fails(self, runner, isolated_data_dir):
        """Test forget on nonexistent default returns VE302."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["forget", "--py"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code != 0
```

### offer/reject Command Tests

```python
class TestOfferRejectCommands:
    """Test cases for offer and reject commands."""
    
    def test_offer_creates_new_offer(self, runner, mock_executable, isolated_data_dir):
        """Test offer creates a new offer entry."""
        from vince.main import app
        
        # First create a default
        runner.invoke(
            app,
            ["set", str(mock_executable), "--md"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        # Then create an offer
        result = runner.invoke(
            app,
            ["offer", "my-code", str(mock_executable), "--md"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code == 0
        
        import json
        offers = json.loads((isolated_data_dir / "offers.json").read_text())
        assert any(o["offer_id"] == "my-code" for o in offers["offers"])
    
    def test_offer_invalid_id_fails(self, runner, mock_executable, isolated_data_dir):
        """Test offer with invalid ID returns VE103."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["offer", "Invalid-ID", str(mock_executable), "--md"],  # Uppercase
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code != 0
        assert "VE103" in result.output or "pattern" in result.output.lower()
    
    def test_offer_reserved_name_fails(self, runner, mock_executable, isolated_data_dir):
        """Test offer with reserved name returns VE103."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["offer", "help", str(mock_executable), "--md"],  # Reserved
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code != 0
    
    def test_reject_removes_offer(self, runner, populated_data_dir):
        """Test reject removes an existing offer."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["reject", "code-md"],  # From sample_offers fixture
            env={"VINCE_DATA_DIR": str(populated_data_dir)}
        )
        
        assert result.exit_code == 0
    
    def test_reject_nonexistent_fails(self, runner, isolated_data_dir):
        """Test reject on nonexistent offer returns VE104."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["reject", "nonexistent"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code != 0
        assert "VE104" in result.output or "not found" in result.output.lower()
    
    def test_reject_complete_delete(self, runner, populated_data_dir):
        """Test reject with complete-delete flag."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["reject", "code-md", "."],  # Complete delete
            env={"VINCE_DATA_DIR": str(populated_data_dir)}
        )
        
        assert result.exit_code == 0
```

### list Command Tests

```python
class TestListCommand:
    """Test cases for the list command."""
    
    def test_list_all_shows_everything(self, runner, populated_data_dir):
        """Test list -all shows all tracked items."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["list", "-all"],
            env={"VINCE_DATA_DIR": str(populated_data_dir)}
        )
        
        assert result.exit_code == 0
        # Should contain table output
        assert len(result.output) > 0
    
    def test_list_defaults_only(self, runner, populated_data_dir):
        """Test list -def shows only defaults."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["list", "-def"],
            env={"VINCE_DATA_DIR": str(populated_data_dir)}
        )
        
        assert result.exit_code == 0
    
    def test_list_offers_only(self, runner, populated_data_dir):
        """Test list -off shows only offers."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["list", "-off"],
            env={"VINCE_DATA_DIR": str(populated_data_dir)}
        )
        
        assert result.exit_code == 0
    
    def test_list_filter_by_extension(self, runner, populated_data_dir):
        """Test list with extension filter."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["list", "-def", "--md"],
            env={"VINCE_DATA_DIR": str(populated_data_dir)}
        )
        
        assert result.exit_code == 0
    
    def test_list_invalid_subsection_fails(self, runner, isolated_data_dir):
        """Test list with invalid subsection returns VE105."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["list", "-invalid"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code != 0
        assert "VE105" in result.output or "invalid" in result.output.lower()
    
    def test_list_empty_data(self, runner, isolated_data_dir):
        """Test list with no data shows empty state."""
        from vince.main import app
        
        result = runner.invoke(
            app,
            ["list", "-all"],
            env={"VINCE_DATA_DIR": str(isolated_data_dir)}
        )
        
        assert result.exit_code == 0
        # Should handle empty state gracefully
```

## Cross-References

- See [api.md](api.md) for command interface specifications
- See [errors.md](errors.md) for error code documentation
- See [states.md](states.md) for state machine documentation
- See [schemas.md](schemas.md) for data model schemas
