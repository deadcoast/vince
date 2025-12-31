"""Vince CLI Rich theme and console configuration."""

from rich.console import Console
from rich.theme import Theme

# Define the vince CLI theme with all styles
VINCE_THEME = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "command": "magenta",
        "path": "blue underline",
        "extension": "cyan bold",
        "offer": "green italic",
        "state": "yellow",
        "header": "white bold",
    }
)

# Create themed console instance for use throughout the application
console = Console(theme=VINCE_THEME)
