"""
Property-Based Tests for Import Usage Completeness

Feature: integration-validation
Property 2: Import Usage Completeness
Validates: Requirements 2.1

Tests that all imports in vince/ source files are used.
"""

import ast
import sys
from pathlib import Path
from typing import NamedTuple

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Data Structures
# =============================================================================


class ImportInfo(NamedTuple):
    """Information about an import statement."""
    name: str  # The imported name (as used in code)
    module: str  # The module it's imported from
    line: int  # Line number of the import
    is_from_import: bool  # True if "from X import Y", False if "import X"


class UsageInfo(NamedTuple):
    """Information about a name usage."""
    name: str  # The name being used
    line: int  # Line number of usage
    context: str  # Context type (e.g., "call", "attribute", "name")


# =============================================================================
# Helper Functions for AST Analysis
# =============================================================================


def extract_imports(source_code: str) -> list[ImportInfo]:
    """
    Extract all import statements from source code.
    
    Returns a list of ImportInfo objects for each imported name.
    """
    imports = []
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return imports
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # import X, Y, Z
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                # For "import X.Y.Z", the usable name is "X"
                usable_name = name.split(".")[0]
                imports.append(ImportInfo(
                    name=usable_name,
                    module=alias.name,
                    line=node.lineno,
                    is_from_import=False,
                ))
        
        elif isinstance(node, ast.ImportFrom):
            # from X import Y, Z
            module = node.module or ""
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                imports.append(ImportInfo(
                    name=name,
                    module=module,
                    line=node.lineno,
                    is_from_import=True,
                ))
    
    return imports


def extract_name_usages(source_code: str) -> set[str]:
    """
    Extract all name usages from source code (excluding import statements).
    
    Returns a set of names that are used in the code.
    """
    usages = set()
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return usages
    
    # Collect line numbers of import statements to exclude
    import_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_lines.add(node.lineno)
    
    for node in ast.walk(tree):
        # Skip nodes that are part of import statements
        if hasattr(node, "lineno") and node.lineno in import_lines:
            # But we need to be careful - only skip the import node itself
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
        
        # Look for Name nodes that reference variables (Load context)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            # Exclude names that are on import lines
            if node.lineno not in import_lines:
                usages.add(node.id)
        
        # Look for Attribute nodes (e.g., module.function)
        elif isinstance(node, ast.Attribute):
            # Get the root name of the attribute chain
            root = node
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name) and isinstance(root.ctx, ast.Load):
                if root.lineno not in import_lines:
                    usages.add(root.id)
    
    return usages


def get_unused_imports(source_code: str) -> list[ImportInfo]:
    """
    Find all unused imports in source code.
    
    Returns a list of ImportInfo objects for imports that are not used.
    """
    imports = extract_imports(source_code)
    usages = extract_name_usages(source_code)
    
    unused = []
    for imp in imports:
        if imp.name not in usages:
            unused.append(imp)
    
    return unused


def get_vince_source_files(include_init: bool = False) -> list[Path]:
    """Get all Python source files in the vince/ directory.
    
    Args:
        include_init: If True, include __init__.py files. Default False
                     because __init__.py files often re-export symbols
                     for public API purposes.
    """
    vince_dir = Path(__file__).parent.parent / "vince"
    
    if not vince_dir.exists():
        return []
    
    source_files = []
    for py_file in vince_dir.rglob("*.py"):
        # Skip __pycache__ directories
        if "__pycache__" in str(py_file):
            continue
        # Skip __init__.py files unless explicitly requested
        # These files typically re-export symbols for public API
        if not include_init and py_file.name == "__init__.py":
            continue
        source_files.append(py_file)
    
    return sorted(source_files)


# =============================================================================
# Property 2: Import Usage Completeness
# Validates: Requirements 2.1
# Feature: integration-validation
# =============================================================================


class TestImportUsageCompleteness:
    """
    Feature: integration-validation, Property 2: Import Usage Completeness
    
    For any import statement in a Python source file in `vince/`, the imported
    name SHALL be referenced at least once in that file's code (excluding
    comments and strings).
    
    Note: __init__.py files are excluded from this check because they typically
    re-export symbols for public API purposes. These re-exports are intentional
    and don't require usage within the file itself.
    """
    
    @pytest.fixture
    def vince_source_files(self) -> list[Path]:
        """Get all Python source files in vince/ (excluding __init__.py)."""
        return get_vince_source_files(include_init=False)
    
    def test_all_imports_used_in_all_files(self, vince_source_files: list[Path]):
        """
        Property 2: All imports in vince/ source files should be used.
        
        For any import statement in a Python source file in `vince/`,
        the imported name SHALL be referenced at least once.
        """
        all_unused = {}
        
        for source_file in vince_source_files:
            source_code = source_file.read_text()
            unused = get_unused_imports(source_code)
            
            if unused:
                relative_path = source_file.relative_to(
                    Path(__file__).parent.parent
                )
                all_unused[str(relative_path)] = unused
        
        if all_unused:
            error_messages = []
            for file_path, unused_imports in all_unused.items():
                for imp in unused_imports:
                    error_messages.append(
                        f"  {file_path}:{imp.line} - '{imp.name}' "
                        f"(from {imp.module})"
                    )
            
            pytest.fail(
                f"Found unused imports in vince/ source files:\n"
                + "\n".join(error_messages)
            )
    
    def test_reject_command_uses_print_warning(self):
        """
        Property 2: The print_warning import in reject.py should be used.
        
        Validates: Requirements 2.2
        """
        reject_path = Path(__file__).parent.parent / "vince/commands/reject.py"
        
        if not reject_path.exists():
            pytest.skip("reject.py not found")
        
        source_code = reject_path.read_text()
        imports = extract_imports(source_code)
        usages = extract_name_usages(source_code)
        
        # Find print_warning import
        print_warning_import = None
        for imp in imports:
            if imp.name == "print_warning":
                print_warning_import = imp
                break
        
        assert print_warning_import is not None, (
            "print_warning should be imported in reject.py"
        )
        
        assert "print_warning" in usages, (
            "print_warning should be used in reject.py "
            "(not just imported)"
        )
    
    def test_each_file_individually(self, vince_source_files: list[Path]):
        """
        Test each vince source file individually for unused imports.
        
        This provides more granular feedback about which files have issues.
        """
        for source_file in vince_source_files:
            source_code = source_file.read_text()
            unused = get_unused_imports(source_code)
            
            relative_path = source_file.relative_to(
                Path(__file__).parent.parent
            )
            
            assert len(unused) == 0, (
                f"File {relative_path} has unused imports: "
                f"{[(imp.name, f'line {imp.line}') for imp in unused]}"
            )


# =============================================================================
# Property-Based Tests for Import Analysis
# =============================================================================


@st.composite
def simple_python_module(draw):
    """Generate simple Python module source code with imports and usages."""
    # Generate some import names
    import_names = draw(st.lists(
        st.sampled_from([
            "os", "sys", "json", "pathlib", "typing",
            "dataclasses", "functools", "itertools",
        ]),
        min_size=1,
        max_size=4,
        unique=True,
    ))
    
    # Decide which imports to use
    used_imports = draw(st.lists(
        st.sampled_from(import_names),
        min_size=0,
        max_size=len(import_names),
        unique=True,
    ))
    
    # Build source code
    lines = []
    for name in import_names:
        lines.append(f"import {name}")
    
    lines.append("")
    lines.append("def main():")
    
    if used_imports:
        for name in used_imports:
            lines.append(f"    print({name})")
    else:
        lines.append("    pass")
    
    source = "\n".join(lines)
    
    return source, set(import_names), set(used_imports)


class TestImportAnalysisProperties:
    """Property-based tests for the import analysis functions."""
    
    @given(module_data=simple_python_module())
    @settings(max_examples=100)
    def test_unused_imports_detected(self, module_data):
        """
        Property: Unused imports should be correctly detected.
        
        For any Python module with imports, the unused imports detected
        should be exactly those imports that are not referenced in the code.
        """
        source, all_imports, used_imports = module_data
        
        unused = get_unused_imports(source)
        unused_names = {imp.name for imp in unused}
        
        expected_unused = all_imports - used_imports
        
        assert unused_names == expected_unused, (
            f"Expected unused: {expected_unused}, "
            f"Got: {unused_names}"
        )
    
    @given(module_data=simple_python_module())
    @settings(max_examples=100)
    def test_all_imports_extracted(self, module_data):
        """
        Property: All imports should be extracted from source code.
        
        For any Python module, extract_imports should find all import statements.
        """
        source, all_imports, _ = module_data
        
        imports = extract_imports(source)
        extracted_names = {imp.name for imp in imports}
        
        assert extracted_names == all_imports, (
            f"Expected imports: {all_imports}, "
            f"Got: {extracted_names}"
        )
    
    def test_from_import_extraction(self):
        """Test that 'from X import Y' style imports are correctly extracted."""
        source = """
from pathlib import Path
from typing import Optional, List

def func(p: Path) -> Optional[List[str]]:
    return None
"""
        imports = extract_imports(source)
        import_names = {imp.name for imp in imports}
        
        assert "Path" in import_names
        assert "Optional" in import_names
        assert "List" in import_names
    
    def test_aliased_import_extraction(self):
        """Test that aliased imports use the alias name."""
        source = """
import numpy as np
from pathlib import Path as P

x = np.array([1, 2, 3])
y = P(".")
"""
        imports = extract_imports(source)
        import_names = {imp.name for imp in imports}
        
        assert "np" in import_names
        assert "P" in import_names
        assert "numpy" not in import_names
        assert "Path" not in import_names
    
    def test_nested_module_import(self):
        """Test that 'import X.Y.Z' uses 'X' as the usable name."""
        source = """
import os.path

result = os.path.join("a", "b")
"""
        imports = extract_imports(source)
        import_names = {imp.name for imp in imports}
        
        # The usable name is "os", not "os.path"
        assert "os" in import_names
        
        # And it should be detected as used
        unused = get_unused_imports(source)
        assert len(unused) == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestImportUsageIntegration:
    """Integration tests for import usage in actual vince source files."""
    
    def test_vince_directory_exists(self):
        """Verify the vince directory exists for testing."""
        vince_dir = Path(__file__).parent.parent / "vince"
        assert vince_dir.exists(), "vince/ directory should exist"
        assert vince_dir.is_dir(), "vince/ should be a directory"
    
    def test_source_files_are_valid_python(self):
        """Verify all vince source files are valid Python."""
        for source_file in get_vince_source_files(include_init=True):
            source_code = source_file.read_text()
            try:
                ast.parse(source_code)
            except SyntaxError as e:
                pytest.fail(
                    f"Syntax error in {source_file}: {e}"
                )
    
    def test_no_star_imports(self):
        """
        Test that no files use 'from X import *' style imports.
        
        Star imports make it impossible to track import usage.
        """
        for source_file in get_vince_source_files(include_init=True):
            source_code = source_file.read_text()
            tree = ast.parse(source_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name == "*":
                            relative_path = source_file.relative_to(
                                Path(__file__).parent.parent
                            )
                            pytest.fail(
                                f"Star import found in {relative_path}:{node.lineno}"
                            )
    
    def test_init_files_have_valid_reexports(self):
        """
        Test that __init__.py files only re-export symbols that exist.
        
        __init__.py files are allowed to import without using because they
        re-export symbols for public API. This test verifies those re-exports
        are valid (the symbols actually exist in the source modules).
        """
        vince_dir = Path(__file__).parent.parent / "vince"
        
        for init_file in vince_dir.rglob("__init__.py"):
            if "__pycache__" in str(init_file):
                continue
            
            source_code = init_file.read_text()
            imports = extract_imports(source_code)
            
            # For each import, verify the source module exists
            for imp in imports:
                if imp.is_from_import and imp.module:
                    # Convert module path to file path
                    module_parts = imp.module.split(".")
                    
                    # Handle relative imports within vince package
                    if module_parts[0] == "vince":
                        module_path = vince_dir.parent
                        for part in module_parts:
                            module_path = module_path / part
                        
                        # Check if it's a module file or package
                        if not (module_path.with_suffix(".py").exists() or 
                                (module_path / "__init__.py").exists()):
                            relative_path = init_file.relative_to(
                                Path(__file__).parent.parent
                            )
                            pytest.fail(
                                f"{relative_path}: Cannot find module "
                                f"'{imp.module}' for import '{imp.name}'"
                            )
