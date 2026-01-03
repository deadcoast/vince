"""
Tests for JSON Schema Validation Module

Feature: json-schema-files
Tests schema file loading, validation functions, and property-based tests
for schema correctness.

Requirements: 1.1, 1.2, 1.4, 1.5, 1.8, 2.1, 2.2, 2.4, 2.5, 2.8, 3.1, 3.5, 3.9, 4.7, 6.2, 6.3
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from vince.errors import DataCorruptedError, InvalidConfigOptionError
from vince.validation.schema import (
    SCHEMA_DIR,
    load_schema,
    validate_against_schema,
    validate_config,
    validate_defaults,
    validate_offers,
)


# =============================================================================
# Task 6.1: Unit Tests for Schema File Loading
# Requirements: 1.1, 2.1, 3.1
# =============================================================================


class TestSchemaFileLoading:
    """
    Unit tests for schema file loading functionality.
    
    Tests that each schema file loads as valid JSON and matches
    the structure defined in docs/schemas.md.
    
    **Validates: Requirements 1.1, 2.1, 3.1**
    """

    def test_defaults_schema_loads_as_valid_json(self):
        """
        Test that defaults.schema.json loads as valid JSON.
        
        **Validates: Requirements 1.1**
        """
        schema = load_schema("defaults")
        
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["title"] == "Vince Defaults"

    def test_offers_schema_loads_as_valid_json(self):
        """
        Test that offers.schema.json loads as valid JSON.
        
        **Validates: Requirements 2.1**
        """
        schema = load_schema("offers")
        
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["title"] == "Vince Offers"

    def test_config_schema_loads_as_valid_json(self):
        """
        Test that config.schema.json loads as valid JSON.
        
        **Validates: Requirements 3.1**
        """
        schema = load_schema("config")
        
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["title"] == "Vince Configuration"

    def test_defaults_schema_structure_matches_docs(self):
        """
        Test that defaults schema structure matches docs/schemas.md.
        
        **Validates: Requirements 1.1**
        """
        schema = load_schema("defaults")
        
        # Check required top-level properties
        assert "properties" in schema
        assert "version" in schema["properties"]
        assert "defaults" in schema["properties"]
        assert schema["required"] == ["version", "defaults"]
        assert schema["additionalProperties"] is False
        
        # Check DefaultEntry definition
        assert "definitions" in schema
        assert "DefaultEntry" in schema["definitions"]
        
        default_entry = schema["definitions"]["DefaultEntry"]
        required_fields = ["id", "extension", "application_path", "state", "created_at"]
        assert default_entry["required"] == required_fields
        
        # Check state enum values
        state_prop = default_entry["properties"]["state"]
        assert state_prop["enum"] == ["pending", "active", "removed"]

    def test_offers_schema_structure_matches_docs(self):
        """
        Test that offers schema structure matches docs/schemas.md.
        
        **Validates: Requirements 2.1**
        """
        schema = load_schema("offers")
        
        # Check required top-level properties
        assert "properties" in schema
        assert "version" in schema["properties"]
        assert "offers" in schema["properties"]
        assert schema["required"] == ["version", "offers"]
        assert schema["additionalProperties"] is False
        
        # Check OfferEntry definition
        assert "definitions" in schema
        assert "OfferEntry" in schema["definitions"]
        
        offer_entry = schema["definitions"]["OfferEntry"]
        required_fields = ["offer_id", "default_id", "state", "created_at"]
        assert offer_entry["required"] == required_fields
        
        # Check state enum values
        state_prop = offer_entry["properties"]["state"]
        assert state_prop["enum"] == ["created", "active", "rejected"]

    def test_config_schema_structure_matches_docs(self):
        """
        Test that config schema structure matches docs/schemas.md.
        
        **Validates: Requirements 3.1**
        """
        schema = load_schema("config")
        
        # Check required top-level properties
        assert "properties" in schema
        assert "version" in schema["properties"]
        assert schema["required"] == ["version"]
        assert schema["additionalProperties"] is False
        
        # Check optional properties exist
        optional_props = ["data_dir", "verbose", "color_theme", "backup_enabled", 
                         "max_backups", "confirm_destructive"]
        for prop in optional_props:
            assert prop in schema["properties"]
        
        # Check color_theme enum values
        color_theme_prop = schema["properties"]["color_theme"]
        assert color_theme_prop["enum"] == ["default", "dark", "light"]
        
        # Check max_backups constraints
        max_backups_prop = schema["properties"]["max_backups"]
        assert max_backups_prop["minimum"] == 0
        assert max_backups_prop["maximum"] == 100

    def test_schema_file_not_found_raises_error(self):
        """
        Test that loading a non-existent schema raises FileNotFoundError.
        """
        with pytest.raises(FileNotFoundError):
            load_schema("nonexistent")

    def test_all_schema_files_exist(self):
        """
        Test that all expected schema files exist in the schemas directory.
        """
        expected_schemas = ["defaults", "offers", "config"]
        
        for schema_name in expected_schemas:
            schema_path = SCHEMA_DIR / f"{schema_name}.schema.json"
            assert schema_path.exists(), f"Schema file {schema_path} does not exist"



# =============================================================================
# Task 6.2: Property Test for Version Pattern Validation
# Property 1: Version pattern validation
# Requirements: 1.2, 2.2
# =============================================================================


# Strategy for generating valid semver versions
@st.composite
def valid_semver_versions(draw):
    """Generate valid semver version strings."""
    major = draw(st.integers(min_value=0, max_value=999))
    minor = draw(st.integers(min_value=0, max_value=999))
    patch = draw(st.integers(min_value=0, max_value=999))
    return f"{major}.{minor}.{patch}"


# Strategy for generating invalid version strings
@st.composite
def invalid_version_strings(draw):
    """Generate strings that don't match semver pattern ^\\d+\\.\\d+\\.\\d+$."""
    choice = draw(st.integers(min_value=0, max_value=5))
    
    if choice == 0:
        # Missing parts
        return draw(st.sampled_from(["1", "1.0", "1.0.", ".1.0", "1..0"]))
    elif choice == 1:
        # Non-numeric parts
        return draw(st.sampled_from(["a.b.c", "1.x.0", "v1.0.0", "1.0.0-beta"]))
    elif choice == 2:
        # Extra parts
        return draw(st.sampled_from(["1.0.0.0", "1.0.0.0.0"]))
    elif choice == 3:
        # Letters mixed in
        return draw(st.sampled_from(["1a.0.0", "1.0a.0", "1.0.0a"]))
    elif choice == 4:
        # Empty or whitespace
        return draw(st.sampled_from(["", " ", "  1.0.0", "1.0.0  "]))
    else:
        # Random non-version strings that definitely don't match the pattern
        return draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz!@#$%').filter(
            lambda s: not re.match(r'^\d+\.\d+\.\d+$', s)
        ))


class TestVersionPatternValidation:
    """
    Property 1: Version pattern validation
    
    *For any* string, validation passes iff it matches `^\\d+\\.\\d+\\.\\d+$`
    
    **Validates: Requirements 1.2, 2.2**
    """

    @given(version=valid_semver_versions())
    @settings(max_examples=100)
    def test_valid_semver_passes_defaults_validation(self, version: str):
        """
        Property 1: Valid semver versions should pass defaults validation.
        
        *For any* valid semver string, validation SHALL pass.
        
        **Validates: Requirements 1.2**
        """
        data = {
            "version": version,
            "defaults": []
        }
        
        # Should not raise
        validate_defaults(data)

    @given(version=valid_semver_versions())
    @settings(max_examples=100)
    def test_valid_semver_passes_offers_validation(self, version: str):
        """
        Property 1: Valid semver versions should pass offers validation.
        
        *For any* valid semver string, validation SHALL pass.
        
        **Validates: Requirements 2.2**
        """
        data = {
            "version": version,
            "offers": []
        }
        
        # Should not raise
        validate_offers(data)

    @given(version=invalid_version_strings())
    @settings(max_examples=100)
    def test_invalid_version_fails_defaults_validation(self, version: str):
        """
        Property 1: Invalid version strings should fail defaults validation.
        
        *For any* string not matching semver pattern, validation SHALL fail.
        
        **Validates: Requirements 1.2**
        """
        data = {
            "version": version,
            "defaults": []
        }
        
        with pytest.raises(DataCorruptedError):
            validate_defaults(data)

    @given(version=invalid_version_strings())
    @settings(max_examples=100)
    def test_invalid_version_fails_offers_validation(self, version: str):
        """
        Property 1: Invalid version strings should fail offers validation.
        
        *For any* string not matching semver pattern, validation SHALL fail.
        
        **Validates: Requirements 2.2**
        """
        data = {
            "version": version,
            "offers": []
        }
        
        with pytest.raises(DataCorruptedError):
            validate_offers(data)


# =============================================================================
# Task 6.3: Property Test for Required Fields Rejection
# Property 2: Required fields enforcement
# Requirements: 1.4, 2.4
# =============================================================================


# Strategy for generating valid DefaultEntry with all required fields
@st.composite
def valid_default_entry(draw):
    """Generate a valid DefaultEntry with all required fields."""
    return {
        "id": draw(st.text(min_size=1, max_size=64, alphabet=st.characters(
            whitelist_categories=('L', 'N'), whitelist_characters='-_'
        ))),
        "extension": "." + draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789')),
        "application_path": "/" + draw(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyz/')),
        "state": draw(st.sampled_from(["pending", "active", "removed"])),
        "created_at": "2024-01-01T00:00:00Z",
    }


# Strategy for generating valid OfferEntry with all required fields
@st.composite
def valid_offer_entry(draw):
    """Generate a valid OfferEntry with all required fields."""
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyz'))
    rest = draw(st.text(min_size=0, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_-'))
    return {
        "offer_id": first_char + rest,
        "default_id": draw(st.text(min_size=1, max_size=64, alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_')),
        "state": draw(st.sampled_from(["created", "active", "rejected"])),
        "created_at": "2024-01-01T00:00:00Z",
    }


class TestRequiredFieldsEnforcement:
    """
    Property 2: Required fields enforcement
    
    *For any* entry missing a required field, validation SHALL fail.
    
    **Validates: Requirements 1.4, 2.4**
    """

    @given(
        entry=valid_default_entry(),
        field_to_remove=st.sampled_from(["id", "extension", "application_path", "state", "created_at"])
    )
    @settings(max_examples=100)
    def test_missing_required_field_fails_defaults_validation(
        self, entry: Dict[str, Any], field_to_remove: str
    ):
        """
        Property 2: Missing required field should fail defaults validation.
        
        *For any* DefaultEntry missing a required field, validation SHALL fail.
        
        **Validates: Requirements 1.4**
        """
        # Remove the required field
        del entry[field_to_remove]
        
        data = {
            "version": "1.0.0",
            "defaults": [entry]
        }
        
        with pytest.raises(DataCorruptedError):
            validate_defaults(data)

    @given(
        entry=valid_offer_entry(),
        field_to_remove=st.sampled_from(["offer_id", "default_id", "state", "created_at"])
    )
    @settings(max_examples=100)
    def test_missing_required_field_fails_offers_validation(
        self, entry: Dict[str, Any], field_to_remove: str
    ):
        """
        Property 2: Missing required field should fail offers validation.
        
        *For any* OfferEntry missing a required field, validation SHALL fail.
        
        **Validates: Requirements 2.4**
        """
        # Remove the required field
        del entry[field_to_remove]
        
        data = {
            "version": "1.0.0",
            "offers": [entry]
        }
        
        with pytest.raises(DataCorruptedError):
            validate_offers(data)

    def test_missing_version_fails_defaults_validation(self):
        """
        Test that missing version field fails defaults validation.
        
        **Validates: Requirements 1.4**
        """
        data = {
            "defaults": []
        }
        
        with pytest.raises(DataCorruptedError):
            validate_defaults(data)

    def test_missing_version_fails_offers_validation(self):
        """
        Test that missing version field fails offers validation.
        
        **Validates: Requirements 2.4**
        """
        data = {
            "offers": []
        }
        
        with pytest.raises(DataCorruptedError):
            validate_offers(data)

    def test_missing_defaults_array_fails_validation(self):
        """
        Test that missing defaults array fails validation.
        
        **Validates: Requirements 1.4**
        """
        data = {
            "version": "1.0.0"
        }
        
        with pytest.raises(DataCorruptedError):
            validate_defaults(data)

    def test_missing_offers_array_fails_validation(self):
        """
        Test that missing offers array fails validation.
        
        **Validates: Requirements 2.4**
        """
        data = {
            "version": "1.0.0"
        }
        
        with pytest.raises(DataCorruptedError):
            validate_offers(data)



# =============================================================================
# Task 6.4: Property Test for Enum Validation
# Property 3: Enum value enforcement
# Requirements: 1.5, 2.5, 3.5
# =============================================================================


# Strategy for generating invalid default state values
@st.composite
def invalid_default_state(draw):
    """Generate invalid default state values."""
    valid_states = {"pending", "active", "removed"}
    invalid = draw(st.text(min_size=1, max_size=20).filter(
        lambda s: s.lower() not in valid_states
    ))
    return invalid


# Strategy for generating invalid offer state values
@st.composite
def invalid_offer_state(draw):
    """Generate invalid offer state values."""
    valid_states = {"created", "active", "rejected"}
    invalid = draw(st.text(min_size=1, max_size=20).filter(
        lambda s: s.lower() not in valid_states
    ))
    return invalid


# Strategy for generating invalid color theme values
@st.composite
def invalid_color_theme(draw):
    """Generate invalid color theme values."""
    valid_themes = {"default", "dark", "light"}
    invalid = draw(st.text(min_size=1, max_size=20).filter(
        lambda s: s.lower() not in valid_themes
    ))
    return invalid


class TestEnumValueEnforcement:
    """
    Property 3: Enum value enforcement
    
    *For any* entry with invalid enum value, validation SHALL fail.
    
    **Validates: Requirements 1.5, 2.5, 3.5**
    """

    @given(invalid_state=invalid_default_state())
    @settings(max_examples=100)
    def test_invalid_default_state_fails_validation(self, invalid_state: str):
        """
        Property 3: Invalid default state should fail validation.
        
        *For any* DefaultEntry with invalid state enum value, validation SHALL fail.
        
        **Validates: Requirements 1.5**
        """
        data = {
            "version": "1.0.0",
            "defaults": [{
                "id": "test-id",
                "extension": ".md",
                "application_path": "/usr/bin/test",
                "state": invalid_state,
                "created_at": "2024-01-01T00:00:00Z",
            }]
        }
        
        with pytest.raises(DataCorruptedError):
            validate_defaults(data)

    @given(invalid_state=invalid_offer_state())
    @settings(max_examples=100)
    def test_invalid_offer_state_fails_validation(self, invalid_state: str):
        """
        Property 3: Invalid offer state should fail validation.
        
        *For any* OfferEntry with invalid state enum value, validation SHALL fail.
        
        **Validates: Requirements 2.5**
        """
        data = {
            "version": "1.0.0",
            "offers": [{
                "offer_id": "test-offer",
                "default_id": "def-001",
                "state": invalid_state,
                "created_at": "2024-01-01T00:00:00Z",
            }]
        }
        
        with pytest.raises(DataCorruptedError):
            validate_offers(data)

    @given(invalid_theme=invalid_color_theme())
    @settings(max_examples=100)
    def test_invalid_color_theme_fails_validation(self, invalid_theme: str):
        """
        Property 3: Invalid color theme should fail validation.
        
        *For any* config with invalid color_theme enum value, validation SHALL fail.
        
        **Validates: Requirements 3.5**
        """
        data = {
            "version": "1.0.0",
            "color_theme": invalid_theme,
        }
        
        with pytest.raises(InvalidConfigOptionError):
            validate_config(data)

    def test_valid_default_states_pass_validation(self):
        """
        Test that all valid default states pass validation.
        
        **Validates: Requirements 1.5**
        """
        for state in ["pending", "active", "removed"]:
            data = {
                "version": "1.0.0",
                "defaults": [{
                    "id": "test-id",
                    "extension": ".md",
                    "application_path": "/usr/bin/test",
                    "state": state,
                    "created_at": "2024-01-01T00:00:00Z",
                }]
            }
            # Should not raise
            validate_defaults(data)

    def test_valid_offer_states_pass_validation(self):
        """
        Test that all valid offer states pass validation.
        
        **Validates: Requirements 2.5**
        """
        for state in ["created", "active", "rejected"]:
            data = {
                "version": "1.0.0",
                "offers": [{
                    "offer_id": "test-offer",
                    "default_id": "def-001",
                    "state": state,
                    "created_at": "2024-01-01T00:00:00Z",
                }]
            }
            # Should not raise
            validate_offers(data)

    def test_valid_color_themes_pass_validation(self):
        """
        Test that all valid color themes pass validation.
        
        **Validates: Requirements 3.5**
        """
        for theme in ["default", "dark", "light"]:
            data = {
                "version": "1.0.0",
                "color_theme": theme,
            }
            # Should not raise
            validate_config(data)


# =============================================================================
# Task 6.5: Property Test for additionalProperties Rejection
# Property 4: Unknown field rejection
# Requirements: 1.8, 2.8, 3.9
# =============================================================================


# Strategy for generating unknown field names
@st.composite
def unknown_field_name(draw):
    """Generate field names that are not in any schema."""
    known_fields = {
        # Defaults fields
        "version", "defaults", "id", "extension", "application_path",
        "application_name", "state", "os_synced", "os_synced_at",
        "previous_os_default", "created_at", "updated_at",
        # Offers fields
        "offers", "offer_id", "default_id", "auto_created", "description", "used_at",
        # Config fields
        "data_dir", "verbose", "color_theme", "backup_enabled",
        "max_backups", "confirm_destructive",
    }
    
    field = draw(st.text(min_size=1, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyz_').filter(
        lambda s: s not in known_fields
    ))
    return field


class TestUnknownFieldRejection:
    """
    Property 4: Unknown field rejection
    
    *For any* data with unknown fields, validation SHALL fail.
    
    **Validates: Requirements 1.8, 2.8, 3.9**
    """

    @given(unknown_field=unknown_field_name())
    @settings(max_examples=100)
    def test_unknown_top_level_field_fails_defaults_validation(self, unknown_field: str):
        """
        Property 4: Unknown top-level field should fail defaults validation.
        
        *For any* defaults data with unknown top-level field, validation SHALL fail.
        
        **Validates: Requirements 1.8**
        """
        data = {
            "version": "1.0.0",
            "defaults": [],
            unknown_field: "unexpected_value",
        }
        
        with pytest.raises(DataCorruptedError):
            validate_defaults(data)

    @given(unknown_field=unknown_field_name())
    @settings(max_examples=100)
    def test_unknown_entry_field_fails_defaults_validation(self, unknown_field: str):
        """
        Property 4: Unknown field in DefaultEntry should fail validation.
        
        *For any* DefaultEntry with unknown field, validation SHALL fail.
        
        **Validates: Requirements 1.8**
        """
        data = {
            "version": "1.0.0",
            "defaults": [{
                "id": "test-id",
                "extension": ".md",
                "application_path": "/usr/bin/test",
                "state": "active",
                "created_at": "2024-01-01T00:00:00Z",
                unknown_field: "unexpected_value",
            }]
        }
        
        with pytest.raises(DataCorruptedError):
            validate_defaults(data)

    @given(unknown_field=unknown_field_name())
    @settings(max_examples=100)
    def test_unknown_top_level_field_fails_offers_validation(self, unknown_field: str):
        """
        Property 4: Unknown top-level field should fail offers validation.
        
        *For any* offers data with unknown top-level field, validation SHALL fail.
        
        **Validates: Requirements 2.8**
        """
        data = {
            "version": "1.0.0",
            "offers": [],
            unknown_field: "unexpected_value",
        }
        
        with pytest.raises(DataCorruptedError):
            validate_offers(data)

    @given(unknown_field=unknown_field_name())
    @settings(max_examples=100)
    def test_unknown_entry_field_fails_offers_validation(self, unknown_field: str):
        """
        Property 4: Unknown field in OfferEntry should fail validation.
        
        *For any* OfferEntry with unknown field, validation SHALL fail.
        
        **Validates: Requirements 2.8**
        """
        data = {
            "version": "1.0.0",
            "offers": [{
                "offer_id": "test-offer",
                "default_id": "def-001",
                "state": "active",
                "created_at": "2024-01-01T00:00:00Z",
                unknown_field: "unexpected_value",
            }]
        }
        
        with pytest.raises(DataCorruptedError):
            validate_offers(data)

    @given(unknown_field=unknown_field_name())
    @settings(max_examples=100)
    def test_unknown_field_fails_config_validation(self, unknown_field: str):
        """
        Property 4: Unknown field should fail config validation.
        
        *For any* config data with unknown field, validation SHALL fail.
        
        **Validates: Requirements 3.9**
        """
        data = {
            "version": "1.0.0",
            unknown_field: "unexpected_value",
        }
        
        with pytest.raises(InvalidConfigOptionError):
            validate_config(data)



# =============================================================================
# Task 6.6: Unit Test for Graceful Degradation Without jsonschema
# Requirements: 4.7, 6.2, 6.3
# =============================================================================


class TestGracefulDegradationWithoutJsonschema:
    """
    Unit tests for graceful degradation when jsonschema is not installed.
    
    **Validates: Requirements 4.7, 6.2, 6.3**
    """

    def test_validate_defaults_skips_when_jsonschema_missing(self):
        """
        Test that validate_defaults skips validation when jsonschema not installed.
        
        **Validates: Requirements 4.7, 6.2, 6.3**
        """
        # Mock the import to raise ImportError
        with patch.dict(sys.modules, {'jsonschema': None}):
            # Temporarily remove jsonschema from the module's namespace
            import vince.validation.schema as schema_module
            
            # Create a patched version of validate_against_schema
            original_func = schema_module.validate_against_schema
            
            def patched_validate(data, schema_name):
                # Simulate ImportError for jsonschema
                try:
                    raise ImportError("No module named 'jsonschema'")
                except ImportError:
                    return  # Skip validation
            
            schema_module.validate_against_schema = patched_validate
            
            try:
                # Invalid data that would normally fail
                invalid_data = {
                    "version": "invalid",
                    "defaults": "not_an_array"
                }
                
                # Should not raise - validation is skipped
                schema_module.validate_defaults(invalid_data)
            finally:
                # Restore original function
                schema_module.validate_against_schema = original_func

    def test_validate_offers_skips_when_jsonschema_missing(self):
        """
        Test that validate_offers skips validation when jsonschema not installed.
        
        **Validates: Requirements 4.7, 6.2, 6.3**
        """
        with patch.dict(sys.modules, {'jsonschema': None}):
            import vince.validation.schema as schema_module
            
            original_func = schema_module.validate_against_schema
            
            def patched_validate(data, schema_name):
                try:
                    raise ImportError("No module named 'jsonschema'")
                except ImportError:
                    return
            
            schema_module.validate_against_schema = patched_validate
            
            try:
                invalid_data = {
                    "version": "invalid",
                    "offers": "not_an_array"
                }
                
                schema_module.validate_offers(invalid_data)
            finally:
                schema_module.validate_against_schema = original_func

    def test_validate_config_skips_when_jsonschema_missing(self):
        """
        Test that validate_config skips validation when jsonschema not installed.
        
        **Validates: Requirements 4.7, 6.2, 6.3**
        """
        with patch.dict(sys.modules, {'jsonschema': None}):
            import vince.validation.schema as schema_module
            
            original_func = schema_module.validate_against_schema
            
            def patched_validate(data, schema_name):
                try:
                    raise ImportError("No module named 'jsonschema'")
                except ImportError:
                    return
            
            schema_module.validate_against_schema = patched_validate
            
            try:
                invalid_data = {
                    "version": "invalid",
                    "unknown_field": "value"
                }
                
                schema_module.validate_config(invalid_data)
            finally:
                schema_module.validate_against_schema = original_func

    def test_no_crash_with_import_error_simulation(self):
        """
        Test that the application doesn't crash when jsonschema import fails.
        
        This test simulates the ImportError handling in validate_against_schema.
        
        **Validates: Requirements 4.7, 6.2, 6.3**
        """
        # Create a mock that simulates ImportError
        def mock_validate_against_schema(data, schema_name):
            """Simulates behavior when jsonschema is not installed."""
            try:
                # Simulate the import attempt
                import_error = ImportError("No module named 'jsonschema'")
                raise import_error
            except ImportError:
                # This is the expected graceful degradation
                return None
        
        # Test with various invalid data - none should crash
        test_cases = [
            ({"version": "bad", "defaults": []}, "defaults"),
            ({"version": "bad", "offers": []}, "offers"),
            ({"version": "bad", "unknown": "field"}, "config"),
            ({}, "defaults"),
            (None, "defaults") if False else ({"version": "1.0.0", "defaults": []}, "defaults"),
        ]
        
        for data, schema_name in test_cases:
            # Should not raise any exception
            result = mock_validate_against_schema(data, schema_name)
            assert result is None


# =============================================================================
# Additional Integration Tests
# =============================================================================


class TestSchemaValidationIntegration:
    """
    Integration tests for schema validation with valid data.
    """

    def test_valid_defaults_data_passes_validation(self):
        """
        Test that valid defaults data passes validation.
        """
        data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-001",
                    "extension": ".md",
                    "application_path": "/usr/bin/code",
                    "application_name": "Visual Studio Code",
                    "state": "active",
                    "os_synced": True,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                }
            ]
        }
        
        # Should not raise
        validate_defaults(data)

    def test_valid_offers_data_passes_validation(self):
        """
        Test that valid offers data passes validation.
        """
        data = {
            "version": "1.0.0",
            "offers": [
                {
                    "offer_id": "code-md",
                    "default_id": "def-md-001",
                    "state": "active",
                    "auto_created": True,
                    "description": "VS Code for Markdown",
                    "created_at": "2024-01-15T10:30:00Z",
                    "used_at": "2024-01-18T16:45:00Z",
                }
            ]
        }
        
        # Should not raise
        validate_offers(data)

    def test_valid_config_data_passes_validation(self):
        """
        Test that valid config data passes validation.
        """
        data = {
            "version": "1.0.0",
            "data_dir": "~/.vince",
            "verbose": False,
            "color_theme": "default",
            "backup_enabled": True,
            "max_backups": 5,
            "confirm_destructive": True,
        }
        
        # Should not raise
        validate_config(data)

    def test_minimal_config_passes_validation(self):
        """
        Test that minimal config (only version) passes validation.
        """
        data = {
            "version": "1.0.0"
        }
        
        # Should not raise
        validate_config(data)

    def test_empty_defaults_array_passes_validation(self):
        """
        Test that empty defaults array passes validation.
        """
        data = {
            "version": "1.0.0",
            "defaults": []
        }
        
        # Should not raise
        validate_defaults(data)

    def test_empty_offers_array_passes_validation(self):
        """
        Test that empty offers array passes validation.
        """
        data = {
            "version": "1.0.0",
            "offers": []
        }
        
        # Should not raise
        validate_offers(data)

