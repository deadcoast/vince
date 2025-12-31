"""
Property-Based Tests for Validation Coverage

Feature: integration-validation
Property 6: Validation Coverage
Validates: Requirements 5.1, 5.3

Tests that all doc files are included in validation.
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


def get_all_doc_files(docs_dir: Path) -> set[str]:
    """
    Get all markdown files in the docs directory.
    
    Returns a set of file names (e.g., {'tables.md', 'api.md', ...}).
    """
    if not docs_dir.exists():
        return set()
    
    return {f.name for f in docs_dir.glob("*.md")}


def get_expected_doc_files() -> set[str]:
    """
    Get the expected documentation files that should be validated.
    
    These are the files defined in validate_all_docs() function.
    """
    return {
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
    }


# =============================================================================
# Property 6: Validation Coverage
# Validates: Requirements 5.1, 5.3
# Feature: integration-validation
# =============================================================================


class TestValidationCoverage:
    """
    Feature: integration-validation, Property 6: Validation Coverage
    
    For any markdown file in the `docs/` directory, the validation script
    SHALL process that file and include it in the validation report.
    """
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    @pytest.fixture
    def all_doc_files(self, docs_dir: Path) -> set[str]:
        """Get all markdown files in docs directory."""
        return get_all_doc_files(docs_dir)
    
    @pytest.fixture
    def expected_doc_files(self) -> set[str]:
        """Get expected documentation files."""
        return get_expected_doc_files()
    
    def test_all_doc_files_are_validated(
        self,
        docs_dir: Path,
        all_doc_files: set[str],
    ):
        """
        Property 6: All markdown files in docs/ should be validated.
        
        For any markdown file in the `docs/` directory, the validation
        script SHALL process that file.
        
        **Validates: Requirements 5.1**
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        # Run validation
        result = validate_all_docs(docs_dir)
        
        # Get the set of validated file names (extract just the filename)
        validated_files = {
            Path(f).name for f in result.files_validated
        }
        
        # Check that all doc files were validated
        missing_files = all_doc_files - validated_files
        
        assert len(missing_files) == 0, (
            f"Documentation files not validated: {sorted(missing_files)}"
        )
    
    def test_expected_files_are_validated(
        self,
        docs_dir: Path,
        expected_doc_files: set[str],
    ):
        """
        Property 6: All expected documentation files should be validated.
        
        The validation script SHALL validate all expected documentation
        files defined in the system.
        
        **Validates: Requirements 5.1**
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        # Run validation
        result = validate_all_docs(docs_dir)
        
        # Get the set of validated file names
        validated_files = {
            Path(f).name for f in result.files_validated
        }
        
        # Check that all expected files were validated (if they exist)
        existing_expected = {
            f for f in expected_doc_files
            if (docs_dir / f).exists()
        }
        
        missing_files = existing_expected - validated_files
        
        assert len(missing_files) == 0, (
            f"Expected documentation files not validated: {sorted(missing_files)}"
        )
    
    def test_files_validated_set_is_populated(
        self,
        docs_dir: Path,
    ):
        """
        Property 6: The files_validated set should be populated.
        
        After running validation, the ValidationResult SHALL have
        a non-empty files_validated set.
        
        **Validates: Requirements 5.3**
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        # Run validation
        result = validate_all_docs(docs_dir)
        
        # Check that files_validated is populated
        assert len(result.files_validated) > 0, (
            "files_validated set should be populated after validation"
        )
    
    def test_validate_file_marks_file_as_validated(
        self,
        docs_dir: Path,
    ):
        """
        Property 6: validate_file should mark files as validated.
        
        When validate_file processes a file, it SHALL mark that file
        as validated in the result.
        
        **Validates: Requirements 5.1**
        """
        from validate_docs import validate_file, extract_definitions_from_tables
        
        tables_path = docs_dir / "tables.md"
        
        if not tables_path.exists():
            pytest.skip("tables.md not found")
        
        # Get tables definitions for cross-reference validation
        tables_definitions = extract_definitions_from_tables(
            tables_path.read_text()
        )
        
        # Validate a single file
        result = validate_file(tables_path, tables_definitions)
        
        # Check that the file was marked as validated
        assert str(tables_path) in result.files_validated, (
            f"File {tables_path} should be marked as validated"
        )


# =============================================================================
# Property-Based Tests for Validation Coverage
# =============================================================================


@st.composite
def doc_file_strategy(draw):
    """Generate valid documentation file names."""
    return draw(st.sampled_from([
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
    ]))


class TestValidationCoverageProperties:
    """Property-based tests for validation coverage."""
    
    @given(doc_file=doc_file_strategy())
    @settings(max_examples=100)
    def test_doc_file_validation_coverage_property(
        self,
        doc_file: str,
    ):
        """
        Property 6: For any expected documentation file, if it exists,
        it should be included in validation.
        
        For any markdown file in the expected documentation set,
        if that file exists in docs/, it SHALL be validated.
        
        **Validates: Requirements 5.1, 5.3**
        """
        from validate_docs import validate_all_docs
        
        docs_dir = Path(__file__).parent.parent / "docs"
        
        if not docs_dir.exists():
            return  # Skip if docs directory doesn't exist
        
        file_path = docs_dir / doc_file
        
        if not file_path.exists():
            return  # Skip if specific file doesn't exist
        
        # Run validation
        result = validate_all_docs(docs_dir)
        
        # Get validated file names
        validated_files = {
            Path(f).name for f in result.files_validated
        }
        
        # If the file exists, it should be validated
        assert doc_file in validated_files, (
            f"Documentation file '{doc_file}' exists but was not validated"
        )


# =============================================================================
# Integration Tests: Validate Coverage Tracking
# =============================================================================


class TestValidationCoverageIntegration:
    """Integration tests for validation coverage tracking."""
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    def test_validation_result_tracks_all_files(
        self,
        docs_dir: Path,
    ):
        """
        Test that ValidationResult correctly tracks all validated files.
        
        The files_validated set should contain all files that were
        processed during validation.
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        # Get all markdown files in docs
        all_md_files = get_all_doc_files(docs_dir)
        
        # Run validation
        result = validate_all_docs(docs_dir)
        
        # Get validated file names
        validated_file_names = {
            Path(f).name for f in result.files_validated
        }
        
        # All existing markdown files should be validated
        # (or at least attempted - some may be missing)
        expected_files = get_expected_doc_files()
        existing_expected = {
            f for f in expected_files
            if (docs_dir / f).exists()
        }
        
        coverage_ratio = len(validated_file_names & existing_expected) / len(existing_expected)
        
        assert coverage_ratio == 1.0, (
            f"Validation coverage is {coverage_ratio:.1%}, expected 100%. "
            f"Missing: {existing_expected - validated_file_names}"
        )
    
    def test_validation_reports_missing_files(
        self,
        docs_dir: Path,
    ):
        """
        Test that validation reports missing expected files.
        
        If an expected documentation file is missing, the validation
        should report a warning.
        """
        from validate_docs import validate_all_docs
        
        if not docs_dir.exists():
            pytest.skip("docs directory not found")
        
        # Run validation
        result = validate_all_docs(docs_dir)
        
        # Check for warnings about missing files
        expected_files = get_expected_doc_files()
        
        for expected_file in expected_files:
            file_path = docs_dir / expected_file
            
            if not file_path.exists():
                # Should have a warning about missing file
                missing_warnings = [
                    w for w in result.warnings
                    if expected_file in w.message and "not found" in w.message.lower()
                ]
                
                assert len(missing_warnings) > 0, (
                    f"Missing file '{expected_file}' should generate a warning"
                )
    
    def test_properties_checked_tracking(
        self,
        docs_dir: Path,
    ):
        """
        Test that properties_checked set is available in ValidationResult.
        
        The ValidationResult should have a properties_checked set
        for tracking which property validators have run.
        
        **Validates: Requirements 5.3**
        """
        from validate_docs import ValidationResult
        
        # Create a new ValidationResult
        result = ValidationResult()
        
        # Check that properties_checked attribute exists
        assert hasattr(result, "properties_checked"), (
            "ValidationResult should have properties_checked attribute"
        )
        
        # Check that it's a set
        assert isinstance(result.properties_checked, set), (
            "properties_checked should be a set"
        )
        
        # Test mark_property_checked method
        result.mark_property_checked("test_property")
        
        assert "test_property" in result.properties_checked, (
            "mark_property_checked should add property to set"
        )
    
    def test_files_validated_tracking(
        self,
        docs_dir: Path,
    ):
        """
        Test that files_validated set is available in ValidationResult.
        
        The ValidationResult should have a files_validated set
        for tracking which files have been processed.
        
        **Validates: Requirements 5.1**
        """
        from validate_docs import ValidationResult
        
        # Create a new ValidationResult
        result = ValidationResult()
        
        # Check that files_validated attribute exists
        assert hasattr(result, "files_validated"), (
            "ValidationResult should have files_validated attribute"
        )
        
        # Check that it's a set
        assert isinstance(result.files_validated, set), (
            "files_validated should be a set"
        )
        
        # Test mark_file_validated method
        result.mark_file_validated("test_file.md")
        
        assert "test_file.md" in result.files_validated, (
            "mark_file_validated should add file to set"
        )
    
    def test_merge_preserves_coverage_tracking(
        self,
        docs_dir: Path,
    ):
        """
        Test that merge() preserves coverage tracking data.
        
        When merging ValidationResults, the files_validated and
        properties_checked sets should be combined.
        """
        from validate_docs import ValidationResult
        
        # Create two ValidationResults
        result1 = ValidationResult()
        result1.mark_file_validated("file1.md")
        result1.mark_property_checked("property1")
        
        result2 = ValidationResult()
        result2.mark_file_validated("file2.md")
        result2.mark_property_checked("property2")
        
        # Merge result2 into result1
        result1.merge(result2)
        
        # Check that both files are tracked
        assert "file1.md" in result1.files_validated, (
            "merge should preserve original files_validated"
        )
        assert "file2.md" in result1.files_validated, (
            "merge should add merged files_validated"
        )
        
        # Check that both properties are tracked
        assert "property1" in result1.properties_checked, (
            "merge should preserve original properties_checked"
        )
        assert "property2" in result1.properties_checked, (
            "merge should add merged properties_checked"
        )
