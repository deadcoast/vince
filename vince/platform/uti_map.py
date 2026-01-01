"""Extension to UTI (Uniform Type Identifier) mapping for macOS.

This module provides mapping between file extensions and macOS UTIs
(Uniform Type Identifiers). UTIs are Apple's system for identifying
file types and are required for setting file associations via
Launch Services.

Requirements: 2.2, 2.5
"""

from typing import Optional

# Mapping of file extensions to macOS UTIs
# Covers all 12 supported extensions from vince.validation.extension
UTI_MAP: dict[str, str] = {
    # Markdown
    ".md": "net.daringfireball.markdown",
    ".markdown": "net.daringfireball.markdown",
    # Python
    ".py": "public.python-script",
    # Plain text
    ".txt": "public.plain-text",
    # JavaScript
    ".js": "com.netscape.javascript-source",
    # HTML
    ".html": "public.html",
    ".htm": "public.html",
    # CSS
    ".css": "public.css",
    # JSON
    ".json": "public.json",
    # YAML
    ".yml": "public.yaml",
    ".yaml": "public.yaml",
    # XML
    ".xml": "public.xml",
    # CSV
    ".csv": "public.comma-separated-values-text",
    # SQL
    ".sql": "public.sql",
}


def extension_to_uti(extension: str) -> Optional[str]:
    """Convert file extension to macOS UTI.

    Args:
        extension: File extension with or without leading dot
                   (e.g., ".md", "md", ".py", "py")

    Returns:
        The corresponding UTI string if found, None otherwise

    Examples:
        >>> extension_to_uti(".md")
        'net.daringfireball.markdown'
        >>> extension_to_uti("py")
        'public.python-script'
        >>> extension_to_uti(".unknown")
        None
    """
    ext = extension.lower()
    if not ext.startswith("."):
        ext = f".{ext}"
    return UTI_MAP.get(ext)


def uti_to_extension(uti: str) -> Optional[str]:
    """Convert UTI back to primary file extension.

    Returns the first (primary) extension that maps to the given UTI.
    For UTIs with multiple extensions (e.g., .yml and .yaml both map
    to public.yaml), returns the first one found in the mapping.

    Args:
        uti: macOS Uniform Type Identifier string

    Returns:
        The primary file extension for the UTI, or None if not found

    Examples:
        >>> uti_to_extension("net.daringfireball.markdown")
        '.md'
        >>> uti_to_extension("public.python-script")
        '.py'
        >>> uti_to_extension("unknown.uti")
        None
    """
    for ext, mapped_uti in UTI_MAP.items():
        if mapped_uti == uti:
            return ext
    return None


def get_all_utis() -> set[str]:
    """Get all unique UTIs in the mapping.

    Returns:
        Set of all unique UTI strings

    Examples:
        >>> utis = get_all_utis()
        >>> "public.python-script" in utis
        True
    """
    return set(UTI_MAP.values())


def get_extensions_for_uti(uti: str) -> list[str]:
    """Get all extensions that map to a given UTI.

    Some UTIs have multiple extensions (e.g., .yml and .yaml both
    map to public.yaml). This function returns all of them.

    Args:
        uti: macOS Uniform Type Identifier string

    Returns:
        List of all extensions mapping to the UTI, empty if none found

    Examples:
        >>> get_extensions_for_uti("public.yaml")
        ['.yml', '.yaml']
        >>> get_extensions_for_uti("public.python-script")
        ['.py']
    """
    return [ext for ext, mapped_uti in UTI_MAP.items() if mapped_uti == uti]
