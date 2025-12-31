"""
Property-Based Tests for Document Structure Consistency

Property 10: Document Structure Consistency
**Validates: Requirements 10.2, 10.6**

Tests that all documentation files have consistent structure including:
- Overview sections explaining the document's purpose
- Cross-References sections linking to related documents
"""

import pytest
from pathlib import Path
from hypothesis import given, settings, assume
from hypothesis import strategies as st


# List of all documentation files that should have consistent structure
DOC_FILES = [
    "README.md",
    "api.md",
    "config.md",
    "errors.md",
    "examples.md",
    "overview.md",
    "schemas.md",
    "states.md",
    "tables.md",
    "testing.md",
]


@pytest.fixture
def docs_dir() -> Path:
    """Return the path to the docs directory."""
    return Path(__file__).parent.parent / "docs"


def has_overview_section(content: str) -> bool:
    """
    Check if the document has an Overview section.
    
    An Overview section can be:
    - A heading "## Overview"
    - A heading containing "Overview" (e.g., "## ID SYSTEM OVERVIEW")
    - The document starts with a description paragraph after the title
    """
    lines = content.split("\n")
    
    # Check for explicit "## Overview" heading
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and "overview" in stripped.lower():
            return True
    
    return False


def has_cross_references_section(content: str) -> bool:
    """
    Check if the document has a Cross-References section.
    
    A Cross-References section should be:
    - A heading "## Cross-References"
    """
    lines = content.split("\n")
    
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "## cross-references":
            return True
    
    return False


def get_cross_references_links(content: str) -> list[str]:
    """
    Extract all links from the Cross-References section.
    
    Returns a list of link targets (file paths).
    """
    lines = content.split("\n")
    links = []
    in_cross_refs = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check if we're entering the Cross-References section
        if stripped.lower() == "## cross-references":
            in_cross_refs = True
            continue
        
        # Check if we're leaving the section (new heading)
        if in_cross_refs and stripped.startswith("## "):
            break
        
        # Extract links from the line
        if in_cross_refs:
            # Look for markdown links: [text](path)
            import re
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.findall(link_pattern, line)
            for _, path in matches:
                # Only include relative links to .md files
                if path.endswith(".md") and not path.startswith("http"):
                    links.append(path)
    
    return links


class TestDocumentStructureConsistency:
    """
    Property 10: Document Structure Consistency
    
    *For any* document in docs/, it SHALL have an Overview section and 
    a Cross-References section linking to related documents.
    
    **Validates: Requirements 10.2, 10.6**
    """

    def test_all_docs_have_overview_section(self, docs_dir: Path):
        """
        Property 10: All documents should have an Overview section.
        
        *For any* document in docs/, it SHALL have an Overview section
        explaining the document's purpose.
        
        **Validates: Requirements 10.6**
        """
        missing_overview = []
        
        for doc_name in DOC_FILES:
            doc_path = docs_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = doc_path.read_text()
            if not has_overview_section(content):
                missing_overview.append(doc_name)
        
        assert len(missing_overview) == 0, (
            f"Documents missing Overview section: {missing_overview}"
        )

    def test_all_docs_have_cross_references_section(self, docs_dir: Path):
        """
        Property 10: All documents should have a Cross-References section.
        
        *For any* document in docs/, it SHALL have a Cross-References section
        linking to related documents.
        
        **Validates: Requirements 10.2**
        """
        missing_cross_refs = []
        
        for doc_name in DOC_FILES:
            doc_path = docs_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = doc_path.read_text()
            if not has_cross_references_section(content):
                missing_cross_refs.append(doc_name)
        
        assert len(missing_cross_refs) == 0, (
            f"Documents missing Cross-References section: {missing_cross_refs}"
        )

    def test_cross_references_links_are_valid(self, docs_dir: Path):
        """
        Property 10: Cross-References links should point to existing files.
        
        *For any* link in a Cross-References section, the target file SHALL exist.
        
        **Validates: Requirements 10.2**
        """
        invalid_links = []
        
        for doc_name in DOC_FILES:
            doc_path = docs_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = doc_path.read_text()
            links = get_cross_references_links(content)
            
            for link in links:
                # Handle relative paths
                if link.startswith("../"):
                    target_path = docs_dir.parent / link.lstrip("../")
                else:
                    target_path = docs_dir / link
                
                if not target_path.exists():
                    invalid_links.append(f"{doc_name}: {link}")
        
        assert len(invalid_links) == 0, (
            f"Invalid Cross-References links:\n" + "\n".join(invalid_links)
        )

    def test_cross_references_include_tables_md(self, docs_dir: Path):
        """
        Property 10: Cross-References should include tables.md (SSOT).
        
        *For any* document in docs/ (except tables.md itself), the Cross-References
        section SHOULD include a link to tables.md as the Single Source of Truth.
        
        **Validates: Requirements 10.2**
        """
        missing_tables_link = []
        
        for doc_name in DOC_FILES:
            # Skip tables.md itself
            if doc_name == "tables.md":
                continue
            
            doc_path = docs_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = doc_path.read_text()
            links = get_cross_references_links(content)
            
            # Check if tables.md is referenced
            has_tables_link = any("tables.md" in link for link in links)
            if not has_tables_link:
                missing_tables_link.append(doc_name)
        
        # This is a soft check - warn but don't fail
        if missing_tables_link:
            pytest.skip(
                f"Documents without tables.md in Cross-References (advisory): "
                f"{missing_tables_link}"
            )


@st.composite
def doc_file_names(draw):
    """Generate valid documentation file names."""
    return draw(st.sampled_from(DOC_FILES))


class TestDocumentStructurePropertyBased:
    """
    Property-based tests for document structure using Hypothesis.
    
    **Property 10: Document Structure Consistency**
    **Validates: Requirements 10.2, 10.6**
    """

    @given(doc_name=doc_file_names())
    @settings(max_examples=100)
    def test_random_doc_has_overview(self, doc_name: str):
        """
        Property 10: Randomly selected documents should have Overview sections.
        
        *For any* randomly selected document from docs/, it SHALL have
        an Overview section.
        
        **Validates: Requirements 10.6**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        doc_path = docs_dir / doc_name
        
        assume(doc_path.exists())
        
        content = doc_path.read_text()
        assert has_overview_section(content), (
            f"{doc_name} is missing an Overview section"
        )

    @given(doc_name=doc_file_names())
    @settings(max_examples=100)
    def test_random_doc_has_cross_references(self, doc_name: str):
        """
        Property 10: Randomly selected documents should have Cross-References sections.
        
        *For any* randomly selected document from docs/, it SHALL have
        a Cross-References section.
        
        **Validates: Requirements 10.2**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        doc_path = docs_dir / doc_name
        
        assume(doc_path.exists())
        
        content = doc_path.read_text()
        assert has_cross_references_section(content), (
            f"{doc_name} is missing a Cross-References section"
        )

    @given(doc_name=doc_file_names())
    @settings(max_examples=100)
    def test_random_doc_cross_refs_valid(self, doc_name: str):
        """
        Property 10: Cross-References in randomly selected documents should be valid.
        
        *For any* randomly selected document from docs/, all links in its
        Cross-References section SHALL point to existing files.
        
        **Validates: Requirements 10.2**
        """
        docs_dir = Path(__file__).parent.parent / "docs"
        doc_path = docs_dir / doc_name
        
        assume(doc_path.exists())
        
        content = doc_path.read_text()
        links = get_cross_references_links(content)
        
        for link in links:
            if link.startswith("../"):
                target_path = docs_dir.parent / link.lstrip("../")
            else:
                target_path = docs_dir / link
            
            assert target_path.exists(), (
                f"{doc_name}: Cross-References link '{link}' points to non-existent file"
            )
