"""
Property-Based Tests for Documentation-to-Code Mapping

Feature: integration-validation
Property 3: Documentation-to-Code Mapping
Validates: Requirements 3.1, 3.2, 3.3

Tests that all documented entities have implementations.
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
# Helper Functions for Extraction
# =============================================================================


def extract_documented_commands(api_path: Path) -> set[str]:
    """
    Extract all documented command names from api.md.
    
    Parses the api.md file to find command sections (### command_name)
    and returns a set of command identifiers.
    """
    commands = set()
    
    if not api_path.exists():
        return commands
    
    content = api_path.read_text()
    lines = content.split("\n")
    
    # Pattern to match command section headers like ### slap, ### chop, etc.
    command_section_pattern = re.compile(r"^###\s+(\w+)\s*$")
    
    # Known vince commands to filter out non-command sections
    known_commands = {"slap", "chop", "set", "forget", "offer", "reject", "list"}
    
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Track code blocks to avoid matching headers inside them
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        match = command_section_pattern.match(stripped)
        if match:
            cmd_name = match.group(1).lower()
            # Only include if it's a known command
            if cmd_name in known_commands:
                commands.add(cmd_name)
    
    return commands


def extract_implemented_commands(commands_dir: Path) -> set[str]:
    """
    Extract all implemented command names from vince/commands/ directory.
    
    Scans the commands directory for Python files and extracts command
    identifiers based on file names and function definitions.
    """
    commands = set()
    
    if not commands_dir.exists() or not commands_dir.is_dir():
        return commands
    
    # Map file names to command names
    file_to_command = {
        "slap.py": "slap",
        "chop.py": "chop",
        "set_cmd.py": "set",
        "forget.py": "forget",
        "offer.py": "offer",
        "reject.py": "reject",
        "list_cmd.py": "list",
    }
    
    for py_file in commands_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        # Check if file maps to a known command
        if py_file.name in file_to_command:
            commands.add(file_to_command[py_file.name])
        else:
            # For unknown files, try to extract command from function definition
            content = py_file.read_text()
            cmd_pattern = re.compile(r"def\s+cmd_(\w+)\s*\(")
            for match in cmd_pattern.finditer(content):
                commands.add(match.group(1).lower())
    
    return commands


def extract_documented_error_codes(errors_path: Path) -> set[str]:
    """
    Extract all documented error codes from errors.md.
    
    Parses the errors.md file to find error codes in the format VE{category}{number}.
    """
    error_codes = set()
    
    if not errors_path.exists():
        return error_codes
    
    content = errors_path.read_text()
    
    # Pattern to match error codes like VE101, VE201, etc.
    error_code_pattern = re.compile(r"\bVE[1-5]\d{2}\b")
    
    # Find all error codes in the document
    for match in error_code_pattern.finditer(content):
        error_codes.add(match.group())
    
    return error_codes


def extract_implemented_error_codes(errors_py_path: Path) -> set[str]:
    """
    Extract all implemented error codes from vince/errors.py.
    
    Parses the errors.py file to find error codes defined in exception classes.
    """
    error_codes = set()
    
    if not errors_py_path.exists():
        return error_codes
    
    content = errors_py_path.read_text()
    
    # Pattern to match error codes in code like code="VE101"
    code_pattern = re.compile(r'code\s*=\s*["\']?(VE[1-5]\d{2})["\']?')
    
    for match in code_pattern.finditer(content):
        error_codes.add(match.group(1))
    
    return error_codes


def extract_documented_states(states_path: Path) -> dict[str, set[str]]:
    """
    Extract all documented states from states.md.
    
    Returns a dict with 'default_states' and 'offer_states' sets.
    """
    states = {
        "default_states": set(),
        "offer_states": set(),
    }
    
    if not states_path.exists():
        return states
    
    content = states_path.read_text()
    
    # Known default states
    default_state_names = {"none", "pending", "active", "removed"}
    # Known offer states
    offer_state_names = {"none", "created", "active", "rejected"}
    
    # Check if these states are documented
    for state in default_state_names:
        # Look for state in Default States section
        if re.search(rf"\|\s*{state}\s*\|", content, re.IGNORECASE):
            states["default_states"].add(state)
    
    for state in offer_state_names:
        # Look for state in Offer States section
        if re.search(rf"\|\s*{state}\s*\|", content, re.IGNORECASE):
            states["offer_states"].add(state)
    
    return states


def extract_implemented_states(state_dir: Path) -> dict[str, set[str]]:
    """
    Extract all implemented states from vince/state/ directory.
    
    Returns a dict with 'default_states' and 'offer_states' sets.
    """
    states = {
        "default_states": set(),
        "offer_states": set(),
    }
    
    if not state_dir.exists() or not state_dir.is_dir():
        return states
    
    # Check default_state.py
    default_state_path = state_dir / "default_state.py"
    if default_state_path.exists():
        content = default_state_path.read_text()
        # Look for enum values like NONE = "none", PENDING = "pending", etc.
        state_pattern = re.compile(r'(\w+)\s*=\s*["\'](\w+)["\']')
        for match in state_pattern.finditer(content):
            state_value = match.group(2).lower()
            if state_value in {"none", "pending", "active", "removed"}:
                states["default_states"].add(state_value)
    
    # Check offer_state.py
    offer_state_path = state_dir / "offer_state.py"
    if offer_state_path.exists():
        content = offer_state_path.read_text()
        state_pattern = re.compile(r'(\w+)\s*=\s*["\'](\w+)["\']')
        for match in state_pattern.finditer(content):
            state_value = match.group(2).lower()
            if state_value in {"none", "created", "active", "rejected"}:
                states["offer_states"].add(state_value)
    
    return states


# =============================================================================
# Property 3: Documentation-to-Code Mapping
# Validates: Requirements 3.1, 3.2, 3.3
# Feature: integration-validation
# =============================================================================


class TestDocumentationToCodeMapping:
    """
    Feature: integration-validation, Property 3: Documentation-to-Code Mapping
    
    For any command/error/state defined in the documentation system, there SHALL
    exist a corresponding implementation in the source code with matching identifier.
    """
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    @pytest.fixture
    def src_dir(self) -> Path:
        """Get the vince source directory path."""
        return Path(__file__).parent.parent / "vince"
    
    def test_all_documented_commands_have_implementations(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 3: All documented commands should have implementations.
        
        For any command defined in docs/api.md, there SHALL exist a corresponding
        implementation in vince/commands/.
        
        **Validates: Requirements 3.1**
        """
        api_path = docs_dir / "api.md"
        commands_dir = src_dir / "commands"
        
        if not api_path.exists():
            pytest.skip("api.md not found")
        
        if not commands_dir.exists():
            pytest.skip("vince/commands/ not found")
        
        doc_commands = extract_documented_commands(api_path)
        src_commands = extract_implemented_commands(commands_dir)
        
        # Check that all documented commands are implemented
        missing_implementations = doc_commands - src_commands
        
        assert len(missing_implementations) == 0, (
            f"Commands documented in api.md but not implemented: "
            f"{sorted(missing_implementations)}"
        )
    
    def test_all_documented_error_codes_have_implementations(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 3: All documented error codes should have implementations.
        
        For any error code defined in docs/errors.md, there SHALL exist a
        corresponding exception class in vince/errors.py.
        
        **Validates: Requirements 3.2**
        """
        errors_md_path = docs_dir / "errors.md"
        errors_py_path = src_dir / "errors.py"
        
        if not errors_md_path.exists():
            pytest.skip("errors.md not found")
        
        if not errors_py_path.exists():
            pytest.skip("vince/errors.py not found")
        
        doc_error_codes = extract_documented_error_codes(errors_md_path)
        src_error_codes = extract_implemented_error_codes(errors_py_path)
        
        # Check that all documented error codes are implemented
        missing_implementations = doc_error_codes - src_error_codes
        
        assert len(missing_implementations) == 0, (
            f"Error codes documented in errors.md but not implemented: "
            f"{sorted(missing_implementations)}"
        )
    
    def test_all_documented_states_have_implementations(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 3: All documented states should have implementations.
        
        For any state defined in docs/states.md, there SHALL exist a
        corresponding state value in vince/state/.
        
        **Validates: Requirements 3.3**
        """
        states_md_path = docs_dir / "states.md"
        state_dir = src_dir / "state"
        
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        if not state_dir.exists():
            pytest.skip("vince/state/ not found")
        
        doc_states = extract_documented_states(states_md_path)
        src_states = extract_implemented_states(state_dir)
        
        # Check default states
        missing_default_states = doc_states["default_states"] - src_states["default_states"]
        assert len(missing_default_states) == 0, (
            f"Default states documented in states.md but not implemented: "
            f"{sorted(missing_default_states)}"
        )
        
        # Check offer states
        missing_offer_states = doc_states["offer_states"] - src_states["offer_states"]
        assert len(missing_offer_states) == 0, (
            f"Offer states documented in states.md but not implemented: "
            f"{sorted(missing_offer_states)}"
        )


# =============================================================================
# Property-Based Tests for Documentation-Code Consistency
# =============================================================================


@st.composite
def command_name_strategy(draw):
    """Generate valid command names."""
    return draw(st.sampled_from([
        "slap", "chop", "set", "forget", "offer", "reject", "list",
    ]))


@st.composite
def error_code_strategy(draw):
    """Generate valid error codes."""
    category = draw(st.integers(min_value=1, max_value=5))
    number = draw(st.integers(min_value=1, max_value=5))
    return f"VE{category}0{number}"


class TestDocCodeMappingProperties:
    """Property-based tests for documentation-code mapping."""
    
    @given(command=command_name_strategy())
    @settings(max_examples=100)
    def test_documented_command_has_implementation(
        self,
        command: str,
    ):
        """
        Property: For any documented command, implementation should exist.
        
        For any command name from the known command set, if it is documented
        in api.md, then it SHALL have an implementation in vince/commands/.
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        src_dir = Path(__file__).parent.parent / "vince"
        
        api_path = docs_dir / "api.md"
        commands_dir = src_dir / "commands"
        
        if not api_path.exists() or not commands_dir.exists():
            return  # Skip if files don't exist
        
        doc_commands = extract_documented_commands(api_path)
        src_commands = extract_implemented_commands(commands_dir)
        
        # If command is documented, it should be implemented
        if command in doc_commands:
            assert command in src_commands, (
                f"Command '{command}' is documented but not implemented"
            )
    
    @given(error_code=error_code_strategy())
    @settings(max_examples=100)
    def test_documented_error_code_has_implementation(
        self,
        error_code: str,
    ):
        """
        Property: For any documented error code, implementation should exist.
        
        For any error code from the valid error code space, if it is documented
        in errors.md, then it SHALL have an implementation in vince/errors.py.
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        src_dir = Path(__file__).parent.parent / "vince"
        
        errors_md_path = docs_dir / "errors.md"
        errors_py_path = src_dir / "errors.py"
        
        if not errors_md_path.exists() or not errors_py_path.exists():
            return  # Skip if files don't exist
        
        doc_error_codes = extract_documented_error_codes(errors_md_path)
        src_error_codes = extract_implemented_error_codes(errors_py_path)
        
        # If error code is documented, it should be implemented
        if error_code in doc_error_codes:
            assert error_code in src_error_codes, (
                f"Error code '{error_code}' is documented but not implemented"
            )


# =============================================================================
# Integration Tests: Validate Real Documentation-Code Sync
# =============================================================================


class TestDocCodeSyncIntegration:
    """Integration tests for documentation-code synchronization."""
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    @pytest.fixture
    def src_dir(self) -> Path:
        """Get the vince source directory path."""
        return Path(__file__).parent.parent / "vince"
    
    def test_validate_code_documentation_sync_function(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Test the validate_code_documentation_sync function from validate_docs.py.
        
        This verifies that the validation function correctly identifies
        documentation-code sync issues.
        """
        from validate_docs import validate_code_documentation_sync
        
        result = validate_code_documentation_sync(docs_dir, src_dir)
        
        # The result should have no errors if docs and code are in sync
        doc_code_errors = [
            e for e in result.errors
            if e.rule in ("DOC-CODE", "CODE-DOC")
        ]
        
        assert len(doc_code_errors) == 0, (
            f"Documentation-code sync errors found: "
            f"{[(e.rule, e.message) for e in doc_code_errors]}"
        )
    
    def test_command_file_structure_matches_documentation(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Test that command file structure matches documentation.
        
        Each documented command should have a corresponding file in
        vince/commands/ with the expected naming convention.
        """
        api_path = docs_dir / "api.md"
        commands_dir = src_dir / "commands"
        
        if not api_path.exists() or not commands_dir.exists():
            pytest.skip("Required files not found")
        
        # Expected file mapping
        command_to_file = {
            "slap": "slap.py",
            "chop": "chop.py",
            "set": "set_cmd.py",  # Avoids Python keyword
            "forget": "forget.py",
            "offer": "offer.py",
            "reject": "reject.py",
            "list": "list_cmd.py",  # Avoids Python keyword
        }
        
        doc_commands = extract_documented_commands(api_path)
        
        for cmd in doc_commands:
            expected_file = command_to_file.get(cmd)
            if expected_file:
                file_path = commands_dir / expected_file
                assert file_path.exists(), (
                    f"Command '{cmd}' documented but file '{expected_file}' "
                    f"not found in vince/commands/"
                )
    
    def test_error_class_naming_convention(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Test that error classes follow naming conventions.
        
        Each error code should have a corresponding exception class
        with a descriptive name.
        """
        errors_py_path = src_dir / "errors.py"
        
        if not errors_py_path.exists():
            pytest.skip("vince/errors.py not found")
        
        content = errors_py_path.read_text()
        tree = ast.parse(content)
        
        # Find all exception classes
        exception_classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from VinceError or Exception
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id in ("VinceError", "Exception"):
                            exception_classes.append(node.name)
        
        # Verify we have exception classes
        assert len(exception_classes) > 0, (
            "No exception classes found in vince/errors.py"
        )
        
        # Verify naming convention (should end with "Error")
        for class_name in exception_classes:
            if class_name != "VinceError":  # Base class is allowed
                assert class_name.endswith("Error"), (
                    f"Exception class '{class_name}' should end with 'Error'"
                )
    
    def test_state_enum_values_match_documentation(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Test that state enum values match documentation.
        
        The state values in vince/state/ should match those documented
        in states.md.
        """
        states_md_path = docs_dir / "states.md"
        state_dir = src_dir / "state"
        
        if not states_md_path.exists() or not state_dir.exists():
            pytest.skip("Required files not found")
        
        doc_states = extract_documented_states(states_md_path)
        src_states = extract_implemented_states(state_dir)
        
        # Verify bidirectional consistency for default states
        assert doc_states["default_states"] == src_states["default_states"], (
            f"Default states mismatch. "
            f"Documented: {doc_states['default_states']}, "
            f"Implemented: {src_states['default_states']}"
        )
        
        # Verify bidirectional consistency for offer states
        assert doc_states["offer_states"] == src_states["offer_states"], (
            f"Offer states mismatch. "
            f"Documented: {doc_states['offer_states']}, "
            f"Implemented: {src_states['offer_states']}"
        )



# =============================================================================
# Property 1: Source-Documentation Synchronization (Errors)
# Validates: Requirements 1.2
# Feature: documentation-unification
# =============================================================================


def extract_error_details_from_source(errors_py_path: Path) -> dict[str, dict]:
    """
    Extract error details (code, message template, recovery) from vince/errors.py.
    
    Returns a dict mapping error codes to their details.
    """
    error_details = {}
    
    if not errors_py_path.exists():
        return error_details
    
    content = errors_py_path.read_text()
    
    # Pattern to match error class definitions with their details
    # Looking for patterns like:
    # code="VE101",
    # message=f"Invalid path: {path} does not exist",
    # recovery="Verify the application path exists and is accessible"
    
    class_pattern = re.compile(
        r'class\s+(\w+Error)\(VinceError\):.*?'
        r'code\s*=\s*["\']?(VE\d{3})["\']?.*?'
        r'message\s*=\s*f?["\']([^"\']+)["\'].*?'
        r'recovery\s*=\s*["\']([^"\']+)["\']',
        re.DOTALL
    )
    
    for match in class_pattern.finditer(content):
        class_name = match.group(1)
        code = match.group(2)
        message_template = match.group(3)
        recovery = match.group(4)
        
        error_details[code] = {
            "class_name": class_name,
            "message_template": message_template,
            "recovery": recovery,
        }
    
    return error_details


def extract_error_details_from_docs(errors_md_path: Path) -> dict[str, dict]:
    """
    Extract error details from docs/errors.md.
    
    Returns a dict mapping error codes to their documented details.
    """
    error_details = {}
    
    if not errors_md_path.exists():
        return error_details
    
    content = errors_md_path.read_text()
    
    # Pattern to match table rows with error details
    # Format: | VE101 | `InvalidPathError` | Invalid path: {path} does not exist | error | Verify... |
    table_row_pattern = re.compile(
        r'\|\s*(VE\d{3})\s*\|\s*`?(\w+)`?\s*\|\s*([^|]+)\s*\|\s*(\w+)\s*\|\s*([^|]+)\s*\|'
    )
    
    for match in table_row_pattern.finditer(content):
        code = match.group(1)
        class_name = match.group(2)
        message_template = match.group(3).strip()
        severity = match.group(4).strip()
        recovery = match.group(5).strip()
        
        error_details[code] = {
            "class_name": class_name,
            "message_template": message_template,
            "severity": severity,
            "recovery": recovery,
        }
    
    return error_details


class TestErrorSourceDocSynchronization:
    """
    Feature: documentation-unification, Property 1: Source-Documentation Synchronization (errors)
    
    For any error class defined in vince/errors.py, the documentation system SHALL
    contain a corresponding entry with matching code, message template, and recovery action.
    
    **Validates: Requirements 1.2**
    """
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    @pytest.fixture
    def src_dir(self) -> Path:
        """Get the vince source directory path."""
        return Path(__file__).parent.parent / "vince"
    
    def test_all_source_errors_documented(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 1: All source error codes should be documented.
        
        For any error code defined in vince/errors.py, there SHALL exist a
        corresponding entry in docs/errors.md.
        
        **Validates: Requirements 1.2**
        """
        errors_py_path = src_dir / "errors.py"
        errors_md_path = docs_dir / "errors.md"
        
        if not errors_py_path.exists():
            pytest.skip("vince/errors.py not found")
        
        if not errors_md_path.exists():
            pytest.skip("docs/errors.md not found")
        
        src_error_codes = extract_implemented_error_codes(errors_py_path)
        doc_error_codes = extract_documented_error_codes(errors_md_path)
        
        # Check that all source error codes are documented
        missing_in_docs = src_error_codes - doc_error_codes
        
        assert len(missing_in_docs) == 0, (
            f"Error codes in source but not documented: {sorted(missing_in_docs)}"
        )
    
    def test_all_documented_errors_in_source(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 1: All documented error codes should exist in source.
        
        For any error code documented in docs/errors.md, there SHALL exist a
        corresponding implementation in vince/errors.py.
        
        **Validates: Requirements 1.2**
        """
        errors_py_path = src_dir / "errors.py"
        errors_md_path = docs_dir / "errors.md"
        
        if not errors_py_path.exists():
            pytest.skip("vince/errors.py not found")
        
        if not errors_md_path.exists():
            pytest.skip("docs/errors.md not found")
        
        src_error_codes = extract_implemented_error_codes(errors_py_path)
        doc_error_codes = extract_documented_error_codes(errors_md_path)
        
        # Check that all documented error codes exist in source
        missing_in_source = doc_error_codes - src_error_codes
        
        assert len(missing_in_source) == 0, (
            f"Error codes documented but not in source: {sorted(missing_in_source)}"
        )
    
    def test_error_code_count_matches(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 1: Error code counts should match between source and docs.
        
        The number of error codes in vince/errors.py SHALL equal the number
        of error codes in docs/errors.md.
        
        **Validates: Requirements 1.2**
        """
        errors_py_path = src_dir / "errors.py"
        errors_md_path = docs_dir / "errors.md"
        
        if not errors_py_path.exists():
            pytest.skip("vince/errors.py not found")
        
        if not errors_md_path.exists():
            pytest.skip("docs/errors.md not found")
        
        src_error_codes = extract_implemented_error_codes(errors_py_path)
        doc_error_codes = extract_documented_error_codes(errors_md_path)
        
        assert len(src_error_codes) == len(doc_error_codes), (
            f"Error code count mismatch. Source: {len(src_error_codes)}, "
            f"Docs: {len(doc_error_codes)}"
        )


@st.composite
def implemented_error_code_strategy(draw):
    """Generate error codes that are implemented in source."""
    # All implemented error codes
    implemented_codes = [
        "VE101", "VE102", "VE103", "VE104", "VE105",  # Input
        "VE201", "VE202", "VE203",  # File
        "VE301", "VE302", "VE303", "VE304",  # State
        "VE401", "VE402",  # Config
        "VE501",  # System
    ]
    return draw(st.sampled_from(implemented_codes))


class TestErrorSyncProperties:
    """
    Property-based tests for error synchronization.
    
    Feature: documentation-unification, Property 1: Source-Documentation Synchronization (errors)
    **Validates: Requirements 1.2**
    """
    
    @given(error_code=implemented_error_code_strategy())
    @settings(max_examples=100)
    def test_implemented_error_is_documented(
        self,
        error_code: str,
    ):
        """
        Property 1: For any implemented error code, documentation should exist.
        
        For any error code from the implemented error code set, it SHALL be
        documented in docs/errors.md.
        
        **Validates: Requirements 1.2**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        errors_md_path = docs_dir / "errors.md"
        
        if not errors_md_path.exists():
            return  # Skip if file doesn't exist
        
        doc_error_codes = extract_documented_error_codes(errors_md_path)
        
        assert error_code in doc_error_codes, (
            f"Error code '{error_code}' is implemented but not documented"
        )
