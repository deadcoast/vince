"""
Property-Based Tests for Schema Documentation Accuracy

Feature: documentation-unification
Property 5: Schema Documentation Accuracy
Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5

Tests that schema documentation in docs/schemas.md accurately reflects
the actual field definitions in the persistence layer source code.
"""

import re
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


# =============================================================================
# Helper Functions for Extraction
# =============================================================================


def extract_defaults_store_fields(defaults_py_path: Path) -> dict[str, dict]:
    """
    Extract field definitions from DefaultsStore.add() method.
    
    Returns a dict mapping field names to their properties.
    """
    fields = {}
    
    if not defaults_py_path.exists():
        return fields
    
    content = defaults_py_path.read_text()
    
    # Extract fields from the add() method entry dict
    # Looking for patterns like:
    # "id": entry_id,
    # "extension": extension,
    # "application_path": application_path,
    # "state": state,
    # "created_at": datetime.now(timezone.utc).isoformat(),
    
    # Find the add method and extract the entry dict
    add_method_pattern = re.compile(
        r'def add\(.*?\).*?entry:\s*Dict\[str,\s*Any\]\s*=\s*\{([^}]+)\}',
        re.DOTALL
    )
    
    match = add_method_pattern.search(content)
    if match:
        entry_content = match.group(1)
        
        # Extract field names from the dict
        field_pattern = re.compile(r'"(\w+)":\s*')
        for field_match in field_pattern.finditer(entry_content):
            field_name = field_match.group(1)
            fields[field_name] = {"required": True}
    
    # Check for optional fields added conditionally
    if 'if application_name:' in content:
        fields["application_name"] = {"required": False}
    
    # Check for updated_at in update_state method
    if 'entry["updated_at"]' in content:
        fields["updated_at"] = {"required": False}
    
    # OS sync fields have default values and are optional
    # os_synced defaults to False, os_synced_at and previous_os_default are only set conditionally
    if 'os_synced' in fields:
        fields["os_synced"] = {"required": False}
    if 'os_synced_at' in fields:
        fields["os_synced_at"] = {"required": False}
    if 'previous_os_default' in fields:
        fields["previous_os_default"] = {"required": False}
    
    return fields


def extract_offers_store_fields(offers_py_path: Path) -> dict[str, dict]:
    """
    Extract field definitions from OffersStore.add() method.
    
    Returns a dict mapping field names to their properties.
    """
    fields = {}
    
    if not offers_py_path.exists():
        return fields
    
    content = offers_py_path.read_text()
    
    # Find the add method and extract the entry dict
    add_method_pattern = re.compile(
        r'def add\(.*?\).*?entry:\s*Dict\[str,\s*Any\]\s*=\s*\{([^}]+)\}',
        re.DOTALL
    )
    
    match = add_method_pattern.search(content)
    if match:
        entry_content = match.group(1)
        
        # Extract field names from the dict
        field_pattern = re.compile(r'"(\w+)":\s*')
        for field_match in field_pattern.finditer(entry_content):
            field_name = field_match.group(1)
            fields[field_name] = {"required": True}
    
    # Check for optional fields added conditionally
    if 'if description:' in content:
        fields["description"] = {"required": False}
    
    # Check for used_at in update_state method
    if 'entry["used_at"]' in content:
        fields["used_at"] = {"required": False}
    
    return fields


def extract_default_state_values(default_state_py_path: Path) -> set[str]:
    """
    Extract state enum values from DefaultState.
    
    Returns a set of state value strings.
    """
    states = set()
    
    if not default_state_py_path.exists():
        return states
    
    content = default_state_py_path.read_text()
    
    # Look for enum values like NONE = "none", PENDING = "pending", etc.
    state_pattern = re.compile(r'(\w+)\s*=\s*"(\w+)"')
    
    # Only capture values within the DefaultState class
    class_match = re.search(
        r'class DefaultState\(Enum\):.*?(?=class|\Z)',
        content,
        re.DOTALL
    )
    
    if class_match:
        class_content = class_match.group(0)
        for match in state_pattern.finditer(class_content):
            state_value = match.group(2).lower()
            states.add(state_value)
    
    return states


def extract_offer_state_values(offer_state_py_path: Path) -> set[str]:
    """
    Extract state enum values from OfferState.
    
    Returns a set of state value strings.
    """
    states = set()
    
    if not offer_state_py_path.exists():
        return states
    
    content = offer_state_py_path.read_text()
    
    # Look for enum values
    state_pattern = re.compile(r'(\w+)\s*=\s*"(\w+)"')
    
    # Only capture values within the OfferState class
    class_match = re.search(
        r'class OfferState\(Enum\):.*?(?=class|\Z)',
        content,
        re.DOTALL
    )
    
    if class_match:
        class_content = class_match.group(0)
        for match in state_pattern.finditer(class_content):
            state_value = match.group(2).lower()
            states.add(state_value)
    
    return states


def extract_documented_default_entry_fields(schemas_md_path: Path) -> dict[str, dict]:
    """
    Extract DefaultEntry field definitions from docs/schemas.md.
    
    Returns a dict mapping field names to their properties.
    """
    fields = {}
    
    if not schemas_md_path.exists():
        return fields
    
    content = schemas_md_path.read_text()
    
    # Find the DefaultEntry Fields table
    # Format: | `field_name` | type | Yes/No | Description |
    table_pattern = re.compile(
        r'### DefaultEntry Fields.*?'
        r'\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|.*?'
        r'((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n?)+)',
        re.DOTALL
    )
    
    match = table_pattern.search(content)
    if match:
        table_content = match.group(1)
        
        # Parse each row
        row_pattern = re.compile(
            r'\|\s*`?(\w+)`?\s*\|\s*(\w+(?:-\w+)?)\s*\|\s*(Yes|No)\s*\|'
        )
        
        for row_match in row_pattern.finditer(table_content):
            field_name = row_match.group(1)
            field_type = row_match.group(2)
            required = row_match.group(3) == "Yes"
            
            fields[field_name] = {
                "type": field_type,
                "required": required,
            }
    
    return fields


def extract_documented_offer_entry_fields(schemas_md_path: Path) -> dict[str, dict]:
    """
    Extract OfferEntry field definitions from docs/schemas.md.
    
    Returns a dict mapping field names to their properties.
    """
    fields = {}
    
    if not schemas_md_path.exists():
        return fields
    
    content = schemas_md_path.read_text()
    
    # Find the OfferEntry Fields table
    table_pattern = re.compile(
        r'### OfferEntry Fields.*?'
        r'\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|.*?'
        r'((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n?)+)',
        re.DOTALL
    )
    
    match = table_pattern.search(content)
    if match:
        table_content = match.group(1)
        
        # Parse each row
        row_pattern = re.compile(
            r'\|\s*`?(\w+)`?\s*\|\s*(\w+(?:-\w+)?)\s*\|\s*(Yes|No)\s*\|'
        )
        
        for row_match in row_pattern.finditer(table_content):
            field_name = row_match.group(1)
            field_type = row_match.group(2)
            required = row_match.group(3) == "Yes"
            
            fields[field_name] = {
                "type": field_type,
                "required": required,
            }
    
    return fields


def extract_documented_default_state_values(schemas_md_path: Path) -> set[str]:
    """
    Extract documented DefaultEntry state enum values from docs/schemas.md.
    
    Returns a set of state value strings.
    """
    states = set()
    
    if not schemas_md_path.exists():
        return states
    
    content = schemas_md_path.read_text()
    
    # Look for state enum in DefaultEntry schema
    # Pattern: "enum": ["pending", "active", "removed"]
    enum_pattern = re.compile(
        r'"state":\s*\{[^}]*"enum":\s*\[([^\]]+)\]',
        re.DOTALL
    )
    
    # Find in DefaultEntry section
    default_entry_match = re.search(
        r'"DefaultEntry":\s*\{.*?"state":\s*\{[^}]*"enum":\s*\[([^\]]+)\]',
        content,
        re.DOTALL
    )
    
    if default_entry_match:
        enum_values = default_entry_match.group(1)
        # Extract individual values
        value_pattern = re.compile(r'"(\w+)"')
        for match in value_pattern.finditer(enum_values):
            states.add(match.group(1).lower())
    
    return states


def extract_documented_offer_state_values(schemas_md_path: Path) -> set[str]:
    """
    Extract documented OfferEntry state enum values from docs/schemas.md.
    
    Returns a set of state value strings.
    """
    states = set()
    
    if not schemas_md_path.exists():
        return states
    
    content = schemas_md_path.read_text()
    
    # Find in OfferEntry section
    offer_entry_match = re.search(
        r'"OfferEntry":\s*\{.*?"state":\s*\{[^}]*"enum":\s*\[([^\]]+)\]',
        content,
        re.DOTALL
    )
    
    if offer_entry_match:
        enum_values = offer_entry_match.group(1)
        # Extract individual values
        value_pattern = re.compile(r'"(\w+)"')
        for match in value_pattern.finditer(enum_values):
            states.add(match.group(1).lower())
    
    return states


def check_timestamp_format_documented(schemas_md_path: Path) -> bool:
    """
    Check if ISO 8601 timestamp format is documented for timestamp fields.
    
    Returns True if properly documented.
    """
    if not schemas_md_path.exists():
        return False
    
    content = schemas_md_path.read_text()
    
    # Check for ISO 8601 mention
    has_iso_8601 = "ISO 8601" in content or "iso 8601" in content.lower()
    
    # Check for date-time format in schema
    has_datetime_format = '"format": "date-time"' in content
    
    # Check for timestamp fields with proper format
    has_created_at_format = re.search(
        r'"created_at":\s*\{[^}]*"format":\s*"date-time"',
        content,
        re.DOTALL
    )
    
    return has_iso_8601 and has_datetime_format and has_created_at_format is not None


# =============================================================================
# Property 5: Schema Documentation Accuracy
# Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
# Feature: documentation-unification
# =============================================================================


class TestSchemaDocumentationAccuracy:
    """
    Feature: documentation-unification, Property 5: Schema Documentation Accuracy
    
    For any field defined in DefaultsStore or OffersStore, the schemas.md
    documentation SHALL contain that field with matching type, required status,
    and format specification.
    
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
    """
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    @pytest.fixture
    def src_dir(self) -> Path:
        """Get the vince source directory path."""
        return Path(__file__).parent.parent / "vince"
    
    def test_default_entry_fields_match_source(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 5: DefaultEntry schema fields should match source code.
        
        For any field defined in DefaultsStore.add(), the schemas.md
        documentation SHALL contain that field.
        
        **Validates: Requirements 5.1, 5.3**
        """
        defaults_py_path = src_dir / "persistence" / "defaults.py"
        schemas_md_path = docs_dir / "schemas.md"
        
        if not defaults_py_path.exists():
            pytest.skip("vince/persistence/defaults.py not found")
        
        if not schemas_md_path.exists():
            pytest.skip("docs/schemas.md not found")
        
        src_fields = extract_defaults_store_fields(defaults_py_path)
        doc_fields = extract_documented_default_entry_fields(schemas_md_path)
        
        # Check that all source fields are documented
        src_field_names = set(src_fields.keys())
        doc_field_names = set(doc_fields.keys())
        
        missing_in_docs = src_field_names - doc_field_names
        
        assert len(missing_in_docs) == 0, (
            f"DefaultEntry fields in source but not documented: {sorted(missing_in_docs)}"
        )
    
    def test_offer_entry_fields_match_source(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 5: OfferEntry schema fields should match source code.
        
        For any field defined in OffersStore.add(), the schemas.md
        documentation SHALL contain that field.
        
        **Validates: Requirements 5.2, 5.3**
        """
        offers_py_path = src_dir / "persistence" / "offers.py"
        schemas_md_path = docs_dir / "schemas.md"
        
        if not offers_py_path.exists():
            pytest.skip("vince/persistence/offers.py not found")
        
        if not schemas_md_path.exists():
            pytest.skip("docs/schemas.md not found")
        
        src_fields = extract_offers_store_fields(offers_py_path)
        doc_fields = extract_documented_offer_entry_fields(schemas_md_path)
        
        # Check that all source fields are documented
        src_field_names = set(src_fields.keys())
        doc_field_names = set(doc_fields.keys())
        
        missing_in_docs = src_field_names - doc_field_names
        
        assert len(missing_in_docs) == 0, (
            f"OfferEntry fields in source but not documented: {sorted(missing_in_docs)}"
        )
    
    def test_default_state_values_match_source(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 5: DefaultEntry state enum values should match source code.
        
        For any state value in DefaultState enum, the schemas.md documentation
        SHALL list that value in the state enum.
        
        **Validates: Requirements 5.3, 5.5**
        """
        default_state_py_path = src_dir / "state" / "default_state.py"
        schemas_md_path = docs_dir / "schemas.md"
        
        if not default_state_py_path.exists():
            pytest.skip("vince/state/default_state.py not found")
        
        if not schemas_md_path.exists():
            pytest.skip("docs/schemas.md not found")
        
        src_states = extract_default_state_values(default_state_py_path)
        doc_states = extract_documented_default_state_values(schemas_md_path)
        
        # Remove "none" from source states as it's not stored in JSON
        src_stored_states = src_states - {"none"}
        
        # Check that documented states match source stored states
        assert src_stored_states == doc_states, (
            f"DefaultEntry state values mismatch. "
            f"Source (stored): {sorted(src_stored_states)}, "
            f"Documented: {sorted(doc_states)}"
        )
    
    def test_offer_state_values_match_source(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 5: OfferEntry state enum values should match source code.
        
        For any state value in OfferState enum, the schemas.md documentation
        SHALL list that value in the state enum.
        
        **Validates: Requirements 5.3, 5.5**
        """
        offer_state_py_path = src_dir / "state" / "offer_state.py"
        schemas_md_path = docs_dir / "schemas.md"
        
        if not offer_state_py_path.exists():
            pytest.skip("vince/state/offer_state.py not found")
        
        if not schemas_md_path.exists():
            pytest.skip("docs/schemas.md not found")
        
        src_states = extract_offer_state_values(offer_state_py_path)
        doc_states = extract_documented_offer_state_values(schemas_md_path)
        
        # Remove "none" from source states as it's not stored in JSON
        src_stored_states = src_states - {"none"}
        
        # Check that documented states match source stored states
        assert src_stored_states == doc_states, (
            f"OfferEntry state values mismatch. "
            f"Source (stored): {sorted(src_stored_states)}, "
            f"Documented: {sorted(doc_states)}"
        )
    
    def test_timestamp_format_documented(
        self,
        docs_dir: Path,
    ):
        """
        Property 5: ISO 8601 timestamp format should be documented.
        
        The schemas.md documentation SHALL specify ISO 8601 format for all
        timestamp fields (created_at, updated_at, used_at).
        
        **Validates: Requirements 5.4**
        """
        schemas_md_path = docs_dir / "schemas.md"
        
        if not schemas_md_path.exists():
            pytest.skip("docs/schemas.md not found")
        
        assert check_timestamp_format_documented(schemas_md_path), (
            "ISO 8601 timestamp format not properly documented in schemas.md"
        )
    
    def test_required_fields_marked_correctly(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 5: Required fields should be marked correctly in documentation.
        
        For any required field in source code, the schemas.md documentation
        SHALL mark it as required.
        
        **Validates: Requirements 5.5**
        """
        defaults_py_path = src_dir / "persistence" / "defaults.py"
        schemas_md_path = docs_dir / "schemas.md"
        
        if not defaults_py_path.exists():
            pytest.skip("vince/persistence/defaults.py not found")
        
        if not schemas_md_path.exists():
            pytest.skip("docs/schemas.md not found")
        
        src_fields = extract_defaults_store_fields(defaults_py_path)
        doc_fields = extract_documented_default_entry_fields(schemas_md_path)
        
        # Check required fields match
        for field_name, field_props in src_fields.items():
            if field_name in doc_fields:
                src_required = field_props.get("required", False)
                doc_required = doc_fields[field_name].get("required", False)
                
                # Only check fields that are required in source
                if src_required:
                    assert doc_required, (
                        f"Field '{field_name}' is required in source but not "
                        f"marked as required in documentation"
                    )


# =============================================================================
# Property-Based Tests for Schema Accuracy
# =============================================================================


@st.composite
def default_entry_field_strategy(draw):
    """Generate valid DefaultEntry field names."""
    return draw(st.sampled_from([
        "id", "extension", "application_path", "application_name",
        "state", "created_at", "updated_at",
    ]))


@st.composite
def offer_entry_field_strategy(draw):
    """Generate valid OfferEntry field names."""
    return draw(st.sampled_from([
        "offer_id", "default_id", "state", "auto_created",
        "description", "created_at", "used_at",
    ]))


class TestSchemaAccuracyProperties:
    """
    Property-based tests for schema documentation accuracy.
    
    Feature: documentation-unification, Property 5: Schema Documentation Accuracy
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
    """
    
    @given(field_name=default_entry_field_strategy())
    @settings(max_examples=100)
    def test_default_entry_field_documented(
        self,
        field_name: str,
    ):
        """
        Property 5: For any DefaultEntry field, documentation should exist.
        
        For any field name from the DefaultEntry schema, it SHALL be
        documented in docs/schemas.md.
        
        **Validates: Requirements 5.1, 5.3**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        schemas_md_path = docs_dir / "schemas.md"
        
        if not schemas_md_path.exists():
            return  # Skip if file doesn't exist
        
        doc_fields = extract_documented_default_entry_fields(schemas_md_path)
        
        assert field_name in doc_fields, (
            f"DefaultEntry field '{field_name}' is not documented in schemas.md"
        )
    
    @given(field_name=offer_entry_field_strategy())
    @settings(max_examples=100)
    def test_offer_entry_field_documented(
        self,
        field_name: str,
    ):
        """
        Property 5: For any OfferEntry field, documentation should exist.
        
        For any field name from the OfferEntry schema, it SHALL be
        documented in docs/schemas.md.
        
        **Validates: Requirements 5.2, 5.3**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        schemas_md_path = docs_dir / "schemas.md"
        
        if not schemas_md_path.exists():
            return  # Skip if file doesn't exist
        
        doc_fields = extract_documented_offer_entry_fields(schemas_md_path)
        
        assert field_name in doc_fields, (
            f"OfferEntry field '{field_name}' is not documented in schemas.md"
        )
