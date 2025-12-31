"""Offer ID validation for vince CLI.

This module provides validation functions for offer IDs.
Validates that offer IDs match the required pattern and are not reserved names.
"""

import re

from vince.errors import InvalidOfferIdError

# Pattern for valid offer IDs: starts with lowercase letter,
# followed by up to 31 lowercase alphanumeric, underscore, or hyphen characters
OFFER_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")

# Reserved names that cannot be used as offer IDs
RESERVED_NAMES = {"help", "version", "list", "all", "none", "default"}


def validate_offer_id(offer_id: str) -> str:
    """Validate offer ID format and availability.

    Performs two checks:
    1. Offer ID matches pattern ^[a-z][a-z0-9_-]{0,31}$
    2. Offer ID is not a reserved name

    Args:
        offer_id: Offer ID to validate (e.g., "code-md", "my_app")

    Returns:
        The offer_id if validation passes

    Raises:
        InvalidOfferIdError: If offer_id is invalid or reserved (VE103)
    """
    # Check pattern match
    if not OFFER_ID_PATTERN.match(offer_id):
        raise InvalidOfferIdError(offer_id)

    # Check if reserved
    if offer_id in RESERVED_NAMES:
        raise InvalidOfferIdError(offer_id)

    return offer_id
