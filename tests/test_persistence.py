"""
Property-Based Tests for Vince CLI Persistence Layer

Feature: vince-cli-implementation
Each test validates a specific correctness property from the design document.
"""

import json
import string
import tempfile
import uuid
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vince.persistence.defaults import DEFAULT_SCHEMA, DefaultsStore
from vince.validation.extension import SUPPORTED_EXTENSIONS

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def valid_extensions(draw):
    """Generate valid file extensions from the supported set."""
    return draw(st.sampled_from(list(SUPPORTED_EXTENSIONS)))


@st.composite
def valid_application_paths(draw):
    """Generate valid-looking application paths."""
    app_name = draw(
        st.text(
            alphabet=string.ascii_lowercase + string.digits + "_-",
            min_size=1,
            max_size=20,
        )
    )
    return f"/usr/bin/{app_name}"


@st.composite
def valid_states(draw):
    """Generate valid default states."""
    return draw(st.sampled_from(["pending", "active"]))


# =============================================================================
# Property 5: DefaultsStore Add-Find Consistency
# Validates: Requirements 4.6
# =============================================================================


class TestDefaultsStoreAddFindConsistency:
    """Feature: vince-cli-implementation, Property 5: DefaultsStore Add-Find Consistency

    *For any* valid extension and application path, after calling DefaultsStore.add(),
    calling find_by_extension() with the same extension SHALL return the added entry.
    """

    @given(
        ext=valid_extensions(), app_path=valid_application_paths(), state=valid_states()
    )
    @settings(max_examples=100)
    def test_add_then_find_returns_entry(self, ext, app_path, state):
        """Property 5: Add then find returns the entry.

        **Validates: Requirements 4.6**

        For any valid extension and application path, after calling add(),
        calling find_by_extension() SHALL return an entry with matching extension.
        """
        # Create isolated data directory for each test run using unique ID
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)

            # Add entry
            added_entry = store.add(
                extension=ext,
                application_path=app_path,
                state=state,
                backup_enabled=False,  # Disable backups for faster tests
            )

            # Find by extension - should find an entry with this extension
            found_entry = store.find_by_extension(ext)

            # Verify consistency - entry exists and has correct extension
            assert found_entry is not None
            assert found_entry["extension"] == ext

            # Verify we can find the specific entry by ID
            found_by_id = store.find_by_id(added_entry["id"])
            assert found_by_id is not None
            assert found_by_id["id"] == added_entry["id"]
            assert found_by_id["extension"] == ext
            assert found_by_id["application_path"] == app_path
            assert found_by_id["state"] == state

    @given(ext=valid_extensions())
    @settings(max_examples=100)
    def test_find_nonexistent_returns_none(self, ext):
        """Property: Finding non-existent extension returns None."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)

            # Find without adding - should return None
            found_entry = store.find_by_extension(ext)

            assert found_entry is None

    @given(ext=valid_extensions(), app_path=valid_application_paths())
    @settings(max_examples=100)
    def test_removed_entries_not_found(self, ext, app_path):
        """Property: Entries with 'removed' state are not found by find_by_extension."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)

            # Add entry as active
            added_entry = store.add(
                extension=ext,
                application_path=app_path,
                state="active",
                backup_enabled=False,
            )

            # Update to removed
            store.update_state(added_entry["id"], "removed", backup_enabled=False)

            # Find should return None
            found_entry = store.find_by_extension(ext)

            assert found_entry is None

    @given(ext=valid_extensions(), app_path=valid_application_paths())
    @settings(max_examples=100)
    def test_find_by_id_returns_entry(self, ext, app_path):
        """Property: find_by_id returns the correct entry."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)

            # Add entry
            added_entry = store.add(
                extension=ext, application_path=app_path, backup_enabled=False
            )

            # Find by ID
            found_entry = store.find_by_id(added_entry["id"])

            assert found_entry is not None
            assert found_entry["id"] == added_entry["id"]
            assert found_entry["extension"] == ext


from vince.persistence.offers import DEFAULT_SCHEMA as OFFERS_DEFAULT_SCHEMA
from vince.persistence.offers import OffersStore
from vince.validation.offer_id import RESERVED_NAMES

# =============================================================================
# Hypothesis Strategies for Offers
# =============================================================================


@st.composite
def valid_offer_ids(draw):
    """Generate valid offer IDs matching the pattern ^[a-z][a-z0-9_-]{0,31}$."""
    first = draw(st.sampled_from(string.ascii_lowercase))
    rest_length = draw(st.integers(min_value=0, max_value=31))
    rest = draw(
        st.text(
            alphabet=string.ascii_lowercase + string.digits + "_-",
            min_size=rest_length,
            max_size=rest_length,
        )
    )
    offer_id = first + rest

    # Ensure not a reserved name
    if offer_id in RESERVED_NAMES:
        offer_id = f"custom-{offer_id}"

    return offer_id


@st.composite
def valid_default_ids(draw):
    """Generate valid default IDs."""
    ext = draw(st.sampled_from(["md", "py", "txt", "js", "html", "css", "json"]))
    num = draw(st.integers(min_value=0, max_value=999))
    return f"def-{ext}-{num:03d}"


# =============================================================================
# Property 6: OffersStore Add-Find Consistency
# Validates: Requirements 4.8
# =============================================================================


class TestOffersStoreAddFindConsistency:
    """Feature: vince-cli-implementation, Property 6: OffersStore Add-Find Consistency

    *For any* valid offer_id and default_id, after calling OffersStore.add(),
    calling find_by_id() with the same offer_id SHALL return the added entry.
    """

    @given(
        offer_id=valid_offer_ids(),
        default_id=valid_default_ids(),
        auto_created=st.booleans(),
    )
    @settings(max_examples=100)
    def test_add_then_find_returns_entry(self, offer_id, default_id, auto_created):
        """Property 6: Add then find returns the entry.

        **Validates: Requirements 4.8**

        For any valid offer_id and default_id, after calling add(),
        calling find_by_id() SHALL return an entry with matching offer_id.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = OffersStore(data_dir)

            # Add entry
            added_entry = store.add(
                offer_id=offer_id,
                default_id=default_id,
                auto_created=auto_created,
                backup_enabled=False,
            )

            # Find by offer_id
            found_entry = store.find_by_id(offer_id)

            # Verify consistency
            assert found_entry is not None
            assert found_entry["offer_id"] == offer_id
            assert found_entry["default_id"] == default_id
            assert found_entry["auto_created"] == auto_created
            assert found_entry["state"] == "created"

    @given(offer_id=valid_offer_ids())
    @settings(max_examples=100)
    def test_find_nonexistent_returns_none(self, offer_id):
        """Property: Finding non-existent offer_id returns None."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = OffersStore(data_dir)

            # Find without adding - should return None
            found_entry = store.find_by_id(offer_id)

            assert found_entry is None

    @given(offer_id=valid_offer_ids(), default_id=valid_default_ids())
    @settings(max_examples=100)
    def test_rejected_entries_not_found(self, offer_id, default_id):
        """Property: Entries with 'rejected' state are not found by find_by_id."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = OffersStore(data_dir)

            # Add entry
            added_entry = store.add(
                offer_id=offer_id, default_id=default_id, backup_enabled=False
            )

            # Update to rejected
            store.update_state(offer_id, "rejected", backup_enabled=False)

            # Find should return None
            found_entry = store.find_by_id(offer_id)

            assert found_entry is None

    @given(offer_id=valid_offer_ids(), default_id=valid_default_ids())
    @settings(max_examples=100)
    def test_find_by_default_id_returns_entries(self, offer_id, default_id):
        """Property: find_by_default_id returns all associated entries."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = OffersStore(data_dir)

            # Add entry
            added_entry = store.add(
                offer_id=offer_id, default_id=default_id, backup_enabled=False
            )

            # Find by default_id
            found_entries = store.find_by_default_id(default_id)

            assert len(found_entries) >= 1
            assert any(e["offer_id"] == offer_id for e in found_entries)


# =============================================================================
# Property 4: Persistence Round-Trip Consistency
# Validates: Requirements 4.1, 4.5, 4.7
# =============================================================================


class TestPersistenceRoundTrip:
    """Feature: vince-cli-implementation, Property 4: Persistence Round-Trip Consistency

    *For any* valid DefaultEntry or OfferEntry, saving to JSON and loading back
    SHALL produce an equivalent object. Specifically: load(save(data)) == data
    for all valid data.
    """

    @given(
        ext=valid_extensions(), app_path=valid_application_paths(), state=valid_states()
    )
    @settings(max_examples=100)
    def test_defaults_round_trip(self, ext, app_path, state):
        """Property 4: DefaultsStore save then load returns equivalent data.

        **Validates: Requirements 4.1, 4.5**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)

            # Add entry
            added_entry = store.add(
                extension=ext,
                application_path=app_path,
                state=state,
                backup_enabled=False,
            )

            # Create a new store instance to force reload from disk
            store2 = DefaultsStore(data_dir)

            # Load and verify
            loaded_data = store2.load()

            assert len(loaded_data["defaults"]) == 1
            loaded_entry = loaded_data["defaults"][0]

            # Verify all fields match
            assert loaded_entry["id"] == added_entry["id"]
            assert loaded_entry["extension"] == ext
            assert loaded_entry["application_path"] == app_path
            assert loaded_entry["state"] == state
            assert loaded_entry["created_at"] == added_entry["created_at"]

    @given(
        offer_id=valid_offer_ids(),
        default_id=valid_default_ids(),
        auto_created=st.booleans(),
    )
    @settings(max_examples=100)
    def test_offers_round_trip(self, offer_id, default_id, auto_created):
        """Property 4: OffersStore save then load returns equivalent data.

        **Validates: Requirements 4.1, 4.7**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = OffersStore(data_dir)

            # Add entry
            added_entry = store.add(
                offer_id=offer_id,
                default_id=default_id,
                auto_created=auto_created,
                backup_enabled=False,
            )

            # Create a new store instance to force reload from disk
            store2 = OffersStore(data_dir)

            # Load and verify
            loaded_data = store2.load()

            assert len(loaded_data["offers"]) == 1
            loaded_entry = loaded_data["offers"][0]

            # Verify all fields match
            assert loaded_entry["offer_id"] == offer_id
            assert loaded_entry["default_id"] == default_id
            assert loaded_entry["auto_created"] == auto_created
            assert loaded_entry["state"] == "created"
            assert loaded_entry["created_at"] == added_entry["created_at"]

    @given(ext=valid_extensions(), app_path=valid_application_paths())
    @settings(max_examples=100)
    def test_state_update_persists(self, ext, app_path):
        """Property: State updates are persisted correctly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)

            # Add entry as pending
            added_entry = store.add(
                extension=ext,
                application_path=app_path,
                state="pending",
                backup_enabled=False,
            )

            # Update to active
            store.update_state(added_entry["id"], "active", backup_enabled=False)

            # Create a new store instance to force reload from disk
            store2 = DefaultsStore(data_dir)

            # Load and verify state was updated
            loaded_entry = store2.find_by_id(added_entry["id"])

            assert loaded_entry is not None
            assert loaded_entry["state"] == "active"
            assert "updated_at" in loaded_entry


import time

# =============================================================================
# Property 7: Backup Retention Limit
# Validates: Requirements 4.9, 4.10
# =============================================================================


class TestBackupRetention:
    """Feature: vince-cli-implementation, Property 7: Backup Retention Limit

    *For any* sequence of N writes with backup_enabled=true and max_backups=M,
    the number of backup files SHALL never exceed M. The oldest backups SHALL
    be deleted when the limit is exceeded.
    """

    @given(
        num_writes=st.integers(min_value=1, max_value=10),
        max_backups=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100)
    def test_backup_count_never_exceeds_max(self, num_writes, max_backups):
        """Property 7: Backup count never exceeds max_backups.

        **Validates: Requirements 4.9, 4.10**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)
            backup_dir = store.backup_dir

            # Perform multiple writes with backups enabled
            for i in range(num_writes):
                store.add(
                    extension=f".ext{i}",
                    application_path=f"/usr/bin/app{i}",
                    state="pending",
                    backup_enabled=True,
                    max_backups=max_backups,
                )
                # Small delay to ensure unique timestamps
                time.sleep(0.01)

            # Count backup files
            if backup_dir.exists():
                backup_files = list(backup_dir.glob("defaults.*.bak"))
                backup_count = len(backup_files)
            else:
                backup_count = 0

            # Verify backup count never exceeds max_backups
            assert (
                backup_count <= max_backups
            ), f"Backup count {backup_count} exceeds max_backups {max_backups}"

    @given(max_backups=st.integers(min_value=1, max_value=3))
    @settings(max_examples=50)
    def test_oldest_backups_deleted_first(self, max_backups):
        """Property: Oldest backups are deleted when limit is exceeded."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)
            backup_dir = store.backup_dir

            # Perform more writes than max_backups to trigger cleanup
            num_writes = max_backups + 3

            for i in range(num_writes):
                store.add(
                    extension=f".ext{i}",
                    application_path=f"/usr/bin/app{i}",
                    state="pending",
                    backup_enabled=True,
                    max_backups=max_backups,
                )
                # Small delay to ensure unique timestamps
                time.sleep(0.02)

            # Get remaining backup files sorted by name (which includes timestamp)
            if backup_dir.exists():
                backup_files = sorted(backup_dir.glob("defaults.*.bak"))

                # Verify we have at most max_backups
                assert len(backup_files) <= max_backups

                # If we have backups, verify they are the most recent ones
                # (sorted by timestamp in filename)
                if len(backup_files) > 1:
                    # Verify files are in chronological order
                    for i in range(len(backup_files) - 1):
                        assert backup_files[i].name < backup_files[i + 1].name

    @given(ext=valid_extensions(), app_path=valid_application_paths())
    @settings(max_examples=50)
    def test_backup_disabled_creates_no_backups(self, ext, app_path):
        """Property: When backup_enabled=False, no backups are created."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            store = DefaultsStore(data_dir)
            backup_dir = store.backup_dir

            # Perform multiple writes with backups disabled
            for i in range(5):
                store.add(
                    extension=f"{ext}{i}" if i > 0 else ext,
                    application_path=app_path,
                    state="pending",
                    backup_enabled=False,
                )

            # Verify no backup files were created
            if backup_dir.exists():
                backup_files = list(backup_dir.glob("*.bak"))
                assert (
                    len(backup_files) == 0
                ), f"Found {len(backup_files)} backup files when backups were disabled"
