"""Vince CLI entry point."""

from typing import Optional

from typer import Option, Typer

import vince

from vince.commands.chop import cmd_chop
from vince.commands.forget import cmd_forget
from vince.commands.list_cmd import cmd_list
from vince.commands.offer import cmd_offer
from vince.commands.reject import cmd_reject
from vince.commands.set_cmd import cmd_set
# Import and register commands
from vince.commands.slap import cmd_slap

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

app.command(name="slap")(cmd_slap)
app.command(name="chop")(cmd_chop)
app.command(name="set")(cmd_set)
app.command(name="forget")(cmd_forget)
app.command(name="offer")(cmd_offer)
app.command(name="reject")(cmd_reject)
app.command(name="list")(cmd_list)


if __name__ == "__main__":
    app()
