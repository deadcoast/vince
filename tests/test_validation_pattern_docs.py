"""
Property-Based Tests for Validation Pattern Documentation

Feature: documentation-unification
Property 9: Validation Pattern Documentation
Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5

Tests that validation patterns documented in overview.md match the source code.
"""

import re
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Helper Functions for Pattern Extraction
# =============================================================================


def extract_pattern_from_source(source_path: Path, pattern_name: str) -> str | None:
    """
    Extract a regex pattern constant from source code.
    
    Args:
        source_path: Path to the Python source file
        pattern_name: Name of the pattern constant (e.g., "EXTENSION_PATTERN")
    
    Returns:
        The regex pattern string, or None if not found
    """
    if not source_path.exists():
        return None
    
    content = source_path.read_text()
    
    # Pattern to match: PATTERN_NAME = re.compile(r'...')
    pattern = re.compile(
        rf'{pattern_name}\s*=\s*re\.compile\s*\(\s*r["\']([^"\']+)["\']',
        re.MULTILINE
    )
    
    match = pattern.search(content)
    if match:
        return match.group(1)
    
    return None


def extract_set_from_source(source_path: Path, set_name: str) -> set[str] | None:
    """
    Extract a set constant from source code.
    
    Args:
        source_path: Path to the Python source file
        set_name: Name of the set constant (e.g., "RESERVED_NAMES")
    
    Returns:
        The set of strings, or None if not found
    """
    if not source_path.exists():
        return None
    
    content = source_path.read_text()
    
    # Pattern to match: SET_NAME = {"item1", "item2", ...}
    pattern = re.compile(
        rf'{set_name}\s*=\s*\{{([^}}]+)\}}',
        re.MULTILINE
    )
    
    match = pattern.search(content)
    if match:
        items_str = match.group(1)
        # Extract quoted strings
        items = re.findall(r'["\']([^"\']+)["\']', items_str)
        return set(items)
    
    return None


def extract_pattern_from_docs(docs_path: Path, pattern_name: str) -> str | None:
    """
    Extract a regex pattern from documentation.
    
    Args:
        docs_path: Path to the markdown documentation file
        pattern_name: Name of the pattern constant (e.g., "EXTENSION_PATTERN")
    
    Returns:
        The regex pattern string, or None if not found
    """
    if not docs_path.exists():
        return None
    
    content = docs_path.read_text()
    
    # Pattern to match: PATTERN_NAME = re.compile(r'...')
    pattern = re.compile(
        rf'{pattern_name}\s*=\s*re\.compile\s*\(\s*r["\']([^"\']+)["\']',
        re.MULTILINE
    )
    
    match = pattern.search(content)
    if match:
        return match.group(1)
    
    return None


def extract_set_from_docs(docs_path: Path, set_name: str) -> set[str] | None:
    """
    Extract a set constant from documentation.
    
    Args:
        docs_path: Path to the markdown documentation file
        set_name: Name of the set constant (e.g., "RESERVED_NAMES")
    
    Returns:
        The set of strings, or None if not found
    """
    if not docs_path.exists():
        return None
    
    content = docs_path.read_text()
    
    # Pattern to match: SET_NAME = {'item1', 'item2', ...}
    pattern = re.compile(
        rf'{set_name}\s*=\s*\{{([^}}]+)\}}',
        re.MULTILINE
    )
    
    match = pattern.search(content)
    if match:
        items_str = match.group(1)
        # Extract quoted strings
        items = re.findall(r'["\']([^"\']+)["\']', items_str)
        return set(items)
    
    return None


def extract_error_codes_from_validation_section(
    docs_path: Path,
    section_name: str,
) -> set[str]:
    """
    Extract error codes documented for a validation section.
    
    Args:
        docs_path: Path to the markdown documentation file
        section_name: Name of the validation section (e.g., "Path Validation")
    
    Returns:
        Set of error codes (e.g., {"VE101", "VE202"})
    """
    if not docs_path.exists():
        return set()
    
    content = docs_path.read_text()
    error_codes = set()
    
    # Find the section
    section_pattern = re.compile(
        rf'###\s+{re.escape(section_name)}.*?(?=###|\Z)',
        re.DOTALL
    )
    
    match = section_pattern.search(content)
    if match:
        section_content = match.group(0)
        # Extract error codes (VE followed by 3 digits)
        codes = re.findall(r'\bVE\d{3}\b', section_content)
        error_codes.update(codes)
    
    return error_codes


# =============================================================================
# Property 9: Validation Pattern Documentation
# Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
# Feature: documentation-unification
# =============================================================================


class TestValidationPatternDocumentation:
    """
    Feature: documentation-unification, Property 9: Validation Pattern Documentation
    
    For any regex pattern constant or reserved name set in source code,
    the documentation SHALL contain the exact matching value.
    
    **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
    """
    
    @pytest.fixture
    def src_dir(self) -> Path:
        """Get the vince source directory path."""
        return Path(__file__).parent.parent / "vince"
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    def test_extension_pattern_matches_source(
        self,
        src_dir: Path,
        docs_dir: Path,
    ):
        """
        Property 9: EXTENSION_PATTERN in docs should match source.
        
        The EXTENSION_PATTERN regex documented in overview.md SHALL match
        the pattern defined in vince/validation/extension.py.
        
        **Validates: Requirements 9.1**
        """
        extension_py = src_dir / "validation" / "extension.py"
        overview_md = docs_dir / "overview.md"
        
        if not extension_py.exists():
            pytest.skip("vince/validation/extension.py not found")
        
        if not overview_md.exists():
            pytest.skip("docs/overview.md not found")
        
        src_pattern = extract_pattern_from_source(extension_py, "EXTENSION_PATTERN")
        doc_pattern = extract_pattern_from_docs(overview_md, "EXTENSION_PATTERN")
        
        assert src_pattern is not None, (
            "EXTENSION_PATTERN not found in vince/validation/extension.py"
        )
        assert doc_pattern is not None, (
            "EXTENSION_PATTERN not found in docs/overview.md"
        )
        assert src_pattern == doc_pattern, (
            f"EXTENSION_PATTERN mismatch. "
            f"Source: {src_pattern!r}, Docs: {doc_pattern!r}"
        )
    
    def test_offer_id_pattern_matches_source(
        self,
        src_dir: Path,
        docs_dir: Path,
    ):
        """
        Property 9: OFFER_ID_PATTERN in docs should match source.
        
        The OFFER_ID_PATTERN regex documented in overview.md SHALL match
        the pattern defined in vince/validation/offer_id.py.
        
        **Validates: Requirements 9.2**
        """
        offer_id_py = src_dir / "validation" / "offer_id.py"
        overview_md = docs_dir / "overview.md"
        
        if not offer_id_py.exists():
            pytest.skip("vince/validation/offer_id.py not found")
        
        if not overview_md.exists():
            pytest.skip("docs/overview.md not found")
        
        src_pattern = extract_pattern_from_source(offer_id_py, "OFFER_ID_PATTERN")
        doc_pattern = extract_pattern_from_docs(overview_md, "OFFER_ID_PATTERN")
        
        assert src_pattern is not None, (
            "OFFER_ID_PATTERN not found in vince/validation/offer_id.py"
        )
        assert doc_pattern is not None, (
            "OFFER_ID_PATTERN not found in docs/overview.md"
        )
        assert src_pattern == doc_pattern, (
            f"OFFER_ID_PATTERN mismatch. "
            f"Source: {src_pattern!r}, Docs: {doc_pattern!r}"
        )
    
    def test_reserved_names_matches_source(
        self,
        src_dir: Path,
        docs_dir: Path,
    ):
        """
        Property 9: RESERVED_NAMES in docs should match source.
        
        The RESERVED_NAMES set documented in overview.md SHALL match
        the set defined in vince/validation/offer_id.py.
        
        **Validates: Requirements 9.3**
        """
        offer_id_py = src_dir / "validation" / "offer_id.py"
        overview_md = docs_dir / "overview.md"
        
        if not offer_id_py.exists():
            pytest.skip("vince/validation/offer_id.py not found")
        
        if not overview_md.exists():
            pytest.skip("docs/overview.md not found")
        
        src_names = extract_set_from_source(offer_id_py, "RESERVED_NAMES")
        doc_names = extract_set_from_docs(overview_md, "RESERVED_NAMES")
        
        assert src_names is not None, (
            "RESERVED_NAMES not found in vince/validation/offer_id.py"
        )
        assert doc_names is not None, (
            "RESERVED_NAMES not found in docs/overview.md"
        )
        assert src_names == doc_names, (
            f"RESERVED_NAMES mismatch. "
            f"Source: {sorted(src_names)}, Docs: {sorted(doc_names)}"
        )
    
    def test_path_validation_error_codes_documented(
        self,
        docs_dir: Path,
    ):
        """
        Property 9: Path validation error codes should be documented.
        
        The path validation section in overview.md SHALL document
        error codes VE101 and VE202.
        
        **Validates: Requirements 9.4**
        """
        overview_md = docs_dir / "overview.md"
        
        if not overview_md.exists():
            pytest.skip("docs/overview.md not found")
        
        error_codes = extract_error_codes_from_validation_section(
            overview_md, "Path Validation"
        )
        
        expected_codes = {"VE101", "VE202"}
        missing_codes = expected_codes - error_codes
        
        assert len(missing_codes) == 0, (
            f"Path validation missing error codes: {sorted(missing_codes)}"
        )
    
    def test_extension_validation_error_codes_documented(
        self,
        docs_dir: Path,
    ):
        """
        Property 9: Extension validation error codes should be documented.
        
        The extension validation section in overview.md SHALL document
        error code VE102.
        
        **Validates: Requirements 9.4**
        """
        overview_md = docs_dir / "overview.md"
        
        if not overview_md.exists():
            pytest.skip("docs/overview.md not found")
        
        error_codes = extract_error_codes_from_validation_section(
            overview_md, "Extension Validation"
        )
        
        expected_codes = {"VE102"}
        missing_codes = expected_codes - error_codes
        
        assert len(missing_codes) == 0, (
            f"Extension validation missing error codes: {sorted(missing_codes)}"
        )
    
    def test_offer_id_validation_error_codes_documented(
        self,
        docs_dir: Path,
    ):
        """
        Property 9: Offer ID validation error codes should be documented.
        
        The offer ID validation section in overview.md SHALL document
        error codes VE103 and VE303.
        
        **Validates: Requirements 9.5**
        """
        overview_md = docs_dir / "overview.md"
        
        if not overview_md.exists():
            pytest.skip("docs/overview.md not found")
        
        error_codes = extract_error_codes_from_validation_section(
            overview_md, "Offer ID Validation"
        )
        
        expected_codes = {"VE103", "VE303"}
        missing_codes = expected_codes - error_codes
        
        assert len(missing_codes) == 0, (
            f"Offer ID validation missing error codes: {sorted(missing_codes)}"
        )


# =============================================================================
# Property-Based Tests for Pattern Consistency
# =============================================================================


@st.composite
def valid_extension_strategy(draw):
    """Generate valid file extensions based on EXTENSION_PATTERN."""
    # Pattern: ^\.[a-z0-9]+$
    ext_chars = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
        min_size=1,
        max_size=10,
    ))
    return f".{ext_chars}"


@st.composite
def valid_offer_id_strategy(draw):
    """Generate valid offer IDs based on OFFER_ID_PATTERN."""
    # Pattern: ^[a-z][a-z0-9_-]{0,31}$
    first_char = draw(st.sampled_from("abcdefghijklmnopqrstuvwxyz"))
    rest_length = draw(st.integers(min_value=0, max_value=31))
    rest_chars = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-",
        min_size=rest_length,
        max_size=rest_length,
    ))
    return first_char + rest_chars


class TestPatternConsistencyProperties:
    """
    Property-based tests for validation pattern consistency.
    
    Feature: documentation-unification, Property 9: Validation Pattern Documentation
    **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
    """
    
    @given(extension=valid_extension_strategy())
    @settings(max_examples=100)
    def test_extension_pattern_accepts_valid_extensions(
        self,
        extension: str,
    ):
        r"""
        Property 9: EXTENSION_PATTERN should accept valid extensions.
        
        For any string matching the documented pattern ^\.[a-z0-9]+$,
        the EXTENSION_PATTERN regex SHALL match.
        """
        from vince.validation.extension import EXTENSION_PATTERN
        
        assert EXTENSION_PATTERN.match(extension), (
            f"EXTENSION_PATTERN should match valid extension: {extension!r}"
        )
    
    @given(offer_id=valid_offer_id_strategy())
    @settings(max_examples=100)
    def test_offer_id_pattern_accepts_valid_ids(
        self,
        offer_id: str,
    ):
        """
        Property 9: OFFER_ID_PATTERN should accept valid offer IDs.
        
        For any string matching the documented pattern ^[a-z][a-z0-9_-]{0,31}$,
        the OFFER_ID_PATTERN regex SHALL match.
        """
        from vince.validation.offer_id import OFFER_ID_PATTERN
        
        assert OFFER_ID_PATTERN.match(offer_id), (
            f"OFFER_ID_PATTERN should match valid offer ID: {offer_id!r}"
        )
    
    @given(name=st.sampled_from(["help", "version", "list", "all", "none", "default"]))
    @settings(max_examples=100)
    def test_reserved_names_are_rejected(
        self,
        name: str,
    ):
        """
        Property 9: RESERVED_NAMES should be rejected by validation.
        
        For any name in the documented RESERVED_NAMES set,
        the validate_offer_id function SHALL raise InvalidOfferIdError.
        """
        from vince.validation.offer_id import RESERVED_NAMES, validate_offer_id
        from vince.errors import InvalidOfferIdError
        
        assert name in RESERVED_NAMES, (
            f"Name '{name}' should be in RESERVED_NAMES"
        )
        
        with pytest.raises(InvalidOfferIdError):
            validate_offer_id(name)


# =============================================================================
# Integration Tests: Verify Documentation Accuracy
# =============================================================================


class TestValidationPatternIntegration:
    """Integration tests for validation pattern documentation accuracy."""
    
    @pytest.fixture
    def src_dir(self) -> Path:
        """Get the vince source directory path."""
        return Path(__file__).parent.parent / "vince"
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    def test_supported_extensions_count_matches(
        self,
        src_dir: Path,
        docs_dir: Path,
    ):
        """
        Test that the number of supported extensions matches between source and docs.
        """
        extension_py = src_dir / "validation" / "extension.py"
        overview_md = docs_dir / "overview.md"
        
        if not extension_py.exists() or not overview_md.exists():
            pytest.skip("Required files not found")
        
        # Extract from source
        src_content = extension_py.read_text()
        src_extensions = extract_set_from_source(extension_py, "SUPPORTED_EXTENSIONS")
        
        # Extract from docs (look for extension table)
        doc_content = overview_md.read_text()
        doc_extensions = set()
        
        # Find extensions in the Supported Extensions table
        ext_pattern = re.compile(r'\|\s*`?(\.[\w]+)`?\s*\|')
        for match in ext_pattern.finditer(doc_content):
            ext = match.group(1)
            if ext.startswith("."):
                doc_extensions.add(ext)
        
        if src_extensions:
            # Check that all source extensions are documented
            missing_in_docs = src_extensions - doc_extensions
            assert len(missing_in_docs) == 0, (
                f"Extensions in source but not documented: {sorted(missing_in_docs)}"
            )
    
    def test_validation_functions_documented(
        self,
        docs_dir: Path,
    ):
        """
        Test that all validation functions are documented in overview.md.
        """
        overview_md = docs_dir / "overview.md"
        
        if not overview_md.exists():
            pytest.skip("docs/overview.md not found")
        
        content = overview_md.read_text()
        
        # Check for validation function documentation
        expected_functions = [
            "validate_path",
            "validate_extension",
            "validate_offer_id",
        ]
        
        for func_name in expected_functions:
            assert func_name in content, (
                f"Validation function '{func_name}' should be documented in overview.md"
            )
    
    def test_error_code_references_are_valid(
        self,
        src_dir: Path,
        docs_dir: Path,
    ):
        """
        Test that error codes referenced in validation docs exist in errors.py.
        """
        errors_py = src_dir / "errors.py"
        overview_md = docs_dir / "overview.md"
        
        if not errors_py.exists() or not overview_md.exists():
            pytest.skip("Required files not found")
        
        # Extract error codes from source
        src_content = errors_py.read_text()
        src_codes = set(re.findall(r'code\s*=\s*["\']?(VE\d{3})["\']?', src_content))
        
        # Extract error codes from validation sections in docs
        doc_content = overview_md.read_text()
        
        # Find the Validation Rules section
        validation_section = re.search(
            r'## Validation Rules.*?(?=## [A-Z]|\Z)',
            doc_content,
            re.DOTALL
        )
        
        if validation_section:
            section_content = validation_section.group(0)
            doc_codes = set(re.findall(r'\bVE\d{3}\b', section_content))
            
            # All documented codes should exist in source
            invalid_codes = doc_codes - src_codes
            assert len(invalid_codes) == 0, (
                f"Error codes in docs but not in source: {sorted(invalid_codes)}"
            )
