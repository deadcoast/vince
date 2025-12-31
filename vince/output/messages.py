"""Vince CLI message output functions."""

from vince.output.theme import console


def print_success(message: str) -> None:
    """Print a success message with green checkmark.

    Format: [success]✓[/] {message}

    Args:
        message: The success message to display
    """
    console.print(f"[success]✓[/] {message}")


def print_warning(message: str) -> None:
    """Print a warning message with yellow warning symbol.

    Format: [warning]⚠[/] {message}

    Args:
        message: The warning message to display
    """
    console.print(f"[warning]⚠[/] {message}")


def print_error(code: str, message: str) -> None:
    """Print an error message with red X and error code.

    Format: [error]✗ {code}:[/] {message}

    Args:
        code: The error code (e.g., VE101)
        message: The error message to display
    """
    console.print(f"[error]✗ {code}:[/] {message}")


def print_info(message: str) -> None:
    """Print an info message with cyan info symbol.

    Format: [info]ℹ[/] {message}

    Args:
        message: The info message to display
    """
    console.print(f"[info]ℹ[/] {message}")
