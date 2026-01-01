"""
Property-Based Tests for UTI Mapping

Feature: os-integration
Property 2: UTI Mapping Completeness
Validates: Requirements 2.2, 2.5

Tests that:
- All supported extensions have UTI mappings
- Extension-to-UTI mapping is complete for all supported extensions
- UTI-to-extension reverse lookup works correctly
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from vince.platform.uti_map import (
    UTI_MAP,
    extension_to_uti,
    get_all_utis,
    get_extensions_for_uti,
    uti_to_extension,
)
from vince.validation.extension import SUPPORTED_EXTENSIONS


# =============================================================================
# Property Test: UTI Mapping Completeness
# Feature: os-integration, Property 2: UTI Mapping Completeness
# Validates: Requirements 2.2, 2.5
# =============================================================================


class TestUTIMappingCompleteness:
    """Property tests for UTI mapping completeness.

    Property 2: UTI Mapping Completeness
    *For any* supported extension, the UTI_MAP SHALL contain a valid UTI mapping,
    and the extension_to_uti function SHALL return a non-None value.

    Validates: Requirements 2.2, 2.5
    """

    @given(extension=st.sampled_from(list(SUPPORTED_EXTENSIONS)))
    @settings(max_examples=100)
    def test_all_supported_extensions_have_uti_mapping(self, extension: str):
        """Property: All supported extensions must have a UTI mapping.

        *For any* extension in SUPPORTED_EXTENSIONS, extension_to_uti(ext)
        SHALL return a non-None UTI string.

        **Validates: Requirements 2.2, 2.5**
        """
        uti = extension_to_uti(extension)
        assert uti is not None, f"Extension {extension} has no UTI mapping"
        assert isinstance(uti, str), f"UTI for {extension} is not a string"
        assert len(uti) > 0, f"UTI for {extension} is empty"

    @given(extension=st.sampled_from(list(SUPPORTED_EXTENSIONS)))
    @settings(max_examples=100)
    def test_extension_to_uti_handles_with_and_without_dot(self, extension: str):
        """Property: extension_to_uti works with or without leading dot.

        *For any* supported extension, calling extension_to_uti with or without
        the leading dot SHALL return the same UTI.

        **Validates: Requirements 2.2**
        """
        # Extension with dot
        uti_with_dot = extension_to_uti(extension)

        # Extension without dot
        ext_without_dot = extension.lstrip(".")
        uti_without_dot = extension_to_uti(ext_without_dot)

        assert uti_with_dot == uti_without_dot, (
            f"UTI mismatch for {extension}: "
            f"with dot={uti_with_dot}, without dot={uti_without_dot}"
        )

    @given(extension=st.sampled_from(list(SUPPORTED_EXTENSIONS)))
    @settings(max_examples=100)
    def test_extension_to_uti_case_insensitive(self, extension: str):
        """Property: extension_to_uti is case-insensitive.

        *For any* supported extension, calling extension_to_uti with different
        cases SHALL return the same UTI.

        **Validates: Requirements 2.2**
        """
        uti_lower = extension_to_uti(extension.lower())
        uti_upper = extension_to_uti(extension.upper())

        assert uti_lower == uti_upper, (
            f"UTI mismatch for case variants of {extension}: "
            f"lower={uti_lower}, upper={uti_upper}"
        )


class TestUTIReverseMapping:
    """Tests for UTI to extension reverse lookup."""

    def test_all_utis_have_at_least_one_extension(self):
        """Every UTI in the map should have at least one extension."""
        all_utis = get_all_utis()
        for uti in all_utis:
            extensions = get_extensions_for_uti(uti)
            assert len(extensions) > 0, f"UTI {uti} has no extensions"

    @given(extension=st.sampled_from(list(SUPPORTED_EXTENSIONS)))
    @settings(max_examples=100)
    def test_uti_to_extension_returns_valid_extension(self, extension: str):
        """Property: uti_to_extension returns a valid extension for known UTIs.

        *For any* supported extension, getting its UTI and then reversing
        SHALL return a valid extension (possibly different due to aliases).

        **Validates: Requirements 2.2**
        """
        uti = extension_to_uti(extension)
        assert uti is not None

        reversed_ext = uti_to_extension(uti)
        assert reversed_ext is not None, f"No reverse mapping for UTI {uti}"
        assert reversed_ext.startswith("."), f"Extension {reversed_ext} missing dot"


class TestUTIMapStructure:
    """Tests for UTI_MAP dictionary structure."""

    def test_uti_map_contains_all_supported_extensions(self):
        """UTI_MAP must contain all supported extensions."""
        for ext in SUPPORTED_EXTENSIONS:
            assert ext in UTI_MAP, f"Extension {ext} not in UTI_MAP"

    def test_uti_map_values_are_valid_uti_format(self):
        """All UTI values should follow UTI naming conventions."""
        for ext, uti in UTI_MAP.items():
            # UTIs are reverse-DNS style or public.* format
            assert "." in uti, f"UTI {uti} for {ext} doesn't contain a dot"
            assert not uti.startswith("."), f"UTI {uti} for {ext} starts with dot"
            assert not uti.endswith("."), f"UTI {uti} for {ext} ends with dot"

    def test_uti_map_keys_are_lowercase_with_dot(self):
        """All extension keys should be lowercase with leading dot."""
        for ext in UTI_MAP.keys():
            assert ext.startswith("."), f"Extension {ext} missing leading dot"
            assert ext == ext.lower(), f"Extension {ext} is not lowercase"

    def test_supported_extensions_count(self):
        """Verify we have mappings for all 12 supported extensions."""
        # The 12 supported extensions from requirements
        required_extensions = {
            ".md",
            ".py",
            ".txt",
            ".js",
            ".html",
            ".css",
            ".json",
            ".yml",
            ".yaml",
            ".xml",
            ".csv",
            ".sql",
        }
        for ext in required_extensions:
            assert extension_to_uti(ext) is not None, (
                f"Required extension {ext} has no UTI mapping"
            )


class TestUTIMapEdgeCases:
    """Tests for edge cases in UTI mapping."""

    def test_unknown_extension_returns_none(self):
        """Unknown extensions should return None."""
        assert extension_to_uti(".unknown") is None
        assert extension_to_uti(".xyz") is None
        assert extension_to_uti("notanext") is None

    def test_unknown_uti_returns_none(self):
        """Unknown UTIs should return None."""
        assert uti_to_extension("unknown.uti") is None
        assert uti_to_extension("com.example.fake") is None

    def test_empty_string_returns_none(self):
        """Empty string should return None."""
        assert extension_to_uti("") is None

    def test_get_extensions_for_unknown_uti_returns_empty(self):
        """Unknown UTI should return empty list."""
        result = get_extensions_for_uti("unknown.uti")
        assert result == []

    def test_yaml_aliases_map_to_same_uti(self):
        """Both .yml and .yaml should map to the same UTI."""
        yml_uti = extension_to_uti(".yml")
        yaml_uti = extension_to_uti(".yaml")
        assert yml_uti == yaml_uti == "public.yaml"

    def test_markdown_aliases_map_to_same_uti(self):
        """Both .md and .markdown should map to the same UTI."""
        md_uti = extension_to_uti(".md")
        markdown_uti = extension_to_uti(".markdown")
        assert md_uti == markdown_uti == "net.daringfireball.markdown"

    def test_html_aliases_map_to_same_uti(self):
        """Both .html and .htm should map to the same UTI."""
        html_uti = extension_to_uti(".html")
        htm_uti = extension_to_uti(".htm")
        assert html_uti == htm_uti == "public.html"
