"""
Property-Based Tests for Tables.md Completeness

Feature: documentation-unification
Property 8: Tables.md Completeness
Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6

Tests that tables.md contains all required tables with complete entries
and no duplicate sid values.
"""

import re
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vince.config import DEFAULT_CONFIG
from vince.state.default_state import DefaultState
from vince.state.offer_state import OfferState
from vince.validation.extension import SUPPORTED_EXTENSIONS


# =============================================================================
# Helper Functions
# =============================================================================


def parse_markdown_table(content: str, section_name: str) -> list[dict[str, str]]:
    """
    Parse a markdown table from a specific section.
    
    Args:
        content: Full markdown content
        section_name: Name of the section (e.g., "COMMANDS", "ERRORS")
    
    Returns:
        List of dictionaries, each representing a row with column headers as keys
    """
    lines = content.split("\n")
    in_section = False
    in_table = False
    headers: list[str] = []
    rows: list[dict[str, str]] = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check for section header
        if stripped.startswith("## "):
            section = stripped[3:].strip().upper().replace(" ", "_")
            if section == section_name.upper().replace(" ", "_"):
                in_section = True
                in_table = False
                headers = []
            else:
                in_section = False
        
        if not in_section:
            continue
        
        # Parse table
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]
            
            if not in_table:
                # Header row
                in_table = True
                headers = cells
            elif "---" in stripped:
                # Separator row, skip
                continue
            else:
                # Data row
                row = dict(zip(headers, cells))
                rows.append(row)
        elif in_table and not stripped.startswith("|"):
            # End of table
            break
    
    return rows


def get_all_sids_from_tables(content: str) -> dict[str, list[tuple[str, str]]]:
    """
    Extract all sid values from all tables in tables.md.
    
    Returns:
        Dictionary mapping sid to list of (table_name, id) tuples
    """
    sids: dict[str, list[tuple[str, str]]] = {}
    
    tables_with_sid = [
        "DEFINITIONS", "COMMANDS", "FILE_TYPES", "UTILITY_FLAGS",
        "QOL_FLAGS", "LIST_FLAGS", "ERRORS", "STATES", "CONFIG_OPTIONS"
    ]
    
    for table_name in tables_with_sid:
        rows = parse_markdown_table(content, table_name)
        for row in rows:
            sid = row.get("sid", "")
            id_val = row.get("id", row.get("code", row.get("key", "")))
            if sid:
                if sid not in sids:
                    sids[sid] = []
                sids[sid].append((table_name, id_val))
    
    return sids


def get_error_classes_from_source() -> list[dict[str, str]]:
    """
    Extract error classes from vince/errors.py source code.
    
    Returns:
        List of dictionaries with code, class_name, category
    """
    from vince import errors
    import inspect
    
    error_classes = []
    
    for name, obj in inspect.getmembers(errors):
        if (inspect.isclass(obj) and 
            issubclass(obj, errors.VinceError) and 
            obj is not errors.VinceError):
            # Try to instantiate to get the code
            try:
                if name == "InvalidPathError":
                    instance = obj("test")
                elif name == "InvalidExtensionError":
                    instance = obj("test")
                elif name == "InvalidOfferIdError":
                    instance = obj("test")
                elif name == "OfferNotFoundError":
                    instance = obj("test")
                elif name == "InvalidSubsectionError":
                    instance = obj("test")
                elif name == "VinceFileNotFoundError":
                    instance = obj("test")
                elif name == "PermissionDeniedError":
                    instance = obj("test")
                elif name == "DataCorruptedError":
                    instance = obj("test")
                elif name == "DefaultExistsError":
                    instance = obj("test")
                elif name == "NoDefaultError":
                    instance = obj("test")
                elif name == "OfferExistsError":
                    instance = obj("test")
                elif name == "OfferInUseError":
                    instance = obj("test")
                elif name == "InvalidConfigOptionError":
                    instance = obj("test")
                elif name == "ConfigMalformedError":
                    instance = obj("test")
                elif name == "UnexpectedError":
                    instance = obj("test")
                else:
                    continue
                
                code = instance.code
                # Determine category from code
                if code.startswith("VE1"):
                    category = "Input"
                elif code.startswith("VE2"):
                    category = "File"
                elif code.startswith("VE3"):
                    category = "State"
                elif code.startswith("VE4"):
                    category = "Config"
                elif code.startswith("VE5"):
                    category = "System"
                else:
                    category = "Unknown"
                
                error_classes.append({
                    "code": code,
                    "class_name": name,
                    "category": category
                })
            except Exception:
                pass
    
    return error_classes


# =============================================================================
# Property 8: Tables.md Completeness
# Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6
# Feature: documentation-unification
# =============================================================================


class TestTablesCompleteness:
    """
    Feature: documentation-unification, Property 8: Tables.md Completeness
    
    For any table in tables.md (COMMANDS, FILE_TYPES, ERRORS, STATES, 
    CONFIG_OPTIONS), all required columns SHALL be present, all entries 
    SHALL have non-empty values, and no duplicate sid values SHALL exist.
    """
    
    @pytest.fixture
    def tables_content(self) -> str:
        """Load tables.md content."""
        tables_path = Path(__file__).parent.parent / "docs" / "tables.md"
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        return tables_path.read_text()
    
    # =========================================================================
    # Requirement 8.1: COMMANDS table completeness
    # =========================================================================
    
    def test_commands_table_has_all_commands(self, tables_content: str):
        """
        Property 8: COMMANDS table should have all 7 commands.
        
        **Validates: Requirements 8.1**
        """
        expected_commands = {"slap", "chop", "set", "forget", "offer", "reject", "list"}
        
        rows = parse_markdown_table(tables_content, "COMMANDS")
        actual_commands = {row.get("id", "").strip("`") for row in rows}
        
        missing = expected_commands - actual_commands
        assert len(missing) == 0, f"Missing commands in COMMANDS table: {missing}"
    
    def test_commands_table_has_required_columns(self, tables_content: str):
        """
        Property 8: COMMANDS table should have id, sid, rid, description columns.
        
        **Validates: Requirements 8.1**
        """
        required_columns = {"id", "sid", "rid", "description"}
        
        rows = parse_markdown_table(tables_content, "COMMANDS")
        assert len(rows) > 0, "COMMANDS table is empty"
        
        actual_columns = set(rows[0].keys())
        missing = required_columns - actual_columns
        assert len(missing) == 0, f"Missing columns in COMMANDS table: {missing}"
    
    def test_commands_table_entries_complete(self, tables_content: str):
        """
        Property 8: All COMMANDS entries should have non-empty values.
        
        **Validates: Requirements 8.1**
        """
        required_columns = ["id", "sid", "rid", "description"]
        
        rows = parse_markdown_table(tables_content, "COMMANDS")
        
        for i, row in enumerate(rows):
            for col in required_columns:
                value = row.get(col, "")
                assert value.strip(), f"Row {i+1} has empty {col} in COMMANDS table"
    
    # =========================================================================
    # Requirement 8.2: FILE_TYPES table completeness
    # =========================================================================
    
    def test_file_types_table_has_all_extensions(self, tables_content: str):
        """
        Property 8: FILE_TYPES table should have all 12 supported extensions.
        
        **Validates: Requirements 8.2, 1.5**
        """
        rows = parse_markdown_table(tables_content, "FILE_TYPES")
        actual_extensions = {row.get("ext", "") for row in rows}
        
        missing = SUPPORTED_EXTENSIONS - actual_extensions
        assert len(missing) == 0, f"Missing extensions in FILE_TYPES table: {missing}"
    
    def test_file_types_table_has_required_columns(self, tables_content: str):
        """
        Property 8: FILE_TYPES table should have all required columns.
        
        **Validates: Requirements 8.2**
        """
        required_columns = {"id", "full_id", "ext", "sid", "flag_short", "flag_long"}
        
        rows = parse_markdown_table(tables_content, "FILE_TYPES")
        assert len(rows) > 0, "FILE_TYPES table is empty"
        
        actual_columns = set(rows[0].keys())
        missing = required_columns - actual_columns
        assert len(missing) == 0, f"Missing columns in FILE_TYPES table: {missing}"
    
    def test_file_types_table_entries_complete(self, tables_content: str):
        """
        Property 8: All FILE_TYPES entries should have non-empty values.
        
        **Validates: Requirements 8.2**
        """
        required_columns = ["id", "full_id", "ext", "sid", "flag_short", "flag_long"]
        
        rows = parse_markdown_table(tables_content, "FILE_TYPES")
        
        for i, row in enumerate(rows):
            for col in required_columns:
                value = row.get(col, "")
                assert value.strip(), f"Row {i+1} has empty {col} in FILE_TYPES table"
    
    # =========================================================================
    # Requirement 8.3: ERRORS table completeness
    # =========================================================================
    
    def test_errors_table_has_all_error_codes(self, tables_content: str):
        """
        Property 8: ERRORS table should have all 15 error codes from source.
        
        **Validates: Requirements 8.3, 1.2, 3.4**
        """
        expected_codes = {
            "VE101", "VE102", "VE103", "VE104", "VE105",
            "VE201", "VE202", "VE203",
            "VE301", "VE302", "VE303", "VE304",
            "VE401", "VE402",
            "VE501"
        }
        
        rows = parse_markdown_table(tables_content, "ERRORS")
        actual_codes = {row.get("code", "") for row in rows}
        
        missing = expected_codes - actual_codes
        assert len(missing) == 0, f"Missing error codes in ERRORS table: {missing}"
    
    def test_errors_table_has_required_columns(self, tables_content: str):
        """
        Property 8: ERRORS table should have code, sid, category, message, severity.
        
        **Validates: Requirements 8.3**
        """
        required_columns = {"code", "sid", "category", "message", "severity"}
        
        rows = parse_markdown_table(tables_content, "ERRORS")
        assert len(rows) > 0, "ERRORS table is empty"
        
        actual_columns = set(rows[0].keys())
        missing = required_columns - actual_columns
        assert len(missing) == 0, f"Missing columns in ERRORS table: {missing}"
    
    def test_errors_table_entries_complete(self, tables_content: str):
        """
        Property 8: All ERRORS entries should have non-empty values.
        
        **Validates: Requirements 8.3**
        """
        required_columns = ["code", "sid", "category", "message", "severity"]
        
        rows = parse_markdown_table(tables_content, "ERRORS")
        
        for i, row in enumerate(rows):
            for col in required_columns:
                value = row.get(col, "")
                assert value.strip(), f"Row {i+1} has empty {col} in ERRORS table"
    
    def test_errors_table_categories_match_code_ranges(self, tables_content: str):
        """
        Property 8: Error categories should match code ranges.
        
        VE1xx = Input, VE2xx = File, VE3xx = State, VE4xx = Config, VE5xx = System
        
        **Validates: Requirements 8.3, 1.2**
        """
        category_map = {
            "1": "Input",
            "2": "File",
            "3": "State",
            "4": "Config",
            "5": "System"
        }
        
        rows = parse_markdown_table(tables_content, "ERRORS")
        
        for row in rows:
            code = row.get("code", "")
            category = row.get("category", "")
            
            if code.startswith("VE") and len(code) >= 3:
                expected_category = category_map.get(code[2], "Unknown")
                assert category == expected_category, (
                    f"Error {code} has category '{category}', expected '{expected_category}'"
                )
    
    # =========================================================================
    # Requirement 8.4: STATES table completeness
    # =========================================================================
    
    def test_states_table_has_all_default_states(self, tables_content: str):
        """
        Property 8: STATES table should have all 4 DefaultState values.
        
        **Validates: Requirements 8.4, 6.1**
        """
        expected_states = {state.value for state in DefaultState}
        
        rows = parse_markdown_table(tables_content, "STATES")
        default_states = {
            row.get("id", "").strip("`") 
            for row in rows 
            if row.get("entity", "") == "default"
        }
        
        missing = expected_states - default_states
        assert len(missing) == 0, f"Missing default states in STATES table: {missing}"
    
    def test_states_table_has_all_offer_states(self, tables_content: str):
        """
        Property 8: STATES table should have all 4 OfferState values.
        
        **Validates: Requirements 8.4, 6.2**
        """
        expected_states = {state.value for state in OfferState}
        
        rows = parse_markdown_table(tables_content, "STATES")
        offer_states = {
            row.get("id", "").strip("`") 
            for row in rows 
            if row.get("entity", "") == "offer"
        }
        
        missing = expected_states - offer_states
        assert len(missing) == 0, f"Missing offer states in STATES table: {missing}"
    
    def test_states_table_has_required_columns(self, tables_content: str):
        """
        Property 8: STATES table should have id, sid, entity, description.
        
        **Validates: Requirements 8.4**
        """
        required_columns = {"id", "sid", "entity", "description"}
        
        rows = parse_markdown_table(tables_content, "STATES")
        assert len(rows) > 0, "STATES table is empty"
        
        actual_columns = set(rows[0].keys())
        missing = required_columns - actual_columns
        assert len(missing) == 0, f"Missing columns in STATES table: {missing}"
    
    def test_states_table_entries_complete(self, tables_content: str):
        """
        Property 8: All STATES entries should have non-empty values.
        
        **Validates: Requirements 8.4**
        """
        required_columns = ["id", "sid", "entity", "description"]
        
        rows = parse_markdown_table(tables_content, "STATES")
        
        for i, row in enumerate(rows):
            for col in required_columns:
                value = row.get(col, "")
                assert value.strip(), f"Row {i+1} has empty {col} in STATES table"
    
    # =========================================================================
    # Requirement 8.5: CONFIG_OPTIONS table completeness
    # =========================================================================
    
    def test_config_options_table_has_all_options(self, tables_content: str):
        """
        Property 8: CONFIG_OPTIONS table should have all 7 config options.
        
        **Validates: Requirements 8.5, 1.4**
        """
        expected_options = set(DEFAULT_CONFIG.keys())
        
        rows = parse_markdown_table(tables_content, "CONFIG_OPTIONS")
        actual_options = {row.get("key", "").strip("`") for row in rows}
        
        missing = expected_options - actual_options
        assert len(missing) == 0, f"Missing config options in CONFIG_OPTIONS table: {missing}"
    
    def test_config_options_table_has_required_columns(self, tables_content: str):
        """
        Property 8: CONFIG_OPTIONS table should have key, sid, type, default, description.
        
        **Validates: Requirements 8.5**
        """
        required_columns = {"key", "sid", "type", "default", "description"}
        
        rows = parse_markdown_table(tables_content, "CONFIG_OPTIONS")
        assert len(rows) > 0, "CONFIG_OPTIONS table is empty"
        
        actual_columns = set(rows[0].keys())
        missing = required_columns - actual_columns
        assert len(missing) == 0, f"Missing columns in CONFIG_OPTIONS table: {missing}"
    
    def test_config_options_table_entries_complete(self, tables_content: str):
        """
        Property 8: All CONFIG_OPTIONS entries should have non-empty values.
        
        **Validates: Requirements 8.5**
        """
        required_columns = ["key", "sid", "type", "default", "description"]
        
        rows = parse_markdown_table(tables_content, "CONFIG_OPTIONS")
        
        for i, row in enumerate(rows):
            for col in required_columns:
                value = row.get(col, "")
                assert value.strip(), f"Row {i+1} has empty {col} in CONFIG_OPTIONS table"
    
    # =========================================================================
    # Requirement 8.6: No duplicate sid values
    # =========================================================================
    
    def test_no_duplicate_sids_within_tables(self, tables_content: str):
        """
        Property 8: No duplicate sid values should exist within the same table.
        
        **Validates: Requirements 8.6**
        """
        tables_to_check = [
            "DEFINITIONS", "FILE_TYPES", "ERRORS", "STATES", "CONFIG_OPTIONS"
        ]
        
        for table_name in tables_to_check:
            rows = parse_markdown_table(tables_content, table_name)
            sids = [row.get("sid", "") for row in rows if row.get("sid", "")]
            
            seen = set()
            duplicates = set()
            for sid in sids:
                if sid in seen:
                    duplicates.add(sid)
                seen.add(sid)
            
            assert len(duplicates) == 0, (
                f"Duplicate sids in {table_name} table: {duplicates}"
            )


# =============================================================================
# Property-Based Tests
# =============================================================================


@st.composite
def table_name_strategy(draw):
    """Generate valid table names."""
    return draw(st.sampled_from([
        "COMMANDS", "FILE_TYPES", "ERRORS", "STATES", "CONFIG_OPTIONS"
    ]))


class TestTablesCompletenessProperties:
    """Property-based tests for tables.md completeness."""
    
    @given(table_name=table_name_strategy())
    @settings(max_examples=100)
    def test_table_has_entries_property(self, table_name: str):
        """
        Property 8: For any required table, it should have at least one entry.
        
        **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
        """
        tables_path = Path(__file__).parent.parent / "docs" / "tables.md"
        
        if not tables_path.exists():
            return  # Skip if tables.md doesn't exist
        
        content = tables_path.read_text()
        rows = parse_markdown_table(content, table_name)
        
        assert len(rows) > 0, f"Table {table_name} should have at least one entry"
    
    @given(table_name=table_name_strategy())
    @settings(max_examples=100)
    def test_table_entries_have_sid_property(self, table_name: str):
        """
        Property 8: For any entry in a required table, it should have a sid value.
        
        **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
        """
        tables_path = Path(__file__).parent.parent / "docs" / "tables.md"
        
        if not tables_path.exists():
            return  # Skip if tables.md doesn't exist
        
        content = tables_path.read_text()
        rows = parse_markdown_table(content, table_name)
        
        # Skip tables that don't have sid column
        if not rows:
            return
        
        if "sid" not in rows[0]:
            return
        
        for i, row in enumerate(rows):
            sid = row.get("sid", "")
            assert sid.strip(), f"Row {i+1} in {table_name} has empty sid"

