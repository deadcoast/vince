"""List command for vince CLI.

The list command displays tracked assets and offers in Rich table format.
It supports various subsections: -app, -cmd, -ext, -def, -off, -all.

Requirements: 4.1, 4.2, 4.3, 4.4
"""

from typing import Dict, Optional

from typer import Option

from vince.config import get_config, get_data_dir
from vince.errors import InvalidSubsectionError, VinceError, handle_error
from vince.output.messages import print_info, print_warning
from vince.output.tables import create_defaults_table, create_offers_table
from vince.output.theme import console
from vince.persistence.defaults import DefaultsStore
from vince.persistence.offers import OffersStore
from vince.validation.extension import validate_extension

# Valid subsection flags
VALID_SUBSECTIONS = {"app", "cmd", "ext", "def", "off", "all"}


def cmd_list(
    app: bool = Option(False, "-app", help="List applications"),
    cmd: bool = Option(False, "-cmd", help="List commands"),
    ext: bool = Option(False, "-ext", help="List extensions"),
    defaults: bool = Option(False, "-def", help="List defaults"),
    offers: bool = Option(False, "-off", help="List offers"),
    all_sections: bool = Option(False, "-all", help="List all sections"),
    md: bool = Option(False, "--md", help="Filter by .md extension"),
    py: bool = Option(False, "--py", help="Filter by .py extension"),
    txt: bool = Option(False, "--txt", help="Filter by .txt extension"),
    js: bool = Option(False, "--js", help="Filter by .js extension"),
    html: bool = Option(False, "--html", help="Filter by .html extension"),
    css: bool = Option(False, "--css", help="Filter by .css extension"),
    json_ext: bool = Option(False, "--json", help="Filter by .json extension"),
    yml: bool = Option(False, "--yml", help="Filter by .yml extension"),
    yaml: bool = Option(False, "--yaml", help="Filter by .yaml extension"),
    xml: bool = Option(False, "--xml", help="Filter by .xml extension"),
    csv: bool = Option(False, "--csv", help="Filter by .csv extension"),
    sql: bool = Option(False, "--sql", help="Filter by .sql extension"),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Display tracked assets and offers.

    Use subsection flags to filter what is displayed:
    - -def: Show defaults table
    - -off: Show offers table
    - -all: Show all sections
    - -app: Show applications (from defaults)
    - -cmd: Show commands (from offers)
    - -ext: Show extensions (from defaults)

    Use extension flags (--md, --py, etc.) to filter by extension.
    """
    try:
        # Load configuration
        config = get_config()
        verbose = verbose or config.get("verbose", False)

        # Determine which subsection to display
        subsection = _get_subsection_from_flags(
            app=app,
            cmd=cmd,
            ext=ext,
            defaults=defaults,
            offers=offers,
            all_sections=all_sections,
        )

        # Default to -all if no subsection specified
        if subsection is None:
            subsection = "all"

        if verbose:
            print_info(f"Displaying subsection: [command]{subsection}[/]")

        # Get extension filter if specified
        ext_filter = _get_extension_from_flags(
            md=md,
            py=py,
            txt=txt,
            js=js,
            html=html,
            css=css,
            json_ext=json_ext,
            yml=yml,
            yaml=yaml,
            xml=xml,
            csv=csv,
            sql=sql,
        )

        if ext_filter:
            ext_filter = validate_extension(ext_filter)
            if verbose:
                print_info(f"Filtering by extension: [extension]{ext_filter}[/]")

        # Get data directory and stores
        data_dir = get_data_dir(config)
        defaults_store = DefaultsStore(data_dir)
        offers_store = OffersStore(data_dir)

        # Display based on subsection
        if subsection == "def":
            _display_defaults(defaults_store, ext_filter, verbose)
        elif subsection == "off":
            _display_offers(offers_store, defaults_store, ext_filter, verbose)
        elif subsection == "all":
            _display_defaults(defaults_store, ext_filter, verbose)
            console.print()  # Add spacing between tables
            _display_offers(offers_store, defaults_store, ext_filter, verbose)
        elif subsection == "app":
            _display_applications(defaults_store, ext_filter, verbose)
        elif subsection == "cmd":
            _display_commands(offers_store, verbose)
        elif subsection == "ext":
            _display_extensions(defaults_store, verbose)
        else:
            raise InvalidSubsectionError(subsection)

    except VinceError as e:
        handle_error(e)
    except Exception as e:
        from vince.errors import UnexpectedError

        handle_error(UnexpectedError(str(e)))


def _get_subsection_from_flags(
    app: bool,
    cmd: bool,
    ext: bool,
    defaults: bool,
    offers: bool,
    all_sections: bool,
) -> Optional[str]:
    """Get subsection string from boolean flags.

    Returns the first True flag's subsection, or None if no flags are set.
    """
    flag_map = {
        "app": app,
        "cmd": cmd,
        "ext": ext,
        "def": defaults,
        "off": offers,
        "all": all_sections,
    }

    for section, is_set in flag_map.items():
        if is_set:
            return section

    return None


def _get_extension_from_flags(
    md: bool,
    py: bool,
    txt: bool,
    js: bool,
    html: bool,
    css: bool,
    json_ext: bool,
    yml: bool,
    yaml: bool,
    xml: bool,
    csv: bool,
    sql: bool,
) -> Optional[str]:
    """Get extension string from boolean flags.

    Returns the first True flag's extension, or None if no flags are set.
    """
    flag_map = {
        ".md": md,
        ".py": py,
        ".txt": txt,
        ".js": js,
        ".html": html,
        ".css": css,
        ".json": json_ext,
        ".yml": yml,
        ".yaml": yaml,
        ".xml": xml,
        ".csv": csv,
        ".sql": sql,
    }

    for extension, is_set in flag_map.items():
        if is_set:
            return extension

    return None


def _display_defaults(
    defaults_store: DefaultsStore, ext_filter: Optional[str], verbose: bool
) -> None:
    """Display defaults table.

    Args:
        defaults_store: The defaults store to read from
        ext_filter: Optional extension to filter by
        verbose: Whether to show verbose output
    """
    all_defaults = defaults_store.find_all()

    # Filter by extension if specified
    if ext_filter:
        all_defaults = [d for d in all_defaults if d.get("extension") == ext_filter]

    # Filter out removed entries for cleaner display
    active_defaults = [d for d in all_defaults if d.get("state") != "removed"]

    if not active_defaults:
        print_warning("No defaults found")
        return

    table = create_defaults_table(active_defaults)
    console.print(table)

    if verbose:
        print_info(f"Total defaults: {len(active_defaults)}")


def _display_offers(
    offers_store: OffersStore,
    defaults_store: DefaultsStore,
    ext_filter: Optional[str],
    verbose: bool,
) -> None:
    """Display offers table.

    Args:
        offers_store: The offers store to read from
        defaults_store: The defaults store for extension filtering
        ext_filter: Optional extension to filter by
        verbose: Whether to show verbose output
    """
    all_offers = offers_store.find_all()

    # Filter by extension if specified (need to look up default to get extension)
    if ext_filter:
        filtered_offers = []
        for offer in all_offers:
            default = defaults_store.find_by_id(offer.get("default_id", ""))
            if default and default.get("extension") == ext_filter:
                filtered_offers.append(offer)
        all_offers = filtered_offers

    # Filter out rejected entries for cleaner display
    active_offers = [o for o in all_offers if o.get("state") != "rejected"]

    if not active_offers:
        print_warning("No offers found")
        return

    table = create_offers_table(active_offers)
    console.print(table)

    if verbose:
        print_info(f"Total offers: {len(active_offers)}")


def _display_applications(
    defaults_store: DefaultsStore, ext_filter: Optional[str], verbose: bool
) -> None:
    """Display unique applications from defaults.

    Args:
        defaults_store: The defaults store to read from
        ext_filter: Optional extension to filter by
        verbose: Whether to show verbose output
    """
    from rich import box
    from rich.table import Table

    all_defaults = defaults_store.find_all()

    # Filter by extension if specified
    if ext_filter:
        all_defaults = [d for d in all_defaults if d.get("extension") == ext_filter]

    # Filter out removed entries
    active_defaults = [d for d in all_defaults if d.get("state") != "removed"]

    # Get unique applications
    apps = {}
    for d in active_defaults:
        path = d.get("application_path", "")
        name = d.get("application_name", path.split("/")[-1] if path else "unknown")
        if path not in apps:
            apps[path] = {"name": name, "path": path, "extensions": []}
        apps[path]["extensions"].append(d.get("extension", ""))

    if not apps:
        print_warning("No applications found")
        return

    table = Table(title="Applications", box=box.ROUNDED, header_style="header")
    table.add_column("Name", style="info")
    table.add_column("Path", style="path")
    table.add_column("Extensions", style="extension")

    for app_info in apps.values():
        table.add_row(
            app_info["name"], app_info["path"], ", ".join(app_info["extensions"])
        )

    console.print(table)

    if verbose:
        print_info(f"Total applications: {len(apps)}")


def _display_commands(offers_store: OffersStore, verbose: bool) -> None:
    """Display offer commands/aliases.

    Args:
        offers_store: The offers store to read from
        verbose: Whether to show verbose output
    """
    from rich import box
    from rich.table import Table

    all_offers = offers_store.find_all()

    # Filter out rejected entries
    active_offers = [o for o in all_offers if o.get("state") != "rejected"]

    if not active_offers:
        print_warning("No commands found")
        return

    table = Table(title="Commands", box=box.ROUNDED, header_style="header")
    table.add_column("Command", style="command")
    table.add_column("Default ID", style="info")
    table.add_column("Auto-created", style="state")

    for offer in active_offers:
        table.add_row(
            offer.get("offer_id", ""),
            offer.get("default_id", ""),
            "Yes" if offer.get("auto_created", False) else "No",
        )

    console.print(table)

    if verbose:
        print_info(f"Total commands: {len(active_offers)}")


def _display_extensions(defaults_store: DefaultsStore, verbose: bool) -> None:
    """Display extensions with defaults.

    Args:
        defaults_store: The defaults store to read from
        verbose: Whether to show verbose output
    """
    from rich import box
    from rich.table import Table

    all_defaults = defaults_store.find_all()

    # Filter out removed entries
    active_defaults = [d for d in all_defaults if d.get("state") != "removed"]

    # Get unique extensions with their status
    extensions = {}
    for d in active_defaults:
        ext = d.get("extension", "")
        if ext not in extensions:
            extensions[ext] = {"extension": ext, "count": 0, "states": set()}
        extensions[ext]["count"] += 1
        extensions[ext]["states"].add(d.get("state", ""))

    if not extensions:
        print_warning("No extensions found")
        return

    table = Table(title="Extensions", box=box.ROUNDED, header_style="header")
    table.add_column("Extension", style="extension")
    table.add_column("Defaults", style="info")
    table.add_column("States", style="state")

    for ext_info in sorted(extensions.values(), key=lambda x: x["extension"]):
        table.add_row(
            ext_info["extension"],
            str(ext_info["count"]),
            ", ".join(sorted(ext_info["states"])),
        )

    console.print(table)

    if verbose:
        print_info(f"Total extensions: {len(extensions)}")
