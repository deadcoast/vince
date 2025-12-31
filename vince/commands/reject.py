"""Reject command for vince CLI.

The reject command removes a custom offer/alias. It transitions the offer
state to 'rejected', effectively removing it from active use.
"""

from typer import Argument, Option

from vince.config import get_config, get_data_dir
from vince.errors import OfferNotFoundError, VinceError, handle_error
from vince.output.messages import print_info, print_success, print_warning
from vince.persistence.offers import OffersStore
from vince.state.offer_state import OfferState, validate_transition


def cmd_reject(
    offer_id: str = Argument(
        ...,
        help="The offer ID to reject",
    ),
    complete_delete: bool = Option(
        False,
        "-.",
        help="Complete delete - remove offer entirely from data file",
    ),
    verbose: bool = Option(
        False,
        "-vb",
        "--verbose",
        help="Enable verbose output",
    ),
) -> None:
    """Remove a custom offer/alias.

    Transitions the offer state to 'rejected'. Use the '.' flag for
    complete deletion from the data file.
    """
    try:
        # Load configuration
        config = get_config()
        verbose = verbose or config.get("verbose", False)
        backup_enabled = config.get("backup_enabled", True)
        max_backups = config.get("max_backups", 5)

        if verbose:
            print_info(f"Rejecting offer: [offer]{offer_id}[/]")

        # Get data directory and store
        data_dir = get_data_dir(config)
        offers_store = OffersStore(data_dir)

        # Find the offer
        existing_offer = offers_store.find_by_id(offer_id)

        if existing_offer is None:
            raise OfferNotFoundError(offer_id)

        if verbose:
            print_info(f"Found offer with state: [state]{existing_offer['state']}[/]")

        # Get current state
        current_state = OfferState(existing_offer["state"])
        target_state = OfferState.REJECTED

        # Validate the transition
        validate_transition(current_state, target_state, offer_id)

        # Warn when rejecting an active offer
        if current_state == OfferState.ACTIVE:
            print_warning(
                f"Offer [offer]{offer_id}[/] has been used. "
                "Consider if dependent workflows need updating."
            )

        if complete_delete:
            # Warn about permanent removal
            print_warning(
                f"Complete delete will permanently remove [offer]{offer_id}[/] "
                "from the data file."
            )
            # Complete delete - remove from data file entirely
            _delete_offer(offers_store, offer_id, backup_enabled, max_backups)
            print_success(f"Offer deleted: [offer]{offer_id}[/]")
            if verbose:
                print_info("Offer completely removed from data file")
        else:
            # Normal reject - transition to rejected state
            offers_store.update_state(
                offer_id=offer_id,
                new_state=target_state.value,
                backup_enabled=backup_enabled,
                max_backups=max_backups,
            )
            print_success(f"Offer rejected: [offer]{offer_id}[/]")
            if verbose:
                print_info(
                    f"State changed: [state]{current_state.value}[/] → [state]{target_state.value}[/]"
                )

    except VinceError as e:
        handle_error(e)
    except Exception as e:
        from vince.errors import UnexpectedError

        handle_error(UnexpectedError(str(e)))


def _delete_offer(
    offers_store: OffersStore, offer_id: str, backup_enabled: bool, max_backups: int
) -> None:
    """Delete an offer entry completely from the data file.

    Args:
        offers_store: The OffersStore instance
        offer_id: The offer ID to delete
        backup_enabled: Whether to create backup before write
        max_backups: Maximum number of backups to retain
    """
    data = offers_store.load()
    data["offers"] = [
        offer for offer in data["offers"] if offer["offer_id"] != offer_id
    ]
    offers_store.save(data, backup_enabled, max_backups)
