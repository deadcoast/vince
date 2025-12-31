"""Vince CLI entry point."""

from typer import Typer, Option
from typing import Optional
import vince

app = Typer(
    name="vince",
    help="A Rich CLI for setting default applications to file extensions.",
    add_completion=False,
    rich_markup_mode="rich",
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from rich.console import Console
        console = Console()
        console.print(f"vince version {vince.__version__}")
        raise SystemExit(0)


@app.callback()
def main(
    version: Optional[bool] = Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Vince CLI - A Rich CLI for setting default applications to file extensions."""
    pass


if __name__ == "__main__":
    app()
