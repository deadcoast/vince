"""Sync command for vince CLI.

The sync command applies all active defaults to the OS at once.
It checks each active default against the current OS default and
applies changes for out-of-sync entries.

Requirements: 6.1, 6.2, 6.3, 6.4
"""

from pathlib import Path
from typing import List, Tuple

from typer import Option

from vince.config import get_config, get_data_dir
from vince.errors import VinceError, handle_error
from vince.output.messages import print_info, print_success, print_warning
from vince.persistence.defaults import DefaultsStore
from vince.platform import Platform, get_handler, get_platform
from vince.platform.errors import SyncPartialError, UnsupportedPlatformError


def cmd_sync(
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
    """Sync all active defaults to the OS.

    Applies all active defaults from the JSON store to the operating system.
    Skips entries that are already correctly configured.
    Reports success/failure for each extension.

    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    try:
        # Load configuration
        config = get_config()
        verbose = verbose or config.get("verbose", False)
        backup_enabled = config.get("backup_enabled", True)
        max_backups = config.get("max_backups", 5)

        # Get data directory and store
        data_dir = get_data_dir(config)
        defaults_store = DefaultsStore(data_dir)

        # Load all active defaults
        active_defaults = defaults_store.find_active_defaults()

        if not active_defaults:
            print_info("No active defaults to sync")
            return

        if verbose:
            print_info(f"Found {len(active_defaults)} active default(s) to sync")

        # Get platform handler
        try:
            platform = get_platform()
            if platform == Platform.UNSUPPORTED:
                raise UnsupportedPlatformError("current platform")

            handler = get_handler()
        except UnsupportedPlatformError as e:
            handle_error(e)
            return

        # Track results
        succeeded: List[str] = []
        failed: List[Tuple[str, str]] = []  # (extension, error_message)
        skipped: List[str] = []

        # Process each active default
        for entry in active_defaults:
            ext = entry["extension"]
            app_path = Path(entry["application_path"])

            if verbose:
                print_info(f"Processing [extension]{ext}[/]...")

            # Check if already synced and OS default matches
            os_synced = entry.get("os_synced", False)
            if os_synced:
                # Verify the OS default still matches
                try:
                    current_os_default = handler.get_current_default(ext)
                    if current_os_default:
                        # Normalize paths for comparison
                        current_path = Path(current_os_default).resolve()
                        target_path = app_path.resolve()

                        # Check if paths match (or if app name matches for macOS bundles)
                        if _paths_match(current_path, target_path):
                            if verbose:
                                print_info(
                                    f"[extension]{ext}[/] already synced, skipping"
                                )
                            skipped.append(ext)
                            continue
                except Exception:
                    # If we can't query, proceed with sync
                    pass

            # Apply the change
            try:
                if dry_run:
                    result = handler.set_default(ext, app_path, dry_run=True)
                    print_info(f"[dry run] {ext}: {result.message}")
                    if result.previous_default:
                        print_info(
                            f"[dry run] Previous OS default: {result.previous_default}"
                        )
                    succeeded.append(ext)
                else:
                    result = handler.set_default(ext, app_path, dry_run=False)
                    if result.success:
                        # Update OS sync status in store
                        defaults_store.update_os_sync_status(
                            entry["id"],
                            os_synced=True,
                            previous_os_default=result.previous_default,
                            backup_enabled=backup_enabled,
                            max_backups=max_backups,
                        )
                        succeeded.append(ext)
                        if verbose:
                            print_success(f"[extension]{ext}[/]: {result.message}")
                    else:
                        failed.append((ext, result.message))
                        if verbose:
                            print_warning(f"[extension]{ext}[/]: {result.message}")
            except Exception as e:
                failed.append((ext, str(e)))
                if verbose:
                    print_warning(f"[extension]{ext}[/]: {e}")

        # Report results
        _report_sync_results(
            succeeded=succeeded,
            failed=failed,
            skipped=skipped,
            dry_run=dry_run,
            verbose=verbose,
        )

        # Raise partial error if there were failures (and not dry run)
        if failed and not dry_run:
            raise SyncPartialError(
                succeeded=len(succeeded),
                failed=len(failed),
                failures=[ext for ext, _ in failed],
            )

    except SyncPartialError as e:
        # Don't use handle_error for partial success - just print warning
        print_warning(str(e))
        if e.recovery:
            print_info(e.recovery)
    except VinceError as e:
        handle_error(e)
    except Exception as e:
        from vince.errors import UnexpectedError

        handle_error(UnexpectedError(str(e)))


def _paths_match(path1: Path, path2: Path) -> bool:
    """Check if two paths refer to the same application.

    Handles macOS .app bundles where the executable path may differ
    from the bundle path.

    Args:
        path1: First path to compare
        path2: Second path to compare

    Returns:
        True if paths refer to the same application
    """
    # Direct match
    if path1 == path2:
        return True

    # Check if one is inside the other (for .app bundles)
    try:
        path1_str = str(path1)
        path2_str = str(path2)

        # If one path contains the other
        if path1_str in path2_str or path2_str in path1_str:
            return True

        # Check for .app bundle match
        # e.g., /Applications/VSCode.app vs /Applications/VSCode.app/Contents/MacOS/Electron
        for p1, p2 in [(path1, path2), (path2, path1)]:
            if p1.suffix == ".app":
                if str(p2).startswith(str(p1)):
                    return True
            # Find .app in path
            for parent in p1.parents:
                if parent.suffix == ".app":
                    if str(p2).startswith(str(parent)) or parent == p2:
                        return True
    except Exception:
        pass

    return False


def _report_sync_results(
    succeeded: List[str],
    failed: List[Tuple[str, str]],
    skipped: List[str],
    dry_run: bool,
    verbose: bool,
) -> None:
    """Report sync operation results.

    Args:
        succeeded: List of successfully synced extensions
        failed: List of (extension, error_message) tuples for failures
        skipped: List of skipped extensions (already synced)
        dry_run: Whether this was a dry run
        verbose: Whether verbose output is enabled
    """
    if dry_run:
        print_info(f"[dry run] Would sync {len(succeeded)} extension(s)")
        if skipped:
            print_info(f"[dry run] {len(skipped)} extension(s) already synced")
        return

    # Summary message
    if not failed:
        if succeeded:
            print_success(
                f"Synced {len(succeeded)} extension(s): {', '.join(succeeded)}"
            )
        if skipped and verbose:
            print_info(f"Skipped {len(skipped)} already-synced extension(s)")
    else:
        if succeeded:
            print_success(f"Synced {len(succeeded)} extension(s): {', '.join(succeeded)}")
        print_warning(
            f"Failed to sync {len(failed)} extension(s): "
            f"{', '.join(ext for ext, _ in failed)}"
        )
        if verbose:
            for ext, msg in failed:
                print_info(f"  {ext}: {msg}")
