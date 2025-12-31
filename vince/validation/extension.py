"""Extension validation for vince CLI.

This module provides validation functions for file extensions.
Validates that extensions match the required pattern and are supported.
"""

import re

from vince.errors import InvalidExtensionError


# Pattern for valid extensions: dot followed by lowercase alphanumeric
EXTENSION_PATTERN = re.compile(r'^\.[a-z0-9]+$')

# Set of supported file extensions
SUPPORTED_EXTENSIONS = {
    ".md", ".py", ".txt", ".js", ".html", ".css",
    ".json", ".yml", ".yaml", ".xml", ".csv", ".sql"
}


def validate_extension(ext: str) -> str:
    """Validate file extension format and support.
    
    Performs two checks:
    1. Extension matches pattern ^\.[a-z0-9]+$
    2. Extension is in the supported extensions set
    
    Args:
        ext: File extension to validate (e.g., ".md", ".py")
        
    Returns:
        The lowercase extension if validation passes
        
    Raises:
        InvalidExtensionError: If extension is invalid or unsupported (VE102)
    """
    # Normalize to lowercase
    ext = ext.lower()
    
    # Check pattern match
    if not EXTENSION_PATTERN.match(ext):
        raise InvalidExtensionError(ext)
    
    # Check if supported
    if ext not in SUPPORTED_EXTENSIONS:
        raise InvalidExtensionError(ext)
    
    return ext


def flag_to_extension(flag: str) -> str:
    """Convert CLI flag to extension format.
    
    Converts flags like "--md" or "md" to ".md" format.
    
    Args:
        flag: CLI flag string (e.g., "--md", "-md", "md")
        
    Returns:
        Extension in dot format (e.g., ".md")
    """
    # Remove leading dashes
    if flag.startswith("--"):
        ext_name = flag[2:]
    elif flag.startswith("-"):
        ext_name = flag[1:]
    else:
        ext_name = flag
    
    # Add dot prefix if not present
    if not ext_name.startswith("."):
        return f".{ext_name}"
    
    return ext_name
