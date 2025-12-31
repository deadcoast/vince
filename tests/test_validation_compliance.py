"""
Property-Based Tests for Validation Script Compliance

Feature: documentation-unification
Property 2: Validation Script Compliance
Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8

Tests that all documentation files pass the validation script with zero errors.
"""

import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Helper Functions
# =============================================================================


def get_all_doc_files() -> list[str]:
    """
    Get all documentation files that should be validated.
    
    Returns a list of file names that the validation script processes.
    """
    return [
        "tables.md",
        "overview.md",
        "examples.md",
        "README.md",
        "api.md",
        "schemas.md",
        "errors.md",
        "config.md",
        "states.md",
        "testing.md",
    ]


# =============================================================================
# Property 2: Validation Script Compliance
# Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
# Feature: documentation-unification
# =============================================================================


class TestValidationScriptCompliance:
    """
    Feature: documentation-unification, Property 2: Validation Script Compliance
    
    For any documentation file in the docs/ directory, running the complete
    validation script SHALL produce zero errors.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
    """
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    def test_all_docs_pass_validation(self, docs_dir: Path):
        """
        Property 2: All documentation files should pass validation.
        
        Running validate_all_docs() on the docs/ directory SHALL
        produce zero errors.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        # Run full validation
        result = validate_all_docs(docs_dir)
        
        # Should have zero errors
        assert result.is_valid, (
            f"Validation should pass with zero errors. "
            f"Found {len(result.errors)} errors:\n" +
            "\n".join(f"  [{e.rule}] {e.file}:{e.line} - {e.message}" 
                      for e in result.errors[:10])
        )
    
    def test_heading_hierarchy_compliance(self, docs_dir: Path):
        """
        Property 2.1: All docs pass heading hierarchy validations.
        
        THE Documentation_System SHALL pass all heading hierarchy
        validations (Property 1 in validate_docs.py).
        
        **Validates: Requirements 2.1**
        """
        from validate_docs import validate_heading_hierarchy
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        for doc_file in get_all_doc_files():
            file_path = docs_dir / doc_file
            if file_path.exists():
                content = file_path.read_text()
                result = validate_heading_hierarchy(content, doc_file)
                
                assert result.is_valid, (
                    f"Heading hierarchy validation failed for {doc_file}: "
                    f"{[e.message for e in result.errors]}"
                )
    
    def test_table_syntax_compliance(self, docs_dir: Path):
        """
        Property 2.2: All docs pass table syntax validations.
        
        THE Documentation_System SHALL pass all table syntax
        validations (Property 2 in validate_docs.py).
        
        **Validates: Requirements 2.2**
        """
        from validate_docs import validate_table_syntax
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        for doc_file in get_all_doc_files():
            file_path = docs_dir / doc_file
            if file_path.exists():
                content = file_path.read_text()
                result = validate_table_syntax(content, doc_file)
                
                assert result.is_valid, (
                    f"Table syntax validation failed for {doc_file}: "
                    f"{[e.message for e in result.errors]}"
                )
    
    def test_code_block_compliance(self, docs_dir: Path):
        """
        Property 2.3: All docs pass code block language identifier validations.
        
        THE Documentation_System SHALL pass all code block language
        identifier validations (Property 3 in validate_docs.py).
        
        **Validates: Requirements 2.3**
        """
        from validate_docs import validate_code_blocks
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        for doc_file in get_all_doc_files():
            file_path = docs_dir / doc_file
            if file_path.exists():
                content = file_path.read_text()
                result = validate_code_blocks(content, doc_file)
                
                assert result.is_valid, (
                    f"Code block validation failed for {doc_file}: "
                    f"{[e.message for e in result.errors]}"
                )
    
    def test_entry_completeness_compliance(self, docs_dir: Path):
        """
        Property 2.4: All docs pass entry field completeness validations.
        
        THE Documentation_System SHALL pass all entry field
        completeness validations (Property 4 in validate_docs.py).
        
        **Validates: Requirements 2.4**
        """
        from validate_docs import validate_entry_completeness
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        for doc_file in get_all_doc_files():
            file_path = docs_dir / doc_file
            if file_path.exists():
                content = file_path.read_text()
                result = validate_entry_completeness(content, doc_file)
                
                assert result.is_valid, (
                    f"Entry completeness validation failed for {doc_file}: "
                    f"{[e.message for e in result.errors]}"
                )
    
    def test_sid_naming_compliance(self, docs_dir: Path):
        """
        Property 2.5: All docs pass SID naming convention validations.
        
        THE Documentation_System SHALL pass all SID naming convention
        validations (Property 5 in validate_docs.py).
        
        Note: This checks for errors only, not warnings.
        
        **Validates: Requirements 2.5**
        """
        from validate_docs import validate_sid_naming
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        for doc_file in get_all_doc_files():
            file_path = docs_dir / doc_file
            if file_path.exists():
                content = file_path.read_text()
                result = validate_sid_naming(content, doc_file)
                
                # Only check for errors, not warnings
                assert result.is_valid, (
                    f"SID naming validation failed for {doc_file}: "
                    f"{[e.message for e in result.errors]}"
                )
    
    def test_cross_reference_compliance(self, docs_dir: Path):
        """
        Property 2.6: All docs pass cross-reference consistency validations.
        
        THE Documentation_System SHALL pass all cross-reference
        consistency validations (Property 6 in validate_docs.py).
        
        **Validates: Requirements 2.6**
        """
        from validate_docs import (
            validate_cross_references,
            extract_definitions_from_tables,
        )
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        # Load tables definitions
        tables_path = docs_dir / "tables.md"
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        
        tables_definitions = extract_definitions_from_tables(
            tables_path.read_text()
        )
        
        for doc_file in get_all_doc_files():
            file_path = docs_dir / doc_file
            if file_path.exists():
                content = file_path.read_text()
                result = validate_cross_references(
                    content, doc_file, tables_definitions
                )
                
                assert result.is_valid, (
                    f"Cross-reference validation failed for {doc_file}: "
                    f"{[e.message for e in result.errors]}"
                )
    
    def test_flag_prefix_compliance(self, docs_dir: Path):
        """
        Property 2.7: All docs pass flag prefix convention validations.
        
        THE Documentation_System SHALL pass all flag prefix convention
        validations (Property 7 in validate_docs.py).
        
        **Validates: Requirements 2.7**
        """
        from validate_docs import validate_flag_prefixes
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        for doc_file in get_all_doc_files():
            file_path = docs_dir / doc_file
            if file_path.exists():
                content = file_path.read_text()
                result = validate_flag_prefixes(content, doc_file)
                
                assert result.is_valid, (
                    f"Flag prefix validation failed for {doc_file}: "
                    f"{[e.message for e in result.errors]}"
                )
    
    def test_example_coverage_compliance(self, docs_dir: Path):
        """
        Property 2.8: examples.md passes example coverage validations.
        
        THE Documentation_System SHALL pass all example coverage
        validations (Property 8 in validate_docs.py).
        
        **Validates: Requirements 2.8**
        """
        from validate_docs import (
            validate_example_coverage,
            extract_definitions_from_tables,
        )
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        # Load tables definitions
        tables_path = docs_dir / "tables.md"
        examples_path = docs_dir / "examples.md"
        
        if not tables_path.exists() or not examples_path.exists():
            pytest.skip("Required files not found")
        
        tables_definitions = extract_definitions_from_tables(
            tables_path.read_text()
        )
        
        content = examples_path.read_text()
        result = validate_example_coverage(
            content, "examples.md", tables_definitions
        )
        
        assert result.is_valid, (
            f"Example coverage validation failed: "
            f"{[e.message for e in result.errors]}"
        )


# =============================================================================
# Property-Based Tests for Validation Compliance
# =============================================================================


@st.composite
def doc_file_strategy(draw):
    """Generate valid documentation file names."""
    return draw(st.sampled_from(get_all_doc_files()))


class TestValidationComplianceProperties:
    """
    Property-based tests for validation compliance.
    
    Feature: documentation-unification, Property 2: Validation Script Compliance
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
    """
    
    @given(doc_file=doc_file_strategy())
    @settings(max_examples=100)
    def test_doc_file_validation_compliance_property(
        self,
        doc_file: str,
    ):
        """
        Property 2: For any documentation file, validation should pass.
        
        For any markdown file in the expected documentation set,
        if that file exists in docs/, it SHALL pass validation
        with zero errors.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
        """
        from validate_docs import (
            validate_file,
            extract_definitions_from_tables,
        )
        
        docs_dir = Path(__file__).parent.parent / "docs"
        
        if not docs_dir.exists():
            return  # Skip if docs directory doesn't exist
        
        file_path = docs_dir / doc_file
        
        if not file_path.exists():
            return  # Skip if specific file doesn't exist
        
        # Load tables definitions for cross-reference validation
        tables_path = docs_dir / "tables.md"
        tables_definitions = {}
        if tables_path.exists():
            tables_definitions = extract_definitions_from_tables(
                tables_path.read_text()
            )
        
        # Run validation on the file
        result = validate_file(file_path, tables_definitions)
        
        # Should have zero errors
        assert result.is_valid, (
            f"Documentation file '{doc_file}' should pass validation. "
            f"Found {len(result.errors)} errors:\n" +
            "\n".join(f"  [{e.rule}] {e.message}" for e in result.errors[:5])
        )


# =============================================================================
# Integration Tests: Full Validation Pipeline
# =============================================================================


class TestValidationPipelineIntegration:
    """Integration tests for the full validation pipeline."""
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    def test_validation_result_is_valid(self, docs_dir: Path):
        """
        Test that the overall validation result is valid.
        
        The is_valid property should return True when there are
        zero errors.
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        result = validate_all_docs(docs_dir)
        
        # is_valid should be True when errors list is empty
        assert result.is_valid == (len(result.errors) == 0), (
            "is_valid should reflect error count"
        )
    
    def test_validation_processes_all_expected_files(self, docs_dir: Path):
        """
        Test that validation processes all expected documentation files.
        
        All expected files that exist should be included in
        files_validated set.
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        result = validate_all_docs(docs_dir)
        
        # Get validated file names
        validated_file_names = {
            Path(f).name for f in result.files_validated
        }
        
        # Check that all existing expected files were validated
        expected_files = set(get_all_doc_files())
        existing_expected = {
            f for f in expected_files
            if (docs_dir / f).exists()
        }
        
        missing = existing_expected - validated_file_names
        
        assert len(missing) == 0, (
            f"Expected files not validated: {sorted(missing)}"
        )
    
    def test_validation_runs_all_validators(self, docs_dir: Path):
        """
        Test that validation runs all validator functions.
        
        The validation pipeline should run all property validators
        on each file.
        """
        from validate_docs import validate_file, extract_definitions_from_tables
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        tables_path = docs_dir / "tables.md"
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        
        tables_definitions = extract_definitions_from_tables(
            tables_path.read_text()
        )
        
        # Validate tables.md (should run all validators)
        result = validate_file(tables_path, tables_definitions)
        
        # Result should be populated (even if no errors)
        assert result is not None, "validate_file should return a result"
        assert hasattr(result, 'errors'), "Result should have errors attribute"
        assert hasattr(result, 'warnings'), "Result should have warnings attribute"
        assert hasattr(result, 'files_validated'), "Result should track validated files"
    
    def test_zero_errors_on_full_validation(self, docs_dir: Path):
        """
        Test that full validation produces zero errors.
        
        This is the main compliance test - the documentation
        should pass all validations.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        result = validate_all_docs(docs_dir)
        
        # Should have zero errors
        error_count = len(result.errors)
        
        assert error_count == 0, (
            f"Full validation should produce zero errors. "
            f"Found {error_count} errors:\n" +
            "\n".join(f"  [{e.rule}] {e.file}:{e.line} - {e.message}" 
                      for e in result.errors)
        )
