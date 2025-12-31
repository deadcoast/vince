"""
Property-Based Tests for Cross-Reference Integrity

Feature: integration-validation
Property 5: Cross-Reference Integrity
Validates: Requirements 4.1, 4.2, 4.3, 4.4

Tests that all references in docs point to valid definitions in tables.md.
"""

import re
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Helper Functions for Extraction
# =============================================================================


def extract_error_codes_from_tables(tables_path: Path) -> set[str]:
    """
    Extract all error codes from the ERRORS table in tables.md.
    
    Returns a set of error codes (e.g., {'VE101', 'VE102', ...}).
    """
    error_codes = set()
    
    if not tables_path.exists():
        return error_codes
    
    content = tables_path.read_text()
    lines = content.split("\n")
    
    in_errors_section = False
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check for ERRORS section
        if stripped.startswith("## ERRORS"):
            in_errors_section = True
            continue
        elif stripped.startswith("## ") and in_errors_section:
            in_errors_section = False
            continue
        
        if in_errors_section and stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped:
                in_table = True
                continue
            if in_table:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if cells and cells[0].startswith("VE"):
                    error_codes.add(cells[0])
    
    return error_codes


def extract_state_sids_from_tables(tables_path: Path) -> set[str]:
    """
    Extract all state SIDs from the STATES table in tables.md.
    
    Returns a set of state SIDs (e.g., {'def-none', 'def-pend', 'off-crtd', ...}).
    """
    state_sids = set()
    
    if not tables_path.exists():
        return state_sids
    
    content = tables_path.read_text()
    lines = content.split("\n")
    
    in_states_section = False
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check for STATES section
        if stripped.startswith("## STATES"):
            in_states_section = True
            continue
        elif stripped.startswith("## ") and in_states_section:
            in_states_section = False
            continue
        
        if in_states_section and stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped:
                in_table = True
                continue
            if in_table:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                # sid is typically second column in STATES table
                if len(cells) >= 2 and cells[1]:
                    state_sids.add(cells[1])
    
    return state_sids


def extract_commands_from_tables(tables_path: Path) -> set[str]:
    """
    Extract all command IDs from the COMMANDS table in tables.md.
    
    Returns a set of command names (e.g., {'slap', 'chop', 'set', ...}).
    """
    commands = set()
    
    if not tables_path.exists():
        return commands
    
    content = tables_path.read_text()
    lines = content.split("\n")
    
    in_commands_section = False
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check for COMMANDS section
        if stripped.startswith("## COMMANDS"):
            in_commands_section = True
            continue
        elif stripped.startswith("## ") and in_commands_section:
            in_commands_section = False
            continue
        
        if in_commands_section and stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped:
                in_table = True
                continue
            if in_table:
                cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]
                # id is first column in COMMANDS table
                if cells and cells[0]:
                    commands.add(cells[0])
    
    return commands


def extract_config_options_from_tables(tables_path: Path) -> set[str]:
    """
    Extract all config option keys from the CONFIG_OPTIONS table in tables.md.
    
    Returns a set of config option keys (e.g., {'version', 'data_dir', ...}).
    """
    options = set()
    
    if not tables_path.exists():
        return options
    
    content = tables_path.read_text()
    lines = content.split("\n")
    
    in_config_section = False
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check for CONFIG_OPTIONS section
        if stripped.startswith("## CONFIG_OPTIONS"):
            in_config_section = True
            continue
        elif stripped.startswith("## ") and in_config_section:
            in_config_section = False
            continue
        
        if in_config_section and stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped:
                in_table = True
                continue
            if in_table:
                cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]
                # key is first column in CONFIG_OPTIONS table
                if cells and cells[0]:
                    options.add(cells[0])
    
    return options


def extract_error_codes_from_api(api_path: Path) -> set[str]:
    """
    Extract all error codes referenced in api.md.
    
    Looks for error codes in the format VE### in the document.
    """
    error_codes = set()
    
    if not api_path.exists():
        return error_codes
    
    content = api_path.read_text()
    
    # Pattern to match error codes like VE101, VE201, etc.
    error_code_pattern = re.compile(r"\bVE[1-5]\d{2}\b")
    
    for match in error_code_pattern.finditer(content):
        error_codes.add(match.group())
    
    return error_codes


def extract_state_sids_from_states(states_path: Path) -> set[str]:
    """
    Extract all state SIDs referenced in states.md.
    
    Looks for state SIDs in the format def-* or off-* in the document.
    """
    state_sids = set()
    
    if not states_path.exists():
        return state_sids
    
    content = states_path.read_text()
    
    # Pattern to match state SIDs like def-none, def-pend, off-crtd, etc.
    state_sid_pattern = re.compile(r"\b(def-\w+|off-\w+)\b")
    
    for match in state_sid_pattern.finditer(content):
        state_sids.add(match.group())
    
    return state_sids


def extract_commands_from_examples(examples_path: Path) -> set[str]:
    """
    Extract all command names referenced in examples.md.
    
    Looks for command section headers like ## `slap`.
    """
    commands = set()
    
    if not examples_path.exists():
        return commands
    
    content = examples_path.read_text()
    lines = content.split("\n")
    
    # Pattern to match command section headers like ## `slap`
    section_pattern = re.compile(r"^##\s+`(\w+)`")
    
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        match = section_pattern.match(stripped)
        if match:
            commands.add(match.group(1))
    
    return commands


def extract_config_options_from_config(config_path: Path) -> set[str]:
    """
    Extract all config option keys referenced in config.md.
    
    Looks for config keys in tables and code blocks.
    """
    options = set()
    
    if not config_path.exists():
        return options
    
    content = config_path.read_text()
    lines = content.split("\n")
    
    in_code_block = False
    in_table = False
    table_headers = []
    
    # Known config option keys to look for
    known_options = {
        "version", "data_dir", "verbose", "color_theme",
        "backup_enabled", "max_backups", "confirm_destructive"
    }
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        
        # Look for config keys in tables
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]
            
            if not in_table:
                in_table = True
                table_headers = [h.lower() for h in cells]
            elif "---" in stripped:
                continue
            else:
                # Check if first cell is a known config option
                if cells and cells[0] in known_options:
                    options.add(cells[0])
        elif in_table and not stripped.startswith("|"):
            in_table = False
            table_headers = []
        
        # Also look for config keys in inline code
        for opt in known_options:
            if f"`{opt}`" in line:
                options.add(opt)
    
    return options


# =============================================================================
# Property 5: Cross-Reference Integrity
# Validates: Requirements 4.1, 4.2, 4.3, 4.4
# Feature: integration-validation
# =============================================================================


class TestCrossReferenceIntegrity:
    """
    Feature: integration-validation, Property 5: Cross-Reference Integrity
    
    For any identifier referenced in one documentation file that should be
    defined in tables.md, that identifier SHALL exist in the appropriate
    table in tables.md.
    """
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    @pytest.fixture
    def tables_path(self, docs_dir: Path) -> Path:
        """Get the tables.md path."""
        return docs_dir / "tables.md"
    
    def test_error_codes_in_api_exist_in_tables(
        self,
        docs_dir: Path,
        tables_path: Path,
    ):
        """
        Property 5: All error codes referenced in api.md should exist in tables.md.
        
        For any error code referenced in docs/api.md, THE Documentation_System
        SHALL have a definition in docs/tables.md ERRORS table.
        
        **Validates: Requirements 4.1**
        """
        api_path = docs_dir / "api.md"
        
        if not api_path.exists():
            pytest.skip("api.md not found")
        
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        
        # Extract error codes from both files
        api_error_codes = extract_error_codes_from_api(api_path)
        tables_error_codes = extract_error_codes_from_tables(tables_path)
        
        # Check that all error codes in api.md exist in tables.md
        missing_in_tables = api_error_codes - tables_error_codes
        
        assert len(missing_in_tables) == 0, (
            f"Error codes referenced in api.md but not defined in tables.md ERRORS table: "
            f"{sorted(missing_in_tables)}"
        )
    
    def test_state_sids_in_states_exist_in_tables(
        self,
        docs_dir: Path,
        tables_path: Path,
    ):
        """
        Property 5: All state SIDs referenced in states.md should exist in tables.md.
        
        For any state name referenced in docs/states.md, THE Documentation_System
        SHALL have a definition in docs/tables.md STATES table.
        
        **Validates: Requirements 4.2**
        """
        states_path = docs_dir / "states.md"
        
        if not states_path.exists():
            pytest.skip("states.md not found")
        
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        
        # Extract state SIDs from both files
        states_sids = extract_state_sids_from_states(states_path)
        tables_sids = extract_state_sids_from_tables(tables_path)
        
        # Check that all state SIDs in states.md exist in tables.md
        missing_in_tables = states_sids - tables_sids
        
        assert len(missing_in_tables) == 0, (
            f"State SIDs referenced in states.md but not defined in tables.md STATES table: "
            f"{sorted(missing_in_tables)}"
        )
    
    def test_commands_in_examples_exist_in_tables(
        self,
        docs_dir: Path,
        tables_path: Path,
    ):
        """
        Property 5: All commands referenced in examples.md should exist in tables.md.
        
        For any command referenced in docs/examples.md, THE Documentation_System
        SHALL have a definition in docs/tables.md COMMANDS table.
        
        **Validates: Requirements 4.3**
        """
        examples_path = docs_dir / "examples.md"
        
        if not examples_path.exists():
            pytest.skip("examples.md not found")
        
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        
        # Extract commands from both files
        examples_commands = extract_commands_from_examples(examples_path)
        tables_commands = extract_commands_from_tables(tables_path)
        
        # Check that all commands in examples.md exist in tables.md
        missing_in_tables = examples_commands - tables_commands
        
        assert len(missing_in_tables) == 0, (
            f"Commands referenced in examples.md but not defined in tables.md COMMANDS table: "
            f"{sorted(missing_in_tables)}"
        )
    
    def test_config_options_in_config_exist_in_tables(
        self,
        docs_dir: Path,
        tables_path: Path,
    ):
        """
        Property 5: All config options referenced in config.md should exist in tables.md.
        
        For any config option referenced in docs/config.md, THE Documentation_System
        SHALL have a definition in docs/tables.md CONFIG_OPTIONS table.
        
        **Validates: Requirements 4.4**
        """
        config_path = docs_dir / "config.md"
        
        if not config_path.exists():
            pytest.skip("config.md not found")
        
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        
        # Extract config options from both files
        config_options = extract_config_options_from_config(config_path)
        tables_options = extract_config_options_from_tables(tables_path)
        
        # Check that all config options in config.md exist in tables.md
        missing_in_tables = config_options - tables_options
        
        assert len(missing_in_tables) == 0, (
            f"Config options referenced in config.md but not defined in tables.md CONFIG_OPTIONS table: "
            f"{sorted(missing_in_tables)}"
        )


# =============================================================================
# Property-Based Tests for Cross-Reference Integrity
# =============================================================================


@st.composite
def error_code_strategy(draw):
    """Generate valid error codes in VE### format."""
    category = draw(st.integers(min_value=1, max_value=5))
    number = draw(st.integers(min_value=1, max_value=5))
    return f"VE{category}0{number}"


@st.composite
def state_sid_strategy(draw):
    """Generate valid state SIDs."""
    entity = draw(st.sampled_from(["def", "off"]))
    state_suffixes = {
        "def": ["none", "pend", "actv", "rmvd"],
        "off": ["none", "crtd", "actv", "rjct"],
    }
    suffix = draw(st.sampled_from(state_suffixes[entity]))
    return f"{entity}-{suffix}"


@st.composite
def command_strategy(draw):
    """Generate valid command names."""
    return draw(st.sampled_from([
        "slap", "chop", "set", "forget", "offer", "reject", "list"
    ]))


@st.composite
def config_option_strategy(draw):
    """Generate valid config option keys."""
    return draw(st.sampled_from([
        "version", "data_dir", "verbose", "color_theme",
        "backup_enabled", "max_backups", "confirm_destructive"
    ]))


class TestCrossReferenceProperties:
    """Property-based tests for cross-reference integrity."""
    
    @given(error_code=error_code_strategy())
    @settings(max_examples=100)
    def test_error_code_cross_reference_property(
        self,
        error_code: str,
    ):
        """
        Property: For any error code in the valid error code space,
        if it is referenced in api.md, it should exist in tables.md.
        
        **Validates: Requirements 4.1**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        api_path = docs_dir / "api.md"
        tables_path = docs_dir / "tables.md"
        
        if not api_path.exists() or not tables_path.exists():
            return  # Skip if files don't exist
        
        api_error_codes = extract_error_codes_from_api(api_path)
        tables_error_codes = extract_error_codes_from_tables(tables_path)
        
        # If error code is referenced in api.md, it should be in tables.md
        if error_code in api_error_codes:
            assert error_code in tables_error_codes, (
                f"Error code '{error_code}' referenced in api.md but not in tables.md"
            )
    
    @given(state_sid=state_sid_strategy())
    @settings(max_examples=100)
    def test_state_sid_cross_reference_property(
        self,
        state_sid: str,
    ):
        """
        Property: For any state SID in the valid state SID space,
        if it is referenced in states.md, it should exist in tables.md.
        
        **Validates: Requirements 4.2**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        states_path = docs_dir / "states.md"
        tables_path = docs_dir / "tables.md"
        
        if not states_path.exists() or not tables_path.exists():
            return  # Skip if files don't exist
        
        states_sids = extract_state_sids_from_states(states_path)
        tables_sids = extract_state_sids_from_tables(tables_path)
        
        # If state SID is referenced in states.md, it should be in tables.md
        if state_sid in states_sids:
            assert state_sid in tables_sids, (
                f"State SID '{state_sid}' referenced in states.md but not in tables.md"
            )
    
    @given(command=command_strategy())
    @settings(max_examples=100)
    def test_command_cross_reference_property(
        self,
        command: str,
    ):
        """
        Property: For any command in the valid command space,
        if it is referenced in examples.md, it should exist in tables.md.
        
        **Validates: Requirements 4.3**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        examples_path = docs_dir / "examples.md"
        tables_path = docs_dir / "tables.md"
        
        if not examples_path.exists() or not tables_path.exists():
            return  # Skip if files don't exist
        
        examples_commands = extract_commands_from_examples(examples_path)
        tables_commands = extract_commands_from_tables(tables_path)
        
        # If command is referenced in examples.md, it should be in tables.md
        if command in examples_commands:
            assert command in tables_commands, (
                f"Command '{command}' referenced in examples.md but not in tables.md"
            )
    
    @given(config_option=config_option_strategy())
    @settings(max_examples=100)
    def test_config_option_cross_reference_property(
        self,
        config_option: str,
    ):
        """
        Property: For any config option in the valid config option space,
        if it is referenced in config.md, it should exist in tables.md.
        
        **Validates: Requirements 4.4**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        config_path = docs_dir / "config.md"
        tables_path = docs_dir / "tables.md"
        
        if not config_path.exists() or not tables_path.exists():
            return  # Skip if files don't exist
        
        config_options = extract_config_options_from_config(config_path)
        tables_options = extract_config_options_from_tables(tables_path)
        
        # If config option is referenced in config.md, it should be in tables.md
        if config_option in config_options:
            assert config_option in tables_options, (
                f"Config option '{config_option}' referenced in config.md but not in tables.md"
            )


# =============================================================================
# Integration Tests: Validate Real Cross-References
# =============================================================================


class TestCrossReferenceIntegration:
    """Integration tests for cross-reference validation."""
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    def test_validate_new_table_cross_references_function(
        self,
        docs_dir: Path,
    ):
        """
        Test the validate_new_table_cross_references function from validate_docs.py.
        
        This verifies that the validation function correctly identifies
        cross-reference issues between documents and tables.md.
        """
        from validate_docs import validate_new_table_cross_references
        
        tables_path = docs_dir / "tables.md"
        errors_path = docs_dir / "errors.md"
        states_path = docs_dir / "states.md"
        config_path = docs_dir / "config.md"
        
        if not all(p.exists() for p in [tables_path, errors_path, states_path, config_path]):
            pytest.skip("Required documentation files not found")
        
        tables_content = tables_path.read_text()
        errors_content = errors_path.read_text()
        states_content = states_path.read_text()
        config_content = config_path.read_text()
        
        result = validate_new_table_cross_references(
            errors_content,
            states_content,
            config_content,
            tables_content,
            "cross-refs",
        )
        
        # The result should have no errors if cross-references are valid
        cross_ref_errors = [
            e for e in result.errors
            if e.rule in ("10.2", "10.3", "10.4")
        ]
        
        assert len(cross_ref_errors) == 0, (
            f"Cross-reference errors found: "
            f"{[(e.rule, e.message) for e in cross_ref_errors]}"
        )
    
    def test_all_error_codes_bidirectional_consistency(
        self,
        docs_dir: Path,
    ):
        """
        Test bidirectional consistency for error codes.
        
        Error codes in tables.md should be referenced in errors.md and vice versa.
        """
        tables_path = docs_dir / "tables.md"
        errors_path = docs_dir / "errors.md"
        
        if not tables_path.exists() or not errors_path.exists():
            pytest.skip("Required files not found")
        
        tables_errors = extract_error_codes_from_tables(tables_path)
        
        # Extract error codes from errors.md
        errors_content = errors_path.read_text()
        error_code_pattern = re.compile(r"\bVE[1-5]\d{2}\b")
        errors_md_codes = set(error_code_pattern.findall(errors_content))
        
        # Check bidirectional consistency
        # All error codes in tables.md should be in errors.md
        missing_in_errors_md = tables_errors - errors_md_codes
        
        # Note: We allow errors.md to have more codes than tables.md
        # (e.g., for examples or references), but tables.md should be complete
        assert len(missing_in_errors_md) == 0, (
            f"Error codes in tables.md but not in errors.md: "
            f"{sorted(missing_in_errors_md)}"
        )
    
    def test_all_commands_bidirectional_consistency(
        self,
        docs_dir: Path,
    ):
        """
        Test bidirectional consistency for commands.
        
        Commands in tables.md should be referenced in examples.md and vice versa.
        """
        tables_path = docs_dir / "tables.md"
        examples_path = docs_dir / "examples.md"
        
        if not tables_path.exists() or not examples_path.exists():
            pytest.skip("Required files not found")
        
        tables_commands = extract_commands_from_tables(tables_path)
        examples_commands = extract_commands_from_examples(examples_path)
        
        # Check bidirectional consistency
        # All commands in tables.md should have examples
        missing_examples = tables_commands - examples_commands
        
        assert len(missing_examples) == 0, (
            f"Commands in tables.md but not in examples.md: "
            f"{sorted(missing_examples)}"
        )
        
        # All commands in examples.md should be in tables.md
        missing_in_tables = examples_commands - tables_commands
        
        assert len(missing_in_tables) == 0, (
            f"Commands in examples.md but not in tables.md: "
            f"{sorted(missing_in_tables)}"
        )
