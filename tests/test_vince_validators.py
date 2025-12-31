"""
Property-Based Tests for Vince CLI Validators

Feature: vince-cli-implementation
Each test validates a specific correctness property from the design document.
"""

import os
import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import string
import tempfile

from vince.validation.path import validate_path
from vince.validation.extension import (
    validate_extension,
    flag_to_extension,
    SUPPORTED_EXTENSIONS,
)
from vince.validation.offer_id import (
    validate_offer_id,
    OFFER_ID_PATTERN,
    RESERVED_NAMES,
)
from vince.errors import InvalidPathError, PermissionDeniedError, InvalidExtensionError, InvalidOfferIdError


# =============================================================================
# Property 1: Path Validation Correctness
# Validates: Requirements 3.1, 3.2, 3.3, 3.4
# =============================================================================

class TestPathValidation:
    """Feature: vince-cli-implementation, Property 1: Path Validation Correctness
    
    *For any* file path, if the path exists, is a file, and is executable,
    then validate_path SHALL return the resolved path. If any condition fails,
    validate_path SHALL raise the appropriate error (InvalidPathError for
    non-existent/non-file, PermissionDeniedError for non-executable).
    """
    
    @pytest.fixture
    def executable_file(self, tmp_path):
        """Create a valid executable file for testing."""
        exe = tmp_path / "test_app"
        exe.write_text("#!/bin/bash\necho 'test'")
        exe.chmod(0o755)
        return exe
    
    @pytest.fixture
    def non_executable_file(self, tmp_path):
        """Create a non-executable file for testing."""
        file = tmp_path / "test_file.txt"
        file.write_text("test content")
        file.chmod(0o644)
        return file
    
    @given(st.text(min_size=1, max_size=50, alphabet=string.ascii_letters + string.digits + "_-"))
    @settings(max_examples=100)
    def test_nonexistent_paths_raise_invalid_path_error(self, filename):
        """Property: Non-existent paths should raise InvalidPathError (VE101)."""
        # Create a path that definitely doesn't exist
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
    
    def test_directory_raises_invalid_path_error(self, tmp_path):
        """Property: Directory paths should raise InvalidPathError (VE101)."""
        with pytest.raises(InvalidPathError) as exc_info:
            validate_path(tmp_path)
        
        assert exc_info.value.code == "VE101"
    
    def test_non_executable_raises_permission_denied_error(self, non_executable_file):
        """Property: Non-executable files should raise PermissionDeniedError (VE202)."""
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_path(non_executable_file)
        
        assert exc_info.value.code == "VE202"
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100)
    def test_multiple_executable_files_all_validate(self, count):
        """Property: All valid executable files should validate successfully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            for i in range(count):
                exe = tmp_path / f"app_{i}"
                exe.write_text(f"#!/bin/bash\necho 'app {i}'")
                exe.chmod(0o755)
                
                result = validate_path(exe)
                assert result == exe.resolve()
    
    def test_symlink_to_executable_validates(self, executable_file, tmp_path):
        """Property: Symlinks to executable files should validate."""
        symlink = tmp_path / "symlink_app"
        symlink.symlink_to(executable_file)
        
        result = validate_path(symlink)
        # Should resolve to the actual file
        assert result.exists()
        assert os.access(result, os.X_OK)
    
    def test_symlink_to_nonexistent_raises_error(self, tmp_path):
        """Property: Symlinks to non-existent files should raise InvalidPathError."""
        symlink = tmp_path / "broken_symlink"
        symlink.symlink_to(tmp_path / "nonexistent")
        
        with pytest.raises(InvalidPathError) as exc_info:
            validate_path(symlink)
        
        assert exc_info.value.code == "VE101"


# =============================================================================
# Property 2: Extension Validation Correctness
# Validates: Requirements 3.5, 3.6, 3.7
# =============================================================================

@st.composite
def valid_extensions(draw):
    """Generate valid file extensions from the supported set."""
    return draw(st.sampled_from(list(SUPPORTED_EXTENSIONS)))


@st.composite
def invalid_pattern_extensions(draw):
    """Generate extensions that don't match the required pattern."""
    strategies = [
        st.just("md"),           # Missing dot
        st.just(".MD"),          # Uppercase (will be normalized, but test pattern)
        st.just(".m d"),         # Contains space
        st.just("..md"),         # Double dot
        st.just("."),            # Just a dot
        st.just(""),             # Empty string
        st.just(".md!"),         # Special character
        st.just(".123"),         # Numbers only (valid pattern but not supported)
    ]
    return draw(st.one_of(*strategies))


@st.composite
def unsupported_extensions(draw):
    """Generate extensions that match pattern but are not supported."""
    # Generate valid pattern extensions that aren't in SUPPORTED_EXTENSIONS
    unsupported = [".exe", ".dll", ".so", ".bin", ".dat", ".log", ".tmp", ".bak"]
    return draw(st.sampled_from(unsupported))


class TestExtensionValidation:
    r"""Feature: vince-cli-implementation, Property 2: Extension Validation Correctness
    
    *For any* string, if it matches the pattern ^\.[a-z0-9]+$ AND is in the
    supported extensions set, then validate_extension SHALL return the lowercase
    extension. Otherwise, validate_extension SHALL raise InvalidExtensionError.
    """
    
    @given(ext=valid_extensions())
    @settings(max_examples=100)
    def test_valid_extensions_pass(self, ext):
        """Property: All supported extensions should validate successfully."""
        result = validate_extension(ext)
        assert result == ext.lower()
        assert result in SUPPORTED_EXTENSIONS
    
    @given(ext=valid_extensions())
    @settings(max_examples=100)
    def test_uppercase_extensions_normalize(self, ext):
        """Property: Uppercase versions of valid extensions should normalize and pass."""
        upper_ext = ext.upper()
        result = validate_extension(upper_ext)
        assert result == ext.lower()
    
    @given(ext=unsupported_extensions())
    @settings(max_examples=100)
    def test_unsupported_extensions_fail(self, ext):
        """Property: Unsupported extensions should raise InvalidExtensionError."""
        with pytest.raises(InvalidExtensionError) as exc_info:
            validate_extension(ext)
        
        assert exc_info.value.code == "VE102"
    
    def test_missing_dot_fails(self):
        """Property: Extensions without leading dot should fail."""
        with pytest.raises(InvalidExtensionError) as exc_info:
            validate_extension("md")
        
        assert exc_info.value.code == "VE102"
    
    def test_double_dot_fails(self):
        """Property: Extensions with double dot should fail."""
        with pytest.raises(InvalidExtensionError) as exc_info:
            validate_extension("..md")
        
        assert exc_info.value.code == "VE102"
    
    def test_space_in_extension_fails(self):
        """Property: Extensions with spaces should fail."""
        with pytest.raises(InvalidExtensionError) as exc_info:
            validate_extension(".m d")
        
        assert exc_info.value.code == "VE102"
    
    def test_empty_extension_fails(self):
        """Property: Empty string should fail."""
        with pytest.raises(InvalidExtensionError) as exc_info:
            validate_extension("")
        
        assert exc_info.value.code == "VE102"
    
    def test_just_dot_fails(self):
        """Property: Just a dot should fail."""
        with pytest.raises(InvalidExtensionError) as exc_info:
            validate_extension(".")
        
        assert exc_info.value.code == "VE102"


class TestFlagToExtension:
    """Tests for the flag_to_extension helper function."""
    
    @given(ext=valid_extensions())
    @settings(max_examples=100)
    def test_double_dash_flag_converts(self, ext):
        """Property: --ext flags should convert to .ext format."""
        flag = f"--{ext[1:]}"  # e.g., ".md" -> "--md"
        result = flag_to_extension(flag)
        assert result == ext
    
    @given(ext=valid_extensions())
    @settings(max_examples=100)
    def test_single_dash_flag_converts(self, ext):
        """Property: -ext flags should convert to .ext format."""
        flag = f"-{ext[1:]}"  # e.g., ".md" -> "-md"
        result = flag_to_extension(flag)
        assert result == ext
    
    @given(ext=valid_extensions())
    @settings(max_examples=100)
    def test_bare_name_converts(self, ext):
        """Property: Bare extension names should convert to .ext format."""
        name = ext[1:]  # e.g., ".md" -> "md"
        result = flag_to_extension(name)
        assert result == ext
    
    @given(ext=valid_extensions())
    @settings(max_examples=100)
    def test_already_dotted_passes_through(self, ext):
        """Property: Already dotted extensions should pass through."""
        result = flag_to_extension(ext)
        assert result == ext



# =============================================================================
# Property 3: Offer ID Validation Correctness
# Validates: Requirements 3.8, 3.9, 3.10
# =============================================================================

@st.composite
def valid_offer_ids(draw):
    """Generate valid offer IDs matching the pattern ^[a-z][a-z0-9_-]{0,31}$."""
    first = draw(st.sampled_from(string.ascii_lowercase))
    rest_length = draw(st.integers(min_value=0, max_value=31))
    rest = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "_-",
        min_size=rest_length,
        max_size=rest_length
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
        st.just("1abc"),           # Starts with number
        st.just("Abc"),            # Starts with uppercase
        st.just("_abc"),           # Starts with underscore
        st.just("-abc"),           # Starts with hyphen
        st.just(""),               # Empty string
        st.just("a" * 33),         # Too long (33 chars)
        st.just("abc def"),        # Contains space
        st.just("abc.def"),        # Contains dot
        st.just("abc!def"),        # Contains special char
    ]
    return draw(st.one_of(*strategies))


class TestOfferIdValidation:
    r"""Feature: vince-cli-implementation, Property 3: Offer ID Validation Correctness
    
    *For any* string, if it matches the pattern ^[a-z][a-z0-9_-]{0,31}$ AND is
    not a reserved name, then validate_offer_id SHALL return the offer_id.
    Otherwise, validate_offer_id SHALL raise InvalidOfferIdError.
    """
    
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
    
    @given(offer_id=invalid_pattern_offer_ids())
    @settings(max_examples=100)
    def test_invalid_pattern_fails(self, offer_id):
        """Property: Offer IDs not matching pattern should raise InvalidOfferIdError."""
        with pytest.raises(InvalidOfferIdError) as exc_info:
            validate_offer_id(offer_id)
        
        assert exc_info.value.code == "VE103"
    
    def test_starts_with_number_fails(self):
        """Property: Offer IDs starting with number should fail."""
        with pytest.raises(InvalidOfferIdError) as exc_info:
            validate_offer_id("1abc")
        
        assert exc_info.value.code == "VE103"
    
    def test_starts_with_uppercase_fails(self):
        """Property: Offer IDs starting with uppercase should fail."""
        with pytest.raises(InvalidOfferIdError) as exc_info:
            validate_offer_id("Abc")
        
        assert exc_info.value.code == "VE103"
    
    def test_too_long_fails(self):
        """Property: Offer IDs longer than 32 chars should fail."""
        long_id = "a" + "b" * 32  # 33 chars total
        with pytest.raises(InvalidOfferIdError) as exc_info:
            validate_offer_id(long_id)
        
        assert exc_info.value.code == "VE103"
    
    def test_max_length_passes(self):
        """Property: Offer IDs at exactly 32 chars should pass."""
        max_id = "a" + "b" * 31  # 32 chars total
        result = validate_offer_id(max_id)
        assert result == max_id
        assert len(result) == 32
    
    def test_single_char_passes(self):
        """Property: Single lowercase letter should pass."""
        result = validate_offer_id("a")
        assert result == "a"
    
    def test_with_underscore_passes(self):
        """Property: Offer IDs with underscores should pass."""
        result = validate_offer_id("my_app")
        assert result == "my_app"
    
    def test_with_hyphen_passes(self):
        """Property: Offer IDs with hyphens should pass."""
        result = validate_offer_id("my-app")
        assert result == "my-app"
    
    def test_with_numbers_passes(self):
        """Property: Offer IDs with numbers (not first) should pass."""
        result = validate_offer_id("app123")
        assert result == "app123"
