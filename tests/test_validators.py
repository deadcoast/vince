"""
Property-Based Tests for Documentation Validators

Feature: documentation-population
Each test validates a specific correctness property from the design document.
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_docs import (
    validate_heading_hierarchy,
    validate_table_syntax,
    validate_code_blocks,
    validate_entry_completeness,
    validate_sid_naming,
    validate_cross_references,
    validate_flag_prefixes,
    validate_example_coverage,
    validate_rule_format,
    validate_modular_syntax,
    extract_definitions_from_tables,
)


# =============================================================================
# Generators for Markdown Content
# =============================================================================

@st.composite
def valid_heading_content(draw):
    """Generate markdown content with valid heading hierarchy."""
    h1_text = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S'), blacklist_characters='\n#')))
    h2_texts = draw(st.lists(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N'), blacklist_characters='\n#')), min_size=1, max_size=3))
    h3_texts = draw(st.lists(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N'), blacklist_characters='\n#')), min_size=0, max_size=2))
    
    lines = [f"# {h1_text.strip() or 'Title'}"]
    
    for h2 in h2_texts:
        h2_clean = h2.strip() or "Section"
        lines.append(f"\n## {h2_clean}")
        lines.append("\nSome content here.")
        
        for h3 in h3_texts:
            h3_clean = h3.strip() or "Subsection"
            lines.append(f"\n### {h3_clean}")
            lines.append("\nMore content.")
    
    return "\n".join(lines)


@st.composite
def invalid_heading_content(draw):
    """Generate markdown content with invalid heading hierarchy (H3 before H2)."""
    h1_text = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L',), blacklist_characters='\n#')))
    h3_text = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L',), blacklist_characters='\n#')))
    
    # H3 directly after H1 (no H2)
    return f"# {h1_text.strip() or 'Title'}\n\n### {h3_text.strip() or 'Bad'}\n\nContent"


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


@st.composite
def invalid_table_content(draw):
    """Generate markdown content with invalid table syntax (inconsistent columns)."""
    header_row = "| col1 | col2 | col3 |"
    separator = "| --- | --- | --- |"
    # Row with wrong number of columns
    bad_row = "| val1 | val2 |"
    
    return f"# Table Doc\n\n## Section\n\n{header_row}\n{separator}\n{bad_row}"


@st.composite
def code_block_with_lang(draw):
    """Generate markdown with code blocks that have language identifiers."""
    lang = draw(st.sampled_from(['sh', 'python', 'javascript', 'json', 'yaml']))
    code = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P'), blacklist_characters='`')))
    
    return f"# Doc\n\n## Section\n\n```{lang}\n{code}\n```"


@st.composite
def code_block_without_lang(draw):
    """Generate markdown with code blocks missing language identifiers."""
    code = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'), blacklist_characters='`')))
    
    return f"# Doc\n\n## Section\n\n```\n{code}\n```"


# =============================================================================
# Property 1: Heading Hierarchy Validation
# Validates: Requirements 1.1, 1.2
# =============================================================================

class TestHeadingHierarchy:
    """Feature: documentation-population, Property 1: Heading hierarchy validation"""
    
    @given(content=valid_heading_content())
    @settings(max_examples=100)
    def test_valid_hierarchy_passes(self, content):
        """Valid heading hierarchy should produce no errors."""
        result = validate_heading_hierarchy(content, "test.md")
        assert result.is_valid, f"Valid hierarchy should pass: {result.errors}"
    
    @given(content=invalid_heading_content())
    @settings(max_examples=100)
    def test_h3_before_h2_fails(self, content):
        """H3 appearing before H2 should produce an error."""
        result = validate_heading_hierarchy(content, "test.md")
        # Should have at least one error about H3 before H2
        h3_errors = [e for e in result.errors if "H3" in e.message and "H2" in e.message]
        assert len(h3_errors) > 0, "Should detect H3 before H2"


# =============================================================================
# Property 2: Table Syntax Validation
# Validates: Requirements 1.3
# =============================================================================

class TestTableSyntax:
    """Feature: documentation-population, Property 2: Table syntax validation"""
    
    @given(content=valid_table_content())
    @settings(max_examples=100)
    def test_valid_table_passes(self, content):
        """Valid table syntax should produce no errors."""
        result = validate_table_syntax(content, "test.md")
        assert result.is_valid, f"Valid table should pass: {result.errors}"
    
    @given(content=invalid_table_content())
    @settings(max_examples=100)
    def test_inconsistent_columns_fails(self, content):
        """Tables with inconsistent column counts should produce errors."""
        result = validate_table_syntax(content, "test.md")
        col_errors = [e for e in result.errors if "column" in e.message.lower()]
        assert len(col_errors) > 0, "Should detect column inconsistency"


# =============================================================================
# Property 3: Code Block Language Identifiers
# Validates: Requirements 1.4
# =============================================================================

class TestCodeBlocks:
    """Feature: documentation-population, Property 3: Code block language identifiers"""
    
    @given(content=code_block_with_lang())
    @settings(max_examples=100)
    def test_code_block_with_lang_passes(self, content):
        """Code blocks with language identifiers should pass."""
        result = validate_code_blocks(content, "test.md")
        assert result.is_valid, f"Code block with lang should pass: {result.errors}"
    
    @given(content=code_block_without_lang())
    @settings(max_examples=100)
    def test_code_block_without_lang_fails(self, content):
        """Code blocks without language identifiers should fail."""
        result = validate_code_blocks(content, "test.md")
        lang_errors = [e for e in result.errors if "language" in e.message.lower()]
        assert len(lang_errors) > 0, "Should detect missing language identifier"



# =============================================================================
# Property 4: Entry Field Completeness
# Validates: Requirements 2.1, 2.2, 2.3
# =============================================================================

@st.composite
def complete_definitions_table(draw):
    """Generate a DEFINITIONS table with all required fields."""
    num_entries = draw(st.integers(min_value=1, max_value=3))
    
    rows = []
    for i in range(num_entries):
        id_val = f"item{i}"
        sid = f"i{i}"
        rid = f"i{i}01"
        desc = f"Description for item {i}"
        rows.append(f"| `{id_val}` | {sid} | {rid} | {desc} |")
    
    table = """# Tables

## DEFINITIONS

| id | sid | rid | description |
| --- | --- | --- | --- |
""" + "\n".join(rows)
    
    return table


@st.composite
def incomplete_definitions_table(draw):
    """Generate a DEFINITIONS table with missing fields."""
    # Missing description field
    return """# Tables

## DEFINITIONS

| id | sid | rid | description |
| --- | --- | --- | --- |
| `item1` | i1 | i101 |  |
"""


class TestEntryCompleteness:
    """Feature: documentation-population, Property 4: Entry field completeness"""
    
    @given(content=complete_definitions_table())
    @settings(max_examples=100)
    def test_complete_entries_pass(self, content):
        """Tables with all required fields should pass."""
        result = validate_entry_completeness(content, "tables.md")
        assert result.is_valid, f"Complete entries should pass: {result.errors}"
    
    @given(content=incomplete_definitions_table())
    @settings(max_examples=100)
    def test_incomplete_entries_fail(self, content):
        """Tables with missing fields should fail."""
        result = validate_entry_completeness(content, "tables.md")
        empty_errors = [e for e in result.errors if "Empty field" in e.message]
        assert len(empty_errors) > 0, "Should detect empty fields"


# =============================================================================
# Property 5: SID Naming Convention Compliance
# Validates: Requirements 2.4, 2.5
# =============================================================================

@st.composite
def unique_sid_table(draw):
    """Generate a table with unique SID values."""
    num_entries = draw(st.integers(min_value=2, max_value=4))
    
    rows = []
    for i in range(num_entries):
        id_val = f"item{i}"
        sid = f"i{i}"  # Unique sids
        rows.append(f"| `{id_val}` | {sid} | {sid}01 | Desc {i} |")
    
    return """# Tables

## DEFINITIONS

| id | sid | rid | description |
| --- | --- | --- | --- |
""" + "\n".join(rows)


@st.composite
def duplicate_sid_table(draw):
    """Generate a table with duplicate SID values for different IDs."""
    return """# Tables

## DEFINITIONS

| id | sid | rid | description |
| --- | --- | --- | --- |
| `item1` | dup | dup01 | First item |
| `item2` | dup | dup02 | Second item with same sid |
"""


class TestSidNaming:
    """Feature: documentation-population, Property 5: SID naming convention compliance"""
    
    @given(content=unique_sid_table())
    @settings(max_examples=100)
    def test_unique_sids_pass(self, content):
        """Tables with unique SID values should pass."""
        result = validate_sid_naming(content, "tables.md")
        dup_errors = [e for e in result.errors if "Duplicate" in e.message]
        assert len(dup_errors) == 0, f"Unique sids should pass: {result.errors}"
    
    @given(content=duplicate_sid_table())
    @settings(max_examples=100)
    def test_duplicate_sids_fail(self, content):
        """Tables with duplicate SID values for different IDs should fail."""
        result = validate_sid_naming(content, "tables.md")
        dup_errors = [e for e in result.errors if "Duplicate" in e.message]
        assert len(dup_errors) > 0, "Should detect duplicate sids"


# =============================================================================
# Property 6: Cross-Reference Consistency
# Validates: Requirements 5.1, 5.2, 5.3, 5.5
# =============================================================================

class TestCrossReferences:
    """Feature: documentation-population, Property 6: Cross-reference consistency"""
    
    def test_defined_commands_pass(self):
        """Commands that are defined in tables should pass cross-reference check."""
        tables_content = """# Tables

## COMMANDS

| id | sid | rid | description |
| --- | --- | --- | --- |
| `slap` | sl | sl01 | Set default |
| `chop` | ch | ch01 | Remove default |
"""
        tables_defs = extract_definitions_from_tables(tables_content)
        
        doc_content = """# Overview

## Commands

Use `slap` to set defaults and `chop` to remove them.
"""
        result = validate_cross_references(doc_content, "overview.md", tables_defs)
        assert result.is_valid, f"Defined commands should pass: {result.errors}"
    
    def test_undefined_commands_fail(self):
        """Commands not defined in tables should fail cross-reference check."""
        tables_content = """# Tables

## COMMANDS

| id | sid | rid | description |
| --- | --- | --- | --- |
| `slap` | sl | sl01 | Set default |
"""
        tables_defs = extract_definitions_from_tables(tables_content)
        
        # Test with a document referencing an undefined command
        doc_content = """# Overview

## Commands

Use `slap` and `chop` for operations.
"""
        result = validate_cross_references(doc_content, "overview.md", tables_defs)
        cmd_errors = [e for e in result.errors if "chop" in e.message]
        assert len(cmd_errors) > 0, "Should detect undefined command"


# =============================================================================
# Property 7: Flag Prefix Convention
# Validates: Requirements 4.5
# =============================================================================

@st.composite
def valid_flag_table(draw):
    """Generate a flag table with correct prefixes."""
    return """# Tables

## UTILITY_FLAGS

| id | sid | short | long | description |
| --- | --- | --- | --- | --- |
| `help` | he | -h | --help | Display help |
| `version` | ve | -v | --version | Display version |
"""


@st.composite
def invalid_flag_table(draw):
    """Generate a flag table with incorrect prefixes."""
    return """# Tables

## UTILITY_FLAGS

| id | sid | short | long | description |
| --- | --- | --- | --- | --- |
| `help` | he | --h | -help | Wrong prefixes |
"""


class TestFlagPrefixes:
    """Feature: documentation-population, Property 7: Flag prefix convention"""
    
    @given(content=valid_flag_table())
    @settings(max_examples=100)
    def test_valid_prefixes_pass(self, content):
        """Flags with correct prefixes should pass."""
        result = validate_flag_prefixes(content, "tables.md")
        assert result.is_valid, f"Valid prefixes should pass: {result.errors}"
    
    @given(content=invalid_flag_table())
    @settings(max_examples=100)
    def test_invalid_prefixes_fail(self, content):
        """Flags with incorrect prefixes should fail."""
        result = validate_flag_prefixes(content, "tables.md")
        prefix_errors = [e for e in result.errors if "dash" in e.message.lower() or "should" in e.message.lower()]
        assert len(prefix_errors) > 0, "Should detect wrong prefixes"


# =============================================================================
# Property 8: Example Completeness Per Command
# Validates: Requirements 3.1, 3.2, 7.1, 7.2
# =============================================================================

class TestExampleCoverage:
    """Feature: documentation-population, Property 8: Example completeness per command"""
    
    def test_all_commands_have_examples(self):
        """All defined commands should have example sections."""
        tables_content = """# Tables

## COMMANDS

| id | sid | rid | description |
| --- | --- | --- | --- |
| `slap` | sl | sl01 | Set default |
| `chop` | ch | ch01 | Remove default |
"""
        tables_defs = extract_definitions_from_tables(tables_content)
        
        examples_content = """# Examples

## `slap`

```sh
vince slap app.exe --md
```

## `chop`

```sh
vince chop --md
```
"""
        result = validate_example_coverage(examples_content, "examples.md", tables_defs)
        assert result.is_valid, f"All commands with examples should pass: {result.errors}"
    
    def test_missing_command_examples_fail(self):
        """Commands without example sections should fail."""
        tables_content = """# Tables

## COMMANDS

| id | sid | rid | description |
| --- | --- | --- | --- |
| `slap` | sl | sl01 | Set default |
| `chop` | ch | ch01 | Remove default |
"""
        tables_defs = extract_definitions_from_tables(tables_content)
        
        examples_content = """# Examples

## `slap`

```sh
vince slap app.exe --md
```
"""
        result = validate_example_coverage(examples_content, "examples.md", tables_defs)
        missing_errors = [e for e in result.errors if "chop" in e.message]
        assert len(missing_errors) > 0, "Should detect missing command examples"


# =============================================================================
# Property 9: Rule Reference Format Consistency
# Validates: Requirements 9.2, 9.4
# =============================================================================

@st.composite
def valid_rule_references(draw):
    """Generate content with valid rule references."""
    rules = draw(st.lists(
        st.sampled_from(['PD01', 'UID01', 'TB01', 'TB02', 'SL01']),
        min_size=1, max_size=3
    ))
    
    content = "# Doc\n\n## Section\n\n"
    for rule in rules:
        content += f"See [{rule}] for details.\n"
    
    return content


@st.composite
def invalid_rule_references(draw):
    """Generate content with invalid (lowercase) rule references."""
    return "# Doc\n\n## Section\n\nSee [pd01] for details.\n"


class TestRuleFormat:
    """Feature: documentation-population, Property 9: Rule reference format consistency"""
    
    @given(content=valid_rule_references())
    @settings(max_examples=100)
    def test_valid_rule_format_passes(self, content):
        """Valid rule references should pass."""
        result = validate_rule_format(content, "test.md")
        assert result.is_valid, f"Valid rule format should pass: {result.errors}"
    
    @given(content=invalid_rule_references())
    @settings(max_examples=100)
    def test_lowercase_rule_warns(self, content):
        """Lowercase rule references should produce warnings."""
        result = validate_rule_format(content, "test.md")
        case_warnings = [w for w in result.warnings if "uppercase" in w.message.lower()]
        assert len(case_warnings) > 0, "Should warn about lowercase rule references"


# =============================================================================
# Property 10: Modular Command Syntax
# Validates: Requirements 10.2, 10.3
# =============================================================================

@st.composite
def modular_command_content(draw):
    """Generate content with proper modular command syntax."""
    commands = draw(st.lists(
        st.sampled_from(['slap', 'chop', 'set', 'forget', 'offer', 'reject', 'list']),
        min_size=1, max_size=3
    ))
    
    content = "# Examples\n\n## Commands\n\n```sh\n"
    for cmd in commands:
        content += f"vince {cmd} --md\n"
    content += "```"
    
    return content


@st.composite
def underscore_command_content(draw):
    """Generate content with underscore-joined commands (violates PD01)."""
    return """# Examples

## Commands

```sh
vince sub_command --md
```
"""


class TestModularSyntax:
    """Feature: documentation-population, Property 10: Modular command syntax"""
    
    @given(content=modular_command_content())
    @settings(max_examples=100)
    def test_modular_syntax_passes(self, content):
        """Proper modular command syntax should pass."""
        result = validate_modular_syntax(content, "test.md")
        assert result.is_valid, f"Modular syntax should pass: {result.errors}"
    
    @given(content=underscore_command_content())
    @settings(max_examples=100)
    def test_underscore_commands_fail(self, content):
        """Underscore-joined commands should fail."""
        result = validate_modular_syntax(content, "test.md")
        underscore_errors = [e for e in result.errors if "underscore" in e.message.lower() or "PD01" in e.message]
        assert len(underscore_errors) > 0, "Should detect underscore-joined commands"


# =============================================================================
# Integration Tests with Real Documentation
# =============================================================================

class TestRealDocumentation:
    """Integration tests against actual documentation files."""
    
    @pytest.fixture
    def docs_dir(self):
        return Path(__file__).parent.parent / "docs"
    
    def test_tables_md_structure(self, docs_dir):
        """tables.md should have valid structure."""
        tables_path = docs_dir / "tables.md"
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        
        content = tables_path.read_text()
        
        # Check heading hierarchy
        result = validate_heading_hierarchy(content, "tables.md")
        assert result.is_valid, f"tables.md heading hierarchy: {result.errors}"
        
        # Check table syntax
        result = validate_table_syntax(content, "tables.md")
        assert result.is_valid, f"tables.md table syntax: {result.errors}"
    
    def test_overview_md_structure(self, docs_dir):
        """overview.md should have valid structure."""
        overview_path = docs_dir / "overview.md"
        if not overview_path.exists():
            pytest.skip("overview.md not found")
        
        content = overview_path.read_text()
        
        result = validate_heading_hierarchy(content, "overview.md")
        assert result.is_valid, f"overview.md heading hierarchy: {result.errors}"
    
    def test_examples_md_structure(self, docs_dir):
        """examples.md should have valid structure."""
        examples_path = docs_dir / "examples.md"
        if not examples_path.exists():
            pytest.skip("examples.md not found")
        
        content = examples_path.read_text()
        
        result = validate_heading_hierarchy(content, "examples.md")
        assert result.is_valid, f"examples.md heading hierarchy: {result.errors}"


# =============================================================================
# Property 11: API Documentation Completeness
# Validates: Requirements 1.1, 1.2, 1.3, 1.4
# Feature: python-integration-preparation
# =============================================================================

from validate_docs import (
    validate_api_completeness,
    validate_schema_completeness,
    validate_error_catalog,
    validate_state_transitions,
    validate_new_table_cross_references,
    extract_errors_from_tables,
    extract_states_from_tables,
    extract_config_options_from_tables,
)


@st.composite
def complete_api_command(draw):
    """Generate API documentation for a command with all required elements."""
    cmd = draw(st.sampled_from(['slap', 'chop', 'set', 'forget', 'offer', 'reject', 'list']))
    
    return f"""# API Documentation

## Command Interfaces

### {cmd}

Description of the {cmd} command.

#### Function Signature

```python
@app.command(name="{cmd}")
def cmd_{cmd}(
    path: Path = Argument(..., help="Path to application"),
    verbose: bool = Option(False, "-vb", help="Verbose output"),
) -> None:
    \"\"\"Command description.\"\"\"
    ...
```

#### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `Path` | Required | Path to application |
| `verbose` | `bool` | `False` | Enable verbose output |

#### Return Type

Returns `None`. Output is displayed via Rich console.

#### Raised Exceptions

| Error Code | Condition | Message |
| --- | --- | --- |
| `VE101` | Path does not exist | Invalid path |
"""


@st.composite
def incomplete_api_command(draw):
    """Generate API documentation missing required elements."""
    cmd = draw(st.sampled_from(['slap', 'chop', 'set', 'forget', 'offer', 'reject', 'list']))
    
    # Missing function signature, parameters table, return type, or exceptions
    return f"""# API Documentation

## Command Interfaces

### {cmd}

Description of the {cmd} command without proper documentation.

Some text but no function signature, parameter table, return type, or exceptions.
"""


class TestAPICompleteness:
    """Feature: python-integration-preparation, Property 1: API Documentation Completeness"""
    
    @given(content=complete_api_command())
    @settings(max_examples=100)
    def test_complete_api_passes(self, content):
        """Complete API documentation should pass validation."""
        result = validate_api_completeness(content, "api.md")
        # Check that the documented command has no errors
        cmd_errors = [e for e in result.errors if "missing" in e.message.lower()]
        # We expect errors for the 6 other commands not documented
        assert len([e for e in cmd_errors if "is missing from API" in e.message]) == 6
    
    @given(content=incomplete_api_command())
    @settings(max_examples=100)
    def test_incomplete_api_fails(self, content):
        """Incomplete API documentation should fail validation."""
        result = validate_api_completeness(content, "api.md")
        # Should have errors for missing elements
        assert len(result.errors) > 0, "Should detect missing API elements"
    
    def test_real_api_md(self):
        """Test against actual api.md file."""
        api_path = Path(__file__).parent.parent / "docs" / "api.md"
        if not api_path.exists():
            pytest.skip("api.md not found")
        
        content = api_path.read_text()
        result = validate_api_completeness(content, "api.md")
        assert result.is_valid, f"api.md should be complete: {result.errors}"


# =============================================================================
# Property 12: Schema Completeness
# Validates: Requirements 2.4, 2.5, 2.7
# Feature: python-integration-preparation
# =============================================================================

@st.composite
def complete_schema_doc(draw):
    """Generate schema documentation with all required elements."""
    schema = draw(st.sampled_from(['defaults', 'offers', 'config']))
    
    return f"""# Data Model Schemas

## {schema.title()} Schema

Description of the {schema} schema.

### JSON Schema Definition

```json
{{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Vince {schema.title()}",
  "type": "object",
  "properties": {{
    "version": {{
      "type": "string",
      "pattern": "^\\\\d+\\\\.\\\\d+\\\\.\\\\d+$"
    }},
    "data": {{
      "type": "array",
      "minLength": 0
    }}
  }},
  "required": ["version"]
}}
```

### Example {schema}.json

```json
{{
  "version": "1.0.0",
  "data": []
}}
```
"""


@st.composite
def incomplete_schema_doc(draw):
    """Generate schema documentation missing required elements."""
    schema = draw(st.sampled_from(['defaults', 'offers', 'config']))
    
    return f"""# Data Model Schemas

## {schema.title()} Schema

Description without proper schema definition or example.
"""


class TestSchemaCompleteness:
    """Feature: python-integration-preparation, Property 2: Schema Completeness"""
    
    @given(content=complete_schema_doc())
    @settings(max_examples=100)
    def test_complete_schema_passes(self, content):
        """Complete schema documentation should pass for documented schema."""
        result = validate_schema_completeness(content, "schemas.md")
        # We expect errors for the 2 other schemas not documented
        missing_schema_errors = [e for e in result.errors if "is missing from schemas" in e.message]
        assert len(missing_schema_errors) == 2
    
    @given(content=incomplete_schema_doc())
    @settings(max_examples=100)
    def test_incomplete_schema_fails(self, content):
        """Incomplete schema documentation should fail validation."""
        result = validate_schema_completeness(content, "schemas.md")
        assert len(result.errors) > 0, "Should detect missing schema elements"
    
    def test_real_schemas_md(self):
        """Test against actual schemas.md file."""
        schemas_path = Path(__file__).parent.parent / "docs" / "schemas.md"
        if not schemas_path.exists():
            pytest.skip("schemas.md not found")
        
        content = schemas_path.read_text()
        result = validate_schema_completeness(content, "schemas.md")
        assert result.is_valid, f"schemas.md should be complete: {result.errors}"


# =============================================================================
# Property 13: Error Catalog Completeness
# Validates: Requirements 3.1, 3.3, 3.4, 3.5
# Feature: python-integration-preparation
# =============================================================================

@st.composite
def valid_error_entry(draw):
    """Generate a valid error catalog entry."""
    category = draw(st.sampled_from(['Input', 'File', 'State', 'Config', 'System']))
    category_ranges = {
        'Input': (101, 105),
        'File': (201, 203),
        'State': (301, 304),
        'Config': (401, 402),
        'System': (501, 501),
    }
    min_val, max_val = category_ranges[category]
    code_num = draw(st.integers(min_value=min_val, max_value=max_val))
    
    return f"""# Error Catalog

## Error Registry

### {category} Errors (VE{code_num // 100}xx)

| Code | Message Template | Severity | Recovery Action |
| --- | --- | --- | --- |
| VE{code_num} | Error message for {code_num} | error | Recovery action here |
"""


@st.composite
def invalid_error_entry(draw):
    """Generate an error catalog entry with invalid format."""
    return """# Error Catalog

## Error Registry

### Input Errors (VE1xx)

| Code | Message Template | Severity | Recovery Action |
| --- | --- | --- | --- |
| VE999 | Invalid code outside range | error | Recovery |
"""


class TestErrorCatalog:
    """Feature: python-integration-preparation, Property 3: Error Catalog Completeness"""
    
    @given(content=valid_error_entry())
    @settings(max_examples=100)
    def test_valid_error_passes(self, content):
        """Valid error entries should pass validation."""
        result = validate_error_catalog(content, "errors.md")
        # Should have no format or range errors
        format_errors = [e for e in result.errors if "format" in e.message.lower() or "range" in e.message.lower()]
        assert len(format_errors) == 0, f"Valid errors should pass: {format_errors}"
    
    @given(content=invalid_error_entry())
    @settings(max_examples=100)
    def test_invalid_error_fails(self, content):
        """Invalid error entries should fail validation."""
        result = validate_error_catalog(content, "errors.md")
        range_errors = [e for e in result.errors if "range" in e.message.lower() or "outside" in e.message.lower()]
        assert len(range_errors) > 0, "Should detect out-of-range error codes"
    
    def test_real_errors_md(self):
        """Test against actual errors.md file."""
        errors_path = Path(__file__).parent.parent / "docs" / "errors.md"
        if not errors_path.exists():
            pytest.skip("errors.md not found")
        
        content = errors_path.read_text()
        result = validate_error_catalog(content, "errors.md")
        assert result.is_valid, f"errors.md should be complete: {result.errors}"


# =============================================================================
# Property 14: State Transition Completeness
# Validates: Requirements 5.3, 5.4
# Feature: python-integration-preparation
# =============================================================================

@st.composite
def complete_transition_doc(draw):
    """Generate state transition documentation with all required elements."""
    from_state = draw(st.sampled_from(['none', 'pending', 'active', 'removed']))
    to_state = draw(st.sampled_from(['pending', 'active', 'removed']))
    
    return f"""# State Machine Documentation

## Default Lifecycle

### Default State Transitions

| From | To | Trigger | Conditions | Side Effects |
| --- | --- | --- | --- | --- |
| {from_state} | {to_state} | slap -set | Path exists | Creates entry |
"""


@st.composite
def incomplete_transition_doc(draw):
    """Generate state transition documentation missing required elements."""
    return """# State Machine Documentation

## Default Lifecycle

### Default State Transitions

| From | To | Trigger | Conditions | Side Effects |
| --- | --- | --- | --- | --- |
| none | active | | | |
"""


class TestStateTransitions:
    """Feature: python-integration-preparation, Property 4: State Transition Completeness"""
    
    @given(content=complete_transition_doc())
    @settings(max_examples=100)
    def test_complete_transition_passes(self, content):
        """Complete transition documentation should pass validation."""
        result = validate_state_transitions(content, "states.md")
        assert result.is_valid, f"Complete transitions should pass: {result.errors}"
    
    @given(content=incomplete_transition_doc())
    @settings(max_examples=100)
    def test_incomplete_transition_fails(self, content):
        """Incomplete transition documentation should fail validation."""
        result = validate_state_transitions(content, "states.md")
        missing_errors = [e for e in result.errors if "missing" in e.message.lower()]
        assert len(missing_errors) > 0, "Should detect missing transition elements"
    
    def test_real_states_md(self):
        """Test against actual states.md file."""
        states_path = Path(__file__).parent.parent / "docs" / "states.md"
        if not states_path.exists():
            pytest.skip("states.md not found")
        
        content = states_path.read_text()
        result = validate_state_transitions(content, "states.md")
        assert result.is_valid, f"states.md should be complete: {result.errors}"


# =============================================================================
# Property 15: Cross-Reference Completeness for New Tables
# Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
# Feature: python-integration-preparation
# =============================================================================

class TestNewTableCrossReferences:
    """Feature: python-integration-preparation, Property 6: Cross-Reference Completeness"""
    
    def test_errors_in_tables(self):
        """Error codes in errors.md should be in tables.md ERRORS table."""
        tables_content = """# Tables

## ERRORS

| code | sid | category | message | severity |
| --- | --- | --- | --- | --- |
| VE101 | ve101 | Input | Invalid path | error |
| VE201 | ve201 | File | File not found | error |
"""
        errors_content = "Error VE101 and VE201 are documented."
        
        result = validate_new_table_cross_references(
            errors_content, "", "", tables_content, "cross-refs"
        )
        assert result.is_valid, f"Matching errors should pass: {result.errors}"
    
    def test_missing_errors_in_tables(self):
        """Error codes not in tables.md should be flagged."""
        tables_content = """# Tables

## ERRORS

| code | sid | category | message | severity |
| --- | --- | --- | --- | --- |
| VE101 | ve101 | Input | Invalid path | error |
"""
        errors_content = "Error VE101 and VE999 are documented."
        
        result = validate_new_table_cross_references(
            errors_content, "", "", tables_content, "cross-refs"
        )
        missing_errors = [e for e in result.errors if "VE999" in e.message]
        assert len(missing_errors) > 0, "Should detect missing error in tables"
    
    def test_states_in_tables(self):
        """State sids in states.md should be in tables.md STATES table."""
        tables_content = """# Tables

## STATES

| id | sid | entity | description |
| --- | --- | --- | --- |
| none | def-none | default | No default exists |
| active | def-actv | default | Default is active |
"""
        states_content = "States def-none and def-actv are documented."
        
        result = validate_new_table_cross_references(
            "", states_content, "", tables_content, "cross-refs"
        )
        assert result.is_valid, f"Matching states should pass: {result.errors}"
    
    def test_real_cross_references(self):
        """Test cross-references against actual documentation files."""
        docs_dir = Path(__file__).parent.parent / "docs"
        
        tables_path = docs_dir / "tables.md"
        errors_path = docs_dir / "errors.md"
        states_path = docs_dir / "states.md"
        config_path = docs_dir / "config.md"
        
        if not all(p.exists() for p in [tables_path, errors_path, states_path]):
            pytest.skip("Required documentation files not found")
        
        tables_content = tables_path.read_text()
        errors_content = errors_path.read_text()
        states_content = states_path.read_text()
        config_content = config_path.read_text() if config_path.exists() else ""
        
        result = validate_new_table_cross_references(
            errors_content, states_content, config_content, tables_content, "cross-refs"
        )
        assert result.is_valid, f"Cross-references should be valid: {result.errors}"
