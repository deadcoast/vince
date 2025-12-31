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
from vince.errors import InvalidPathError, PermissionDeniedError


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
