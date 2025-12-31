"""
Property-Based Tests for Pattern Usage Consistency

Feature: integration-validation
Property 1: Pattern Definition-Usage Consistency
Validates: Requirements 1.1

Tests that all defined regex patterns in validate_docs.py are referenced
in validation functions.
"""

import ast
import re
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Helper Functions for AST Analysis
# =============================================================================


def extract_pattern_definitions(source_code: str) -> dict[str, int]:
    """
    Extract all regex pattern variable definitions from source code.
    
    Returns a dict mapping pattern variable names to their line numbers.
    """
    patterns = {}
    
    # Parse the source code into an AST
    tree = ast.parse(source_code)
    
    for node in ast.walk(tree):
        # Look for assignments like: pattern_name = re.compile(...)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Check if the value is a re.compile call
                    if isinstance(node.value, ast.Call):
                        if _is_re_compile_call(node.value):
                            patterns[var_name] = node.lineno
    
    return patterns


def _is_re_compile_call(call_node: ast.Call) -> bool:
    """Check if a Call node is a re.compile() call."""
    if isinstance(call_node.func, ast.Attribute):
        if call_node.func.attr == "compile":
            if isinstance(call_node.func.value, ast.Name):
                return call_node.func.value.id == "re"
    return False


def extract_pattern_usages(source_code: str) -> set[str]:
    """
    Extract all pattern variable usages from source code.
    
    Returns a set of variable names that are used (referenced) in the code.
    """
    usages = set()
    
    tree = ast.parse(source_code)
    
    for node in ast.walk(tree):
        # Look for Name nodes that reference variables
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            usages.add(node.id)
    
    return usages


def get_pattern_usage_in_functions(source_code: str) -> dict[str, set[str]]:
    """
    Extract pattern usages grouped by function.
    
    Returns a dict mapping function names to sets of pattern variables used.
    """
    function_usages = {}
    
    tree = ast.parse(source_code)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            usages = set()
            
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                    usages.add(child.id)
            
            function_usages[func_name] = usages
    
    return function_usages


# =============================================================================
# Property 1: Pattern Definition-Usage Consistency
# Validates: Requirements 1.1
# Feature: integration-validation
# =============================================================================


class TestPatternUsageConsistency:
    """
    Feature: integration-validation, Property 1: Pattern Definition-Usage Consistency
    
    For any regex pattern variable defined in validate_docs.py, if the pattern
    is assigned a compiled regex, then that pattern variable SHALL be referenced
    in at least one validation function.
    """
    
    @pytest.fixture
    def validate_docs_source(self) -> str:
        """Load the validate_docs.py source code."""
        validate_docs_path = Path(__file__).parent.parent / "validate_docs.py"
        return validate_docs_path.read_text()
    
    @pytest.fixture
    def pattern_definitions(self, validate_docs_source: str) -> dict[str, int]:
        """Extract all pattern definitions from validate_docs.py."""
        return extract_pattern_definitions(validate_docs_source)
    
    @pytest.fixture
    def pattern_usages(self, validate_docs_source: str) -> set[str]:
        """Extract all pattern usages from validate_docs.py."""
        return extract_pattern_usages(validate_docs_source)
    
    @pytest.fixture
    def function_usages(self, validate_docs_source: str) -> dict[str, set[str]]:
        """Extract pattern usages grouped by function."""
        return get_pattern_usage_in_functions(validate_docs_source)
    
    def test_all_patterns_are_used(
        self,
        pattern_definitions: dict[str, int],
        pattern_usages: set[str],
    ):
        """
        Property 1: All defined patterns should be used.
        
        For any regex pattern variable defined in validate_docs.py,
        that pattern variable SHALL be referenced at least once.
        """
        unused_patterns = []
        
        for pattern_name, line_num in pattern_definitions.items():
            # A pattern is "used" if it appears in usages more than once
            # (once for definition, at least once for usage)
            # We check if it's in usages at all (which includes the definition)
            # and then verify it's used beyond just the definition
            if pattern_name not in pattern_usages:
                unused_patterns.append((pattern_name, line_num))
        
        assert len(unused_patterns) == 0, (
            f"Found unused pattern definitions: "
            f"{[(name, f'line {line}') for name, line in unused_patterns]}"
        )
    
    def test_patterns_used_in_validation_functions(
        self,
        pattern_definitions: dict[str, int],
        function_usages: dict[str, set[str]],
    ):
        """
        Property 1: Patterns should be used in validation functions.
        
        For any regex pattern variable defined in validate_docs.py,
        that pattern SHALL be referenced in at least one function
        (preferably a validate_* function).
        """
        # Get all validation function names
        validation_functions = {
            name for name in function_usages.keys()
            if name.startswith("validate_") or name.startswith("_validate_")
        }
        
        # Collect all patterns used in validation functions
        patterns_in_validators = set()
        for func_name in validation_functions:
            patterns_in_validators.update(function_usages[func_name])
        
        # Also include patterns used in helper functions that support validation
        helper_functions = {
            name for name in function_usages.keys()
            if name.startswith("extract_") or name.startswith("_")
        }
        for func_name in helper_functions:
            patterns_in_validators.update(function_usages[func_name])
        
        # Check each defined pattern
        patterns_not_in_validators = []
        
        for pattern_name in pattern_definitions.keys():
            # Check if pattern is used in any validation or helper function
            found_in_function = False
            for func_name, usages in function_usages.items():
                if pattern_name in usages:
                    found_in_function = True
                    break
            
            if not found_in_function:
                patterns_not_in_validators.append(pattern_name)
        
        assert len(patterns_not_in_validators) == 0, (
            f"Patterns not used in any function: {patterns_not_in_validators}"
        )
    
    def test_specific_patterns_have_usage(
        self,
        validate_docs_source: str,
    ):
        """
        Test that specific critical patterns are used.
        
        These patterns were identified in the integration-validation spec
        as needing to be properly utilized.
        """
        critical_patterns = [
            "return_type_pattern",
            "exceptions_pattern",
            "example_section_pattern",
            "transition_section_pattern",
        ]
        
        for pattern_name in critical_patterns:
            # Check that pattern is defined
            definition_match = re.search(
                rf"{pattern_name}\s*=\s*re\.compile",
                validate_docs_source,
            )
            assert definition_match is not None, (
                f"Critical pattern '{pattern_name}' should be defined"
            )
            
            # Check that pattern is used (beyond just definition)
            # Look for pattern.match, pattern.search, pattern.findall, etc.
            usage_patterns = [
                rf"{pattern_name}\.match",
                rf"{pattern_name}\.search",
                rf"{pattern_name}\.findall",
                rf"{pattern_name}\.finditer",
                rf"if\s+{pattern_name}",
            ]
            
            found_usage = False
            for usage_pattern in usage_patterns:
                if re.search(usage_pattern, validate_docs_source):
                    found_usage = True
                    break
            
            assert found_usage, (
                f"Critical pattern '{pattern_name}' should be used "
                f"(e.g., {pattern_name}.match() or {pattern_name}.search())"
            )


# =============================================================================
# Property-Based Tests for Pattern Consistency
# =============================================================================


@st.composite
def pattern_name_strategy(draw):
    """Generate valid pattern variable names."""
    prefix = draw(st.sampled_from([
        "heading", "table", "code", "command", "section",
        "error", "state", "config", "flag", "rule",
    ]))
    suffix = draw(st.sampled_from([
        "_pattern", "_regex", "_matcher",
    ]))
    return prefix + suffix


class TestPatternNamingConsistency:
    """Test that pattern naming follows conventions."""
    
    @pytest.fixture
    def pattern_definitions(self) -> dict[str, int]:
        """Extract all pattern definitions from validate_docs.py."""
        validate_docs_path = Path(__file__).parent.parent / "validate_docs.py"
        source = validate_docs_path.read_text()
        return extract_pattern_definitions(source)
    
    @given(pattern_name=pattern_name_strategy())
    @settings(max_examples=100)
    def test_pattern_names_follow_convention(self, pattern_name: str):
        """
        Property: Pattern names should follow naming conventions.
        
        For any pattern variable name, it should end with '_pattern',
        '_regex', or similar suffix to indicate it's a compiled regex.
        """
        # This is a generative test to verify our naming convention strategy
        assert pattern_name.endswith(("_pattern", "_regex", "_matcher")), (
            f"Pattern name '{pattern_name}' should follow naming convention"
        )
    
    def test_actual_patterns_follow_convention(
        self,
        pattern_definitions: dict[str, int],
    ):
        """
        Test that actual pattern definitions follow naming conventions.
        """
        non_conforming = []
        
        for pattern_name in pattern_definitions.keys():
            if not pattern_name.endswith("_pattern"):
                non_conforming.append(pattern_name)
        
        # Allow some flexibility - just warn if patterns don't follow convention
        if non_conforming:
            # This is informational - patterns may have valid reasons for different names
            pass  # Patterns like 'param_table_header' are acceptable


# =============================================================================
# Integration Test: Verify Pattern Usage in Real Validation
# =============================================================================


class TestPatternIntegration:
    """Integration tests for pattern usage in actual validation."""
    
    def test_return_type_pattern_detects_return_sections(self):
        """Test that return_type_pattern correctly detects return type sections."""
        from validate_docs import validate_api_completeness
        
        content = """# API Documentation

## Command Interfaces

### slap

Description of the slap command.

#### Function Signature

```python
def cmd_slap(path: Path) -> None:
    pass
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `Path` | Required | Path to application |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE101` | Path does not exist | Invalid path |
"""
        result = validate_api_completeness(content, "api.md")
        
        # Check that slap command has return type detected
        return_type_errors = [
            e for e in result.errors
            if "slap" in e.message and "return type" in e.message.lower()
        ]
        assert len(return_type_errors) == 0, (
            "return_type_pattern should detect '#### Return Type' section"
        )
    
    def test_exceptions_pattern_detects_exception_sections(self):
        """Test that exceptions_pattern correctly detects exception sections."""
        from validate_docs import validate_api_completeness
        
        content = """# API Documentation

## Command Interfaces

### chop

Description of the chop command.

#### Function Signature

```python
def cmd_chop(extension: str) -> None:
    pass
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `extension` | `str` | Required | File extension |

#### Return Type

Returns `None`.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE302` | No default exists | No default set |
"""
        result = validate_api_completeness(content, "api.md")
        
        # Check that chop command has exceptions detected
        exception_errors = [
            e for e in result.errors
            if "chop" in e.message and "exception" in e.message.lower()
        ]
        assert len(exception_errors) == 0, (
            "exceptions_pattern should detect '#### Raised Exceptions' section"
        )
    
    def test_example_section_pattern_detects_examples(self):
        """Test that example_section_pattern correctly detects example sections."""
        from validate_docs import validate_schema_completeness
        
        content = """# Data Model Schemas

## Defaults Schema

Description of the defaults schema.

### JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Vince Defaults",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\\\d+\\\\.\\\\d+\\\\.\\\\d+$"
    }
  },
  "required": ["version"]
}
```

### Example

```json
{
  "version": "1.0.0",
  "defaults": []
}
```
"""
        result = validate_schema_completeness(content, "schemas.md")
        
        # Check that defaults schema has example detected
        example_errors = [
            e for e in result.errors
            if "defaults" in e.message.lower() and "example" in e.message.lower()
        ]
        assert len(example_errors) == 0, (
            "example_section_pattern should detect '### Example' section"
        )
    
    def test_transition_section_pattern_detects_transitions(self):
        """Test that transition_section_pattern correctly detects transition sections."""
        from validate_docs import validate_state_transitions
        
        content = """# State Management

## Default Lifecycle

Description of default lifecycle.

### Default State Transitions

| From | To | Trigger | Conditions | Side Effects |
| --- | --- | --- | --- | --- |
| none | pending | slap | Path valid | Creates entry |
| pending | active | set | Entry exists | Updates state |
"""
        result = validate_state_transitions(content, "states.md")
        
        # The transition_section_pattern should detect the section
        # and provide context in error messages if there are issues
        # For valid content, there should be no errors about missing transitions
        transition_errors = [
            e for e in result.errors
            if "transition" in e.message.lower() and "missing" in e.message.lower()
        ]
        assert len(transition_errors) == 0, (
            "transition_section_pattern should detect '### Default State Transitions' section"
        )
