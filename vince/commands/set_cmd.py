"""Set command for vince CLI.

The set command directly sets a default for a file extension.
It creates an active default entry immediately (unlike slap without -set).
"""

from pathlib import Path
from typing import Optional

from typer import Argument, Option

from vince.config import get_config, get_data_dir
from vince.errors import VinceError, handle_error
from vince.output.messages import print_success, print_info
from vince.persistence.defaults import DefaultsStore
from vince.state.default_state import DefaultState, validate_transition
from vince.validation.extension import validate_extension
from vince.validation.path import validate_path


def cmd_set(
    path: Path = Argument(
        ...,
        help="Path to application executable",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
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
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Set a default application for a file extension.
    
    Creates an active default entry immediately.
    Raises error if default already exists for the extension.
    """
    try:
        # Load configuration
        config = get_config()
        verbose = verbose or config.get("verbose", False)
        backup_enabled = config.get("backup_enabled", True)
        max_backups = config.get("max_backups", 5)
        
        # Validate path
        validated_path = validate_path(path)
        
        if verbose:
            print_info(f"Processing path: [path]{validated_path}[/]")
        
        # Determine extension from flags
        ext = _get_extension_from_flags(
            md=md, py=py, txt=txt, js=js, html=html, css=css,
            json_ext=json_ext, yml=yml, yaml=yaml, xml=xml, csv=csv, sql=sql
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
        data_dir.mkdir(parents=True, exist_ok=True)
        
        defaults_store = DefaultsStore(data_dir)
        
        # Check existing default
        existing = defaults_store.find_by_extension(ext)
        current_state = DefaultState(existing["state"]) if existing else DefaultState.NONE
        target_state = DefaultState.ACTIVE
        
        if verbose:
            print_info(f"Current state: [state]{current_state.value}[/]")
            print_info(f"Target state: [state]{target_state.value}[/]")
        
        # Validate state transition
        validate_transition(current_state, target_state, ext)
        
        # Create or update default
        if existing:
            defaults_store.update_state(
                existing["id"],
                target_state.value,
                backup_enabled=backup_enabled,
                max_backups=max_backups
            )
            entry = existing
            entry["state"] = target_state.value
        else:
            entry = defaults_store.add(
                extension=ext,
                application_path=str(validated_path),
                state=target_state.value,
                application_name=validated_path.stem,
                backup_enabled=backup_enabled,
                max_backups=max_backups
            )
        
        # Print success message
        print_success(f"Default set for [extension]{ext}[/]")
        
        if verbose:
            print_info(f"Application: [path]{validated_path}[/]")
            print_info(f"Entry ID: {entry['id']}")
            print_info(f"State: [state]{target_state.value}[/]")
    
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
