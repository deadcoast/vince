"""Forget command for vince CLI.

The forget command forgets a default for a file extension.
It transitions the default state to removed.

OS Integration:
The command also removes the OS association via the platform handler.
If the OS operation fails, a warning is shown.
"""

from typing import Optional

from typer import Option

from vince.config import get_config, get_data_dir
from vince.errors import NoDefaultError, VinceError, handle_error
from vince.output.messages import print_info, print_success, print_warning
from vince.persistence.defaults import DefaultsStore
from vince.state.default_state import DefaultState, validate_transition
from vince.validation.extension import validate_extension


def cmd_forget(
    md: bool = Option(False, "--md", help="Target .md files"),
    py: bool = Option(False, "--py", help="Target .py files"),
    txt: bool = Option(False, "--txt", help="Target .txt files"),
    js: bool = Option(False, "--js", help="Target .js files"),
    html: bool = Option(False, "--html", help="Target .html files"),
    css: bool = Option(False, "--css", help="Target .css files"),
    json_ext: bool = Option(False, "--json", help="Target .json files"),
    yml: bool = Option(False, "--yml", help="Target .yml files"),
    yaml: bool = Option(False, "--yaml", help="Target .yaml files"),
    xml: bool = Option(False, "--xml", help="Target .xml files"),
    csv: bool = Option(False, "--csv", help="Target .csv files"),
    sql: bool = Option(False, "--sql", help="Target .sql files"),
    dry_run: bool = Option(
        False,
        "-dry",
        help="Preview changes without applying them to the OS",
    ),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Forget a default for a file extension.

    Transitions the default state to removed and removes OS association.
    Raises error if no default exists for the extension.
    """
    try:
        # Load configuration
        config = get_config()
        verbose = verbose or config.get("verbose", False)
        backup_enabled = config.get("backup_enabled", True)
        max_backups = config.get("max_backups", 5)

        # Determine extension from flags
        ext = _get_extension_from_flags(
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

        if ext is None:
            from vince.errors import InvalidExtensionError

            raise InvalidExtensionError("No extension specified. Use --md, --py, etc.")

        # Validate extension
        ext = validate_extension(ext)

        if verbose:
            print_info(f"Target extension: [extension]{ext}[/]")

        # Get data directory and store
        data_dir = get_data_dir(config)
        defaults_store = DefaultsStore(data_dir)

        # Find existing default
        existing = defaults_store.find_by_extension(ext)

        if existing is None:
            raise NoDefaultError(ext)

        current_state = DefaultState(existing["state"])

        if verbose:
            print_info(f"Current state: [state]{current_state.value}[/]")
            print_info(f"Application: [path]{existing['application_path']}[/]")

        # Determine target state based on current state
        if current_state == DefaultState.PENDING:
            # Pending defaults go back to NONE (conceptually)
            target_state = DefaultState.NONE
        else:
            # Active defaults go to REMOVED
            target_state = DefaultState.REMOVED

        if verbose:
            print_info(f"Target state: [state]{target_state.value}[/]")

        # Validate state transition
        validate_transition(current_state, target_state, ext)

        # Update state - always mark as "removed" in storage
        defaults_store.update_state(
            existing["id"],
            "removed",
            backup_enabled=backup_enabled,
            max_backups=max_backups,
        )

        # Remove OS association via platform handler
        try:
            from vince.platform import get_handler, get_platform, Platform
            from vince.platform.errors import UnsupportedPlatformError

            platform = get_platform()
            if platform != Platform.UNSUPPORTED:
                handler = get_handler()

                if dry_run:
                    # Show what would happen
                    result = handler.remove_default(ext, dry_run=True)
                    print_info(f"[dry run] {result.message}")
                    if result.previous_default:
                        print_info(
                            f"[dry run] Previous OS default: {result.previous_default}"
                        )
                else:
                    # Actually remove the association
                    result = handler.remove_default(ext, dry_run=False)
                    if result.success:
                        if verbose:
                            print_info(f"OS association removed: {result.message}")
                    else:
                        print_warning(
                            f"OS operation failed: {result.message}. "
                            "OS association may still be active."
                        )
            else:
                if verbose:
                    print_info("OS integration not available on this platform")
        except UnsupportedPlatformError:
            if verbose:
                print_info("OS integration not available on this platform")
        except Exception as e:
            print_warning(
                f"OS operation failed: {e}. OS association may still be active."
            )

        print_success(f"Default forgotten for [extension]{ext}[/]")

        if verbose:
            print_info(f"Entry ID: {existing['id']}")

    except VinceError as e:
        handle_error(e)
    except Exception as e:
        from vince.errors import UnexpectedError

        handle_error(UnexpectedError(str(e)))


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

    for ext, is_set in flag_map.items():
        if is_set:
            return ext

    return None
