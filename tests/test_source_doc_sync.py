"""
Property-Based Tests for Source-Documentation Synchronization

Feature: documentation-unification
Property 1: Source-Documentation Synchronization
Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5

Tests that all source code definitions are accurately documented.
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
# Helper Functions for Source Code Extraction
# =============================================================================


def extract_error_codes_from_source(errors_py_path: Path) -> set[str]:
    """Extract all error codes from vince/errors.py."""
    error_codes = set()
    
    if not errors_py_path.exists():
        return error_codes
    
    content = errors_py_path.read_text()
    code_pattern = re.compile(r'code\s*=\s*["\']?(VE[1-5]\d{2})["\']?')
    
    for match in code_pattern.finditer(content):
        error_codes.add(match.group(1))
    
    return error_codes


def extract_states_from_source(state_dir: Path) -> dict[str, set[str]]:
    """Extract all states from vince/state/ directory."""
    states = {"default_states": set(), "offer_states": set()}
    
    if not state_dir.exists():
        return states

    # Extract default states
    default_state_path = state_dir / "default_state.py"
    if default_state_path.exists():
        content = default_state_path.read_text()
        state_pattern = re.compile(r'(\w+)\s*=\s*["\'](\w+)["\']')
        for match in state_pattern.finditer(content):
            state_value = match.group(2).lower()
            if state_value in {"none", "pending", "active", "removed"}:
                states["default_states"].add(state_value)
    
    # Extract offer states
    offer_state_path = state_dir / "offer_state.py"
    if offer_state_path.exists():
        content = offer_state_path.read_text()
        state_pattern = re.compile(r'(\w+)\s*=\s*["\'](\w+)["\']')
        for match in state_pattern.finditer(content):
            state_value = match.group(2).lower()
            if state_value in {"none", "created", "active", "rejected"}:
                states["offer_states"].add(state_value)
    
    return states


def extract_config_options_from_source(config_py_path: Path) -> set[str]:
    """Extract all config options from vince/config.py."""
    options = set()
    
    if not config_py_path.exists():
        return options
    
    content = config_py_path.read_text()
    
    # Look for DEFAULT_CONFIG dictionary keys
    config_pattern = re.compile(r'["\'](\w+)["\']\s*:')
    
    # Find the DEFAULT_CONFIG section
    default_config_match = re.search(
        r'DEFAULT_CONFIG\s*=\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    
    if default_config_match:
        config_section = default_config_match.group(1)
        for match in config_pattern.finditer(config_section):
            options.add(match.group(1))
    
    return options


def extract_extensions_from_source(extension_py_path: Path) -> set[str]:
    """Extract all supported extensions from vince/validation/extension.py."""
    extensions = set()
    
    if not extension_py_path.exists():
        return extensions
    
    content = extension_py_path.read_text()
    
    # Look for SUPPORTED_EXTENSIONS set
    ext_pattern = re.compile(r'["\'](\.\w+)["\']')
    
    supported_match = re.search(
        r'SUPPORTED_EXTENSIONS\s*=\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    
    if supported_match:
        ext_section = supported_match.group(1)
        for match in ext_pattern.finditer(ext_section):
            extensions.add(match.group(1))
    
    return extensions


# =============================================================================
# Helper Functions for Documentation Extraction
# =============================================================================


def extract_error_codes_from_docs(errors_md_path: Path) -> set[str]:
    """Extract all error codes from docs/errors.md."""
    error_codes = set()
    
    if not errors_md_path.exists():
        return error_codes
    
    content = errors_md_path.read_text()
    error_code_pattern = re.compile(r"\bVE[1-5]\d{2}\b")
    
    for match in error_code_pattern.finditer(content):
        error_codes.add(match.group())
    
    return error_codes


def extract_states_from_docs(states_md_path: Path) -> dict[str, set[str]]:
    """Extract all states from docs/states.md."""
    states = {"default_states": set(), "offer_states": set()}
    
    if not states_md_path.exists():
        return states
    
    content = states_md_path.read_text()
    
    # Known states
    default_state_names = {"none", "pending", "active", "removed"}
    offer_state_names = {"none", "created", "active", "rejected"}
    
    for state in default_state_names:
        if re.search(rf"\|\s*{state}\s*\|", content, re.IGNORECASE):
            states["default_states"].add(state)
    
    for state in offer_state_names:
        if re.search(rf"\|\s*{state}\s*\|", content, re.IGNORECASE):
            states["offer_states"].add(state)
    
    return states


def extract_config_options_from_docs(config_md_path: Path) -> set[str]:
    """Extract all config options from docs/config.md."""
    options = set()
    
    if not config_md_path.exists():
        return options
    
    content = config_md_path.read_text()
    
    # Look for config option keys in tables
    # Pattern: | `option_name` | type | default | description |
    option_pattern = re.compile(r'\|\s*`(\w+)`\s*\|')
    
    for match in option_pattern.finditer(content):
        option = match.group(1)
        # Filter out header values
        if option not in {"Option", "Type", "Default", "Description", "key", "type"}:
            options.add(option)
    
    return options


def extract_extensions_from_docs(tables_md_path: Path) -> set[str]:
    """Extract all extensions from docs/tables.md FILE_TYPES table."""
    extensions = set()
    
    if not tables_md_path.exists():
        return extensions
    
    content = tables_md_path.read_text()
    
    # Look for extensions in FILE_TYPES table
    # Pattern: | ... | .ext | ... |
    ext_pattern = re.compile(r'\|\s*(\.\w+)\s*\|')
    
    # Find FILE_TYPES section
    file_types_match = re.search(
        r'## FILE_TYPES(.*?)(?=## |$)',
        content,
        re.DOTALL
    )
    
    if file_types_match:
        file_types_section = file_types_match.group(1)
        for match in ext_pattern.finditer(file_types_section):
            extensions.add(match.group(1))
    
    return extensions


# =============================================================================
# Property 1: Source-Documentation Synchronization
# Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5
# Feature: documentation-unification
# =============================================================================


class TestSourceDocSynchronization:
    """
    Feature: documentation-unification, Property 1: Source-Documentation Synchronization
    
    For any validation function, error class, state, or configuration option
    defined in source code, the documentation system SHALL contain a corresponding
    entry with matching attributes.
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
    """
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    @pytest.fixture
    def src_dir(self) -> Path:
        """Get the vince source directory path."""
        return Path(__file__).parent.parent / "vince"
    
    def test_error_codes_synchronized(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 1.2: Error classes are documented with matching codes.
        
        WHEN an error class is defined in vince/errors.py, THE Documentation_System
        SHALL include that error in docs/errors.md with matching code.
        
        **Validates: Requirements 1.2**
        """
        errors_py_path = src_dir / "errors.py"
        errors_md_path = docs_dir / "errors.md"
        
        if not errors_py_path.exists():
            pytest.skip("vince/errors.py not found")
        
        if not errors_md_path.exists():
            pytest.skip("docs/errors.md not found")
        
        src_errors = extract_error_codes_from_source(errors_py_path)
        doc_errors = extract_error_codes_from_docs(errors_md_path)
        
        # All source errors should be documented
        missing_in_docs = src_errors - doc_errors
        assert len(missing_in_docs) == 0, (
            f"Error codes in source but not documented: {sorted(missing_in_docs)}"
        )
        
        # All documented errors should exist in source
        missing_in_source = doc_errors - src_errors
        assert len(missing_in_source) == 0, (
            f"Error codes documented but not in source: {sorted(missing_in_source)}"
        )
    
    def test_states_synchronized(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 1.3: State transitions are documented with matching states.
        
        WHEN a state transition is implemented in vince/state/, THE Documentation_System
        SHALL document that transition in docs/states.md with matching from/to states.
        
        **Validates: Requirements 1.3**
        """
        state_dir = src_dir / "state"
        states_md_path = docs_dir / "states.md"
        
        if not state_dir.exists():
            pytest.skip("vince/state/ not found")
        
        if not states_md_path.exists():
            pytest.skip("docs/states.md not found")
        
        src_states = extract_states_from_source(state_dir)
        doc_states = extract_states_from_docs(states_md_path)
        
        # Check default states
        assert src_states["default_states"] == doc_states["default_states"], (
            f"Default states mismatch. Source: {src_states['default_states']}, "
            f"Docs: {doc_states['default_states']}"
        )
        
        # Check offer states
        assert src_states["offer_states"] == doc_states["offer_states"], (
            f"Offer states mismatch. Source: {src_states['offer_states']}, "
            f"Docs: {doc_states['offer_states']}"
        )

    def test_config_options_synchronized(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 1.4: Configuration options are documented with matching attributes.
        
        WHEN a configuration option is used in vince/config.py, THE Documentation_System
        SHALL document that option in docs/config.md with matching type, default, and description.
        
        **Validates: Requirements 1.4**
        """
        config_py_path = src_dir / "config.py"
        config_md_path = docs_dir / "config.md"
        
        if not config_py_path.exists():
            pytest.skip("vince/config.py not found")
        
        if not config_md_path.exists():
            pytest.skip("docs/config.md not found")
        
        src_options = extract_config_options_from_source(config_py_path)
        doc_options = extract_config_options_from_docs(config_md_path)
        
        # All source options should be documented
        missing_in_docs = src_options - doc_options
        assert len(missing_in_docs) == 0, (
            f"Config options in source but not documented: {sorted(missing_in_docs)}"
        )
    
    def test_extensions_synchronized(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Property 1.5: Supported extensions are documented in tables.md.
        
        FOR ALL supported extensions in vince/validation/extension.py, THE
        Documentation_System SHALL list them in docs/tables.md FILE_TYPES table.
        
        **Validates: Requirements 1.5**
        """
        extension_py_path = src_dir / "validation" / "extension.py"
        tables_md_path = docs_dir / "tables.md"
        
        if not extension_py_path.exists():
            pytest.skip("vince/validation/extension.py not found")
        
        if not tables_md_path.exists():
            pytest.skip("docs/tables.md not found")
        
        src_extensions = extract_extensions_from_source(extension_py_path)
        doc_extensions = extract_extensions_from_docs(tables_md_path)
        
        # All source extensions should be documented
        missing_in_docs = src_extensions - doc_extensions
        assert len(missing_in_docs) == 0, (
            f"Extensions in source but not documented: {sorted(missing_in_docs)}"
        )


# =============================================================================
# Property-Based Tests for Source-Doc Synchronization
# =============================================================================


@st.composite
def error_code_strategy(draw):
    """Generate valid error codes from the implemented set."""
    implemented_codes = [
        "VE101", "VE102", "VE103", "VE104", "VE105",
        "VE201", "VE202", "VE203",
        "VE301", "VE302", "VE303", "VE304",
        "VE401", "VE402",
        "VE501",
    ]
    return draw(st.sampled_from(implemented_codes))


@st.composite
def state_strategy(draw):
    """Generate valid state names."""
    states = [
        ("default", "none"),
        ("default", "pending"),
        ("default", "active"),
        ("default", "removed"),
        ("offer", "none"),
        ("offer", "created"),
        ("offer", "active"),
        ("offer", "rejected"),
    ]
    return draw(st.sampled_from(states))


@st.composite
def config_option_strategy(draw):
    """Generate valid config option names."""
    options = [
        "version", "data_dir", "verbose", "color_theme",
        "backup_enabled", "max_backups", "confirm_destructive",
    ]
    return draw(st.sampled_from(options))


@st.composite
def extension_strategy(draw):
    """Generate valid extension names."""
    extensions = [
        ".md", ".py", ".txt", ".js", ".html", ".css",
        ".json", ".yml", ".yaml", ".xml", ".csv", ".sql",
    ]
    return draw(st.sampled_from(extensions))


class TestSourceDocSyncProperties:
    """
    Property-based tests for source-documentation synchronization.
    
    Feature: documentation-unification, Property 1: Source-Documentation Synchronization
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
    """
    
    @given(error_code=error_code_strategy())
    @settings(max_examples=100)
    def test_error_code_is_documented(self, error_code: str):
        """
        Property 1.2: For any implemented error code, documentation should exist.
        
        For any error code from the implemented error code set, it SHALL be
        documented in docs/errors.md.
        
        **Validates: Requirements 1.2**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        errors_md_path = docs_dir / "errors.md"
        
        if not errors_md_path.exists():
            return
        
        doc_errors = extract_error_codes_from_docs(errors_md_path)
        
        assert error_code in doc_errors, (
            f"Error code '{error_code}' is implemented but not documented"
        )
    
    @given(state_info=state_strategy())
    @settings(max_examples=100)
    def test_state_is_documented(self, state_info: tuple[str, str]):
        """
        Property 1.3: For any implemented state, documentation should exist.
        
        For any state from the implemented state set, it SHALL be
        documented in docs/states.md.
        
        **Validates: Requirements 1.3**
        """
        entity, state = state_info
        docs_dir = Path(__file__).parent.parent / "docs"
        states_md_path = docs_dir / "states.md"
        
        if not states_md_path.exists():
            return
        
        doc_states = extract_states_from_docs(states_md_path)
        
        if entity == "default":
            assert state in doc_states["default_states"], (
                f"Default state '{state}' is implemented but not documented"
            )
        else:
            assert state in doc_states["offer_states"], (
                f"Offer state '{state}' is implemented but not documented"
            )
    
    @given(option=config_option_strategy())
    @settings(max_examples=100)
    def test_config_option_is_documented(self, option: str):
        """
        Property 1.4: For any implemented config option, documentation should exist.
        
        For any config option from the implemented option set, it SHALL be
        documented in docs/config.md.
        
        **Validates: Requirements 1.4**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        config_md_path = docs_dir / "config.md"
        
        if not config_md_path.exists():
            return
        
        doc_options = extract_config_options_from_docs(config_md_path)
        
        assert option in doc_options, (
            f"Config option '{option}' is implemented but not documented"
        )
    
    @given(extension=extension_strategy())
    @settings(max_examples=100)
    def test_extension_is_documented(self, extension: str):
        """
        Property 1.5: For any supported extension, documentation should exist.
        
        For any extension from the supported extension set, it SHALL be
        documented in docs/tables.md FILE_TYPES table.
        
        **Validates: Requirements 1.5**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        tables_md_path = docs_dir / "tables.md"
        
        if not tables_md_path.exists():
            return
        
        doc_extensions = extract_extensions_from_docs(tables_md_path)
        
        assert extension in doc_extensions, (
            f"Extension '{extension}' is supported but not documented"
        )


# =============================================================================
# Integration Tests: Full Synchronization Check
# =============================================================================


class TestSourceDocSyncIntegration:
    """Integration tests for source-documentation synchronization."""
    
    @pytest.fixture
    def docs_dir(self) -> Path:
        """Get the docs directory path."""
        return Path(__file__).parent.parent / "docs"
    
    @pytest.fixture
    def src_dir(self) -> Path:
        """Get the vince source directory path."""
        return Path(__file__).parent.parent / "vince"
    
    def test_full_synchronization_check(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Test complete source-documentation synchronization.
        
        This is the main integration test that verifies all aspects
        of Property 1 are satisfied.
        
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
        """
        errors = []
        
        # Check error codes (1.2)
        errors_py_path = src_dir / "errors.py"
        errors_md_path = docs_dir / "errors.md"
        
        if errors_py_path.exists() and errors_md_path.exists():
            src_errors = extract_error_codes_from_source(errors_py_path)
            doc_errors = extract_error_codes_from_docs(errors_md_path)
            
            missing_errors = src_errors - doc_errors
            if missing_errors:
                errors.append(
                    f"Error codes not documented: {sorted(missing_errors)}"
                )
        
        # Check states (1.3)
        state_dir = src_dir / "state"
        states_md_path = docs_dir / "states.md"
        
        if state_dir.exists() and states_md_path.exists():
            src_states = extract_states_from_source(state_dir)
            doc_states = extract_states_from_docs(states_md_path)
            
            if src_states["default_states"] != doc_states["default_states"]:
                errors.append(
                    f"Default states mismatch: "
                    f"src={src_states['default_states']}, "
                    f"docs={doc_states['default_states']}"
                )
            
            if src_states["offer_states"] != doc_states["offer_states"]:
                errors.append(
                    f"Offer states mismatch: "
                    f"src={src_states['offer_states']}, "
                    f"docs={doc_states['offer_states']}"
                )
        
        # Check config options (1.4)
        config_py_path = src_dir / "config.py"
        config_md_path = docs_dir / "config.md"
        
        if config_py_path.exists() and config_md_path.exists():
            src_options = extract_config_options_from_source(config_py_path)
            doc_options = extract_config_options_from_docs(config_md_path)
            
            missing_options = src_options - doc_options
            if missing_options:
                errors.append(
                    f"Config options not documented: {sorted(missing_options)}"
                )
        
        # Check extensions (1.5)
        extension_py_path = src_dir / "validation" / "extension.py"
        tables_md_path = docs_dir / "tables.md"
        
        if extension_py_path.exists() and tables_md_path.exists():
            src_extensions = extract_extensions_from_source(extension_py_path)
            doc_extensions = extract_extensions_from_docs(tables_md_path)
            
            missing_extensions = src_extensions - doc_extensions
            if missing_extensions:
                errors.append(
                    f"Extensions not documented: {sorted(missing_extensions)}"
                )
        
        # Assert no synchronization errors
        assert len(errors) == 0, (
            f"Source-documentation synchronization errors:\n" +
            "\n".join(f"  - {e}" for e in errors)
        )
    
    def test_validate_code_documentation_sync_function(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Test the validate_code_documentation_sync function.
        
        This verifies that the validation function correctly identifies
        documentation-code sync issues.
        """
        from validate_docs import validate_code_documentation_sync
        
        result = validate_code_documentation_sync(docs_dir, src_dir)
        
        # Should have no sync errors
        sync_errors = [
            e for e in result.errors
            if e.rule in ("DOC-CODE", "CODE-DOC")
        ]
        
        assert len(sync_errors) == 0, (
            f"Documentation-code sync errors found: "
            f"{[(e.rule, e.message) for e in sync_errors]}"
        )
    
    def test_bidirectional_consistency(
        self,
        docs_dir: Path,
        src_dir: Path,
    ):
        """
        Test bidirectional consistency between source and documentation.
        
        Everything in source should be in docs, and everything in docs
        should be in source.
        """
        # Error codes
        errors_py_path = src_dir / "errors.py"
        errors_md_path = docs_dir / "errors.md"
        
        if errors_py_path.exists() and errors_md_path.exists():
            src_errors = extract_error_codes_from_source(errors_py_path)
            doc_errors = extract_error_codes_from_docs(errors_md_path)
            
            # Bidirectional check
            assert src_errors == doc_errors, (
                f"Error codes not bidirectionally consistent. "
                f"Only in source: {src_errors - doc_errors}, "
                f"Only in docs: {doc_errors - src_errors}"
            )
        
        # Extensions
        extension_py_path = src_dir / "validation" / "extension.py"
        tables_md_path = docs_dir / "tables.md"
        
        if extension_py_path.exists() and tables_md_path.exists():
            src_extensions = extract_extensions_from_source(extension_py_path)
            doc_extensions = extract_extensions_from_docs(tables_md_path)
            
            # Bidirectional check
            assert src_extensions == doc_extensions, (
                f"Extensions not bidirectionally consistent. "
                f"Only in source: {src_extensions - doc_extensions}, "
                f"Only in docs: {doc_extensions - src_extensions}"
            )
