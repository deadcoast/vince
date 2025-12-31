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
├── test_chop_command.py         # Chop command tests
├── test_config.py               # Configuration tests
├── test_cross_references.py     # Cross-reference validation tests
├── test_doc_code_sync.py        # Documentation-code sync tests
├── test_errors.py               # Error handling tests
├── test_forget_command.py       # Forget command tests
├── test_import_usage.py         # Import usage tests
├── test_integration.py          # End-to-end integration tests
├── test_list_command.py         # List command tests
├── test_offer_command.py        # Offer command tests
├── test_pattern_usage.py        # Pattern usage tests
├── test_persistence.py          # Persistence layer tests
├── test_reject_command.py       # Reject command tests
├── test_schema_accuracy.py      # Schema accuracy tests
├── test_set_command.py          # Set command tests
├── test_slap_command.py         # Slap command tests
├── test_state_doc_accuracy.py   # State documentation accuracy tests
├── test_state_machines.py       # State machine tests
├── test_tables_completeness.py  # Tables completeness tests
├── test_validation_coverage.py  # Validation coverage tests
├── test_validation_pattern_docs.py  # Validation pattern docs tests
├── test_validators.py           # Documentation validator tests
└── test_vince_validators.py     # Vince CLI validator tests
```

## Fixtures

Test fixtures provide reusable setup and teardown logic for consistent test environments. Fixtures are defined inline in each test file rather than in a shared `conftest.py`.

### CLI Test Fixture

The CLI test fixture provides an isolated environment for testing Typer commands:

```python
import pytest
from typer.testing import CliRunner

@pytest.fixture
def runner():
    """Provide a Typer CLI test runner."""
    return CliRunner()
```

### Mock Executable Fixture

Creates a mock executable file for testing path validation:

```python
@pytest.fixture
def mock_executable(tmp_path):
    """Create a mock executable file for testing."""
    exe = tmp_path / "mock_app"
    exe.write_text("#!/bin/bash\necho 'mock'")
    exe.chmod(0o755)
    return exe
```

### Non-Executable File Fixture

Creates a non-executable file for testing permission errors:

```python
@pytest.fixture
def non_executable_file(tmp_path):
    """Create a non-executable file for testing."""
    file = tmp_path / "test_file.txt"
    file.write_text("test content")
    file.chmod(0o644)
    return file
```

### Isolated Data Directory Fixture

Provides an isolated data directory with empty data files:

```python
@pytest.fixture
def isolated_data_dir(tmp_path):
    """Provide isolated data directory with empty data files."""
    data_dir = tmp_path / ".vince"
    data_dir.mkdir()
    (data_dir / "defaults.json").write_text('{"version": "1.0.0", "defaults": []}')
    (data_dir / "offers.json").write_text('{"version": "1.0.0", "offers": []}')
    return data_dir
```

### Unique Data Directory Pattern

For property-based tests that run many iterations, use unique directories:

```python
import uuid
import tempfile

with tempfile.TemporaryDirectory() as tmp_dir:
    unique_id = str(uuid.uuid4())
    data_dir = Path(tmp_dir) / f".vince_{unique_id}"
    data_dir.mkdir(exist_ok=True)
    # ... test code
```

## Mocks

Mock patterns for isolating tests from external dependencies.

### Config Mocking

Mock configuration loading for testing different config scenarios:

```python
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

### Monkeypatch Pattern for Commands

Use monkeypatch to inject mock config into commands:

```python
def test_command_with_mock_config(runner, mock_executable, isolated_data_dir, monkeypatch):
    mock_config = create_mock_config(isolated_data_dir)
    mock_data_dir = create_mock_data_dir(isolated_data_dir)

    monkeypatch.setattr("vince.commands.slap.get_config", mock_config)
    monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_data_dir)

    result = runner.invoke(app, ["slap", str(mock_executable), "--md"])
    assert result.exit_code == 0
```

### Multi-Command Monkeypatch

For integration tests involving multiple commands:

```python
def test_multi_command_flow(runner, mock_executable, isolated_data_dir, monkeypatch):
    mock_config = create_mock_config(isolated_data_dir)
    mock_data_dir = create_mock_data_dir(isolated_data_dir)

    # Patch all commands used in the test
    for cmd in ["slap", "offer", "reject", "chop", "list_cmd"]:
        monkeypatch.setattr(f"vince.commands.{cmd}.get_config", mock_config)
        monkeypatch.setattr(f"vince.commands.{cmd}.get_data_dir", mock_data_dir)

    # ... test code
```

## Generators

Hypothesis strategies for generating test data in property-based tests.

### Extension Strategies

Generate valid and invalid file extensions:

```python
from hypothesis import strategies as st
from vince.validation.extension import SUPPORTED_EXTENSIONS

@st.composite
def valid_extensions(draw):
    """Generate valid file extensions from the supported set."""
    return draw(st.sampled_from(list(SUPPORTED_EXTENSIONS)))

@st.composite
def unsupported_extensions(draw):
    """Generate extensions that match pattern but are not supported."""
    unsupported = [".exe", ".dll", ".so", ".bin", ".dat", ".log", ".tmp", ".bak"]
    return draw(st.sampled_from(unsupported))
```

### Offer ID Strategies

Generate valid and invalid offer identifiers:

```python
import string
from vince.validation.offer_id import RESERVED_NAMES

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

    # Ensure not a reserved name
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
```

### Application Path Strategies

Generate valid-looking application paths:

```python
@st.composite
def valid_application_paths(draw):
    """Generate valid-looking application paths."""
    app_name = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "_-",
        min_size=1,
        max_size=20,
    ))
    return f"/usr/bin/{app_name}"
```

### State Strategies

Generate valid states for defaults and offers:

```python
@st.composite
def valid_states(draw):
    """Generate valid default states."""
    return draw(st.sampled_from(["pending", "active"]))

@st.composite
def valid_default_ids(draw):
    """Generate valid default IDs."""
    ext = draw(st.sampled_from(["md", "py", "txt", "js", "html", "css", "json"]))
    num = draw(st.integers(min_value=0, max_value=999))
    return f"def-{ext}-{num:03d}"
```

### State Transition Strategies

Generate valid and invalid state transitions:

```python
from vince.state.default_state import VALID_TRANSITIONS, DefaultState

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
```

### Markdown Content Strategies

Generate markdown content for documentation validation tests:

```python
@st.composite
def valid_heading_content(draw):
    """Generate markdown content with valid heading hierarchy."""
    h1_text = draw(st.text(
        min_size=1, max_size=50,
        alphabet=st.characters(
            whitelist_categories=("L", "N", "P", "S"),
            blacklist_characters="\n#"
        ),
    ))
    h2_texts = draw(st.lists(
        st.text(min_size=1, max_size=30,
            alphabet=st.characters(
                whitelist_categories=("L", "N"),
                blacklist_characters="\n#"
            )),
        min_size=1, max_size=3,
    ))

    lines = [f"# {h1_text.strip() or 'Title'}"]
    for h2 in h2_texts:
        h2_clean = h2.strip() or "Section"
        lines.append(f"\n## {h2_clean}")
        lines.append("\nSome content here.")

    return "\n".join(lines)

@st.composite
def valid_table_content(draw):
    """Generate markdown content with valid table syntax."""
    num_cols = draw(st.integers(min_value=2, max_value=5))
    num_rows = draw(st.integers(min_value=1, max_value=5))

    headers = [f"col{i}" for i in range(num_cols)]
    header_row = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * num_cols) + " |"

    data_rows = []
    for _ in range(num_rows):
        cells = [f"val{i}" for i in range(num_cols)]
        data_rows.append("| " + " | ".join(cells) + " |")

    return f"# Table Doc\n\n## Section\n\n{header_row}\n{separator}\n" + "\n".join(data_rows)
```

## Integration

End-to-end integration test patterns for testing complete command flows.

### Integration Test Base Pattern

```python
import pytest
import json
from typer.testing import CliRunner
from vince.main import app

class TestSlapListChopFlow:
    """Integration tests for slap → list → chop flow."""

    def test_slap_list_chop_complete_flow(
        self, runner, mock_executable, isolated_data_dir, monkeypatch
    ):
        """Test complete flow: slap creates default, list shows it, chop removes it."""
        mock_config = create_mock_config(isolated_data_dir)
        mock_data_dir = create_mock_data_dir(isolated_data_dir)

        # Patch all commands
        monkeypatch.setattr("vince.commands.slap.get_config", mock_config)
        monkeypatch.setattr("vince.commands.slap.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.list_cmd.get_config", mock_config)
        monkeypatch.setattr("vince.commands.list_cmd.get_data_dir", mock_data_dir)
        monkeypatch.setattr("vince.commands.chop.get_config", mock_config)
        monkeypatch.setattr("vince.commands.chop.get_data_dir", mock_data_dir)

        # Step 1: slap creates a pending default
        result = runner.invoke(app, ["slap", str(mock_executable), "--md"])
        assert result.exit_code == 0

        # Verify default was created
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert len(defaults_data["defaults"]) == 1
        assert defaults_data["defaults"][0]["state"] == "pending"

        # Step 2: list -def shows the default
        result = runner.invoke(app, ["list", "-def"])
        assert result.exit_code == 0
        assert ".md" in result.output

        # Step 3: chop -forget removes the default
        result = runner.invoke(app, ["chop", "--md", "-forget"])
        assert result.exit_code == 0

        # Verify default state changed to removed
        defaults_data = json.loads((isolated_data_dir / "defaults.json").read_text())
        assert defaults_data["defaults"][0]["state"] == "removed"
```

### State Verification Helpers

```python
def assert_default_exists(data_dir, extension, state=None):
    """Assert that a default exists for the given extension."""
    defaults = json.loads((data_dir / "defaults.json").read_text())
    matching = [d for d in defaults["defaults"] if d["extension"] == extension]
    assert len(matching) > 0, f"No default found for {extension}"
    if state:
        assert matching[0]["state"] == state

def assert_offer_exists(data_dir, offer_id, state=None):
    """Assert that an offer exists with the given ID."""
    offers = json.loads((data_dir / "offers.json").read_text())
    matching = [o for o in offers["offers"] if o["offer_id"] == offer_id]
    assert len(matching) > 0, f"No offer found with id {offer_id}"
    if state:
        assert matching[0]["state"] == state
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
# pyproject.toml
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

### Path Validation Tests

```python
class TestPathValidation:
    """Property-based tests for path validation."""

    @given(st.text(
        min_size=1, max_size=50,
        alphabet=string.ascii_letters + string.digits + "_-",
    ))
    @settings(max_examples=100)
    def test_nonexistent_paths_raise_invalid_path_error(self, filename):
        """Property: Non-existent paths should raise InvalidPathError (VE101)."""
        nonexistent = Path(f"/nonexistent_dir_xyz/{filename}")

        with pytest.raises(InvalidPathError) as exc_info:
            validate_path(nonexistent)

        assert exc_info.value.code == "VE101"

    def test_valid_executable_returns_resolved_path(self, executable_file):
        """Property: Valid executable paths should return the resolved path."""
        result = validate_path(executable_file)

        assert result == executable_file.resolve()
        assert result.exists()
        assert result.is_file()
        assert os.access(result, os.X_OK)
```

### Extension Validation Tests

```python
class TestExtensionValidation:
    """Property-based tests for extension validation."""

    @given(ext=valid_extensions())
    @settings(max_examples=100)
    def test_valid_extensions_pass(self, ext):
        """Property: All supported extensions should validate successfully."""
        result = validate_extension(ext)
        assert result == ext.lower()
        assert result in SUPPORTED_EXTENSIONS

    @given(ext=unsupported_extensions())
    @settings(max_examples=100)
    def test_unsupported_extensions_fail(self, ext):
        """Property: Unsupported extensions should raise InvalidExtensionError."""
        with pytest.raises(InvalidExtensionError) as exc_info:
            validate_extension(ext)

        assert exc_info.value.code == "VE102"
```

### Offer ID Validation Tests

```python
class TestOfferIdValidation:
    """Property-based tests for offer ID validation."""

    @given(offer_id=valid_offer_ids())
    @settings(max_examples=100)
    def test_valid_offer_ids_pass(self, offer_id):
        """Property: Valid offer IDs should validate successfully."""
        result = validate_offer_id(offer_id)
        assert result == offer_id
        assert OFFER_ID_PATTERN.match(result)
        assert result not in RESERVED_NAMES

    @given(name=st.sampled_from(list(RESERVED_NAMES)))
    @settings(max_examples=100)
    def test_reserved_names_fail(self, name):
        """Property: Reserved names should raise InvalidOfferIdError."""
        with pytest.raises(InvalidOfferIdError) as exc_info:
            validate_offer_id(name)

        assert exc_info.value.code == "VE103"
```

### State Machine Tests

```python
class TestDefaultStateTransitions:
    """Property-based tests for default state transitions."""

    @given(transition=valid_default_transitions(), ext=extensions())
    @settings(max_examples=100)
    def test_valid_transitions_succeed(self, transition, ext):
        """Property: All valid transitions should succeed without raising errors."""
        current, target = transition
        validate_transition(current, target, ext)

    @given(ext=extensions())
    @settings(max_examples=100)
    def test_none_to_removed_raises_no_default_error(self, ext):
        """Property: Transitioning from none to removed should raise NoDefaultError."""
        with pytest.raises(NoDefaultError) as exc_info:
            validate_transition(DefaultState.NONE, DefaultState.REMOVED, ext)

        assert exc_info.value.code == "VE302"
```

### Persistence Round-Trip Tests

```python
class TestPersistenceRoundTrip:
    """Property-based tests for persistence round-trip consistency."""

    @given(
        ext=valid_extensions(),
        app_path=valid_application_paths(),
        state=valid_states()
    )
    @settings(max_examples=100)
    def test_defaults_round_trip(self, ext, app_path, state):
        """Property: DefaultsStore save then load returns equivalent data."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)

            # Add entry
            added_entry = store.add(
                extension=ext,
                application_path=app_path,
                state=state,
                backup_enabled=False,
            )

            # Create a new store instance to force reload from disk
            store2 = DefaultsStore(data_dir)

            # Load and verify
            loaded_data = store2.load()

            assert len(loaded_data["defaults"]) == 1
            loaded_entry = loaded_data["defaults"][0]

            assert loaded_entry["id"] == added_entry["id"]
            assert loaded_entry["extension"] == ext
            assert loaded_entry["application_path"] == app_path
            assert loaded_entry["state"] == state
```

### Backup Retention Tests

```python
class TestBackupRetention:
    """Property-based tests for backup retention limit."""

    @given(
        num_writes=st.integers(min_value=1, max_value=10),
        max_backups=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100)
    def test_backup_count_never_exceeds_max(self, num_writes, max_backups):
        """Property: Backup count never exceeds max_backups."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)
            backup_dir = store.backup_dir

            for i in range(num_writes):
                store.add(
                    extension=f".ext{i}",
                    application_path=f"/usr/bin/app{i}",
                    state="pending",
                    backup_enabled=True,
                    max_backups=max_backups,
                )
                time.sleep(0.01)

            if backup_dir.exists():
                backup_files = list(backup_dir.glob("defaults.*.bak"))
                backup_count = len(backup_files)
            else:
                backup_count = 0

            assert backup_count <= max_backups
```

## Cross-References

- See [api.md](api.md) for command interface specifications
- See [errors.md](errors.md) for error code documentation
- See [states.md](states.md) for state machine documentation
- See [schemas.md](schemas.md) for data model schemas
- See [tables.md](tables.md) for the Single Source of Truth definitions
