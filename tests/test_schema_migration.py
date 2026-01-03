"""
Tests for Schema Migration in Vince CLI Persistence Layer

Feature: coverage-completion
Tests validate schema migration correctness from v1.0.0 to v1.1.0.
"""

import json
import string
import tempfile
import uuid
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vince.persistence.defaults import (
    CURRENT_SCHEMA_VERSION,
    DEFAULT_SCHEMA,
    DefaultsStore,
    migrate_schema,
)
from vince.validation.extension import SUPPORTED_EXTENSIONS


# =============================================================================
# Unit Tests for Schema Migration (Task 11.1)
# =============================================================================


class TestSchemaMigrationUnit:
    """Unit tests for schema migration from v1.0.0 to v1.1.0.

    Requirements: 8.4
    """

    def test_v1_0_0_to_v1_1_0_adds_os_synced_field(self):
        """Test v1.0.0 to v1.1.0 migration adds os_synced field.

        Requirements: 8.4
        """
        # Create v1.0.0 data without os_synced field
        v1_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/vim",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                },
                {
                    "id": "def-py-001",
                    "extension": ".py",
                    "application_path": "/usr/bin/code",
                    "state": "pending",
                    "created_at": "2024-01-02T00:00:00+00:00",
                },
            ],
        }

        # Migrate
        migrated = migrate_schema(v1_data)

        # Verify os_synced field was added to all entries
        for entry in migrated["defaults"]:
            assert "os_synced" in entry
            assert entry["os_synced"] is False

    def test_v1_0_0_to_v1_1_0_updates_version(self):
        """Test v1.0.0 to v1.1.0 migration updates version.

        Requirements: 8.4
        """
        v1_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/vim",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }

        # Migrate
        migrated = migrate_schema(v1_data)

        # Verify version was updated
        assert migrated["version"] == "1.1.0"

    def test_v1_1_0_files_skip_migration(self):
        """Test v1.1.0 files skip migration.

        Requirements: 8.4
        """
        v1_1_data = {
            "version": "1.1.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/vim",
                    "state": "active",
                    "os_synced": True,
                    "os_synced_at": "2024-01-01T12:00:00+00:00",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }

        # Migrate (should be no-op)
        migrated = migrate_schema(v1_1_data)

        # Verify data is unchanged
        assert migrated["version"] == "1.1.0"
        assert migrated["defaults"][0]["os_synced"] is True
        assert migrated["defaults"][0]["os_synced_at"] == "2024-01-01T12:00:00+00:00"

    def test_migration_preserves_existing_fields(self):
        """Test migration preserves all existing fields.

        Requirements: 8.4
        """
        v1_data = {
            "version": "1.0.0",
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/vim",
                    "application_name": "Vim",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                    "updated_at": "2024-01-02T00:00:00+00:00",
                }
            ],
        }

        # Migrate
        migrated = migrate_schema(v1_data)

        # Verify all original fields are preserved
        entry = migrated["defaults"][0]
        assert entry["id"] == "def-md-000"
        assert entry["extension"] == ".md"
        assert entry["application_path"] == "/usr/bin/vim"
        assert entry["application_name"] == "Vim"
        assert entry["state"] == "active"
        assert entry["created_at"] == "2024-01-01T00:00:00+00:00"
        assert entry["updated_at"] == "2024-01-02T00:00:00+00:00"

    def test_migration_handles_empty_defaults(self):
        """Test migration handles empty defaults array.

        Requirements: 8.4
        """
        v1_data = {"version": "1.0.0", "defaults": []}

        # Migrate
        migrated = migrate_schema(v1_data)

        # Verify version updated and defaults still empty
        assert migrated["version"] == "1.1.0"
        assert migrated["defaults"] == []

    def test_migration_handles_missing_version(self):
        """Test migration handles missing version field (defaults to 1.0.0).

        Requirements: 8.4
        """
        data_no_version = {
            "defaults": [
                {
                    "id": "def-md-000",
                    "extension": ".md",
                    "application_path": "/usr/bin/vim",
                    "state": "active",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ]
        }

        # Migrate
        migrated = migrate_schema(data_no_version)

        # Verify version was set and os_synced added
        assert migrated["version"] == "1.1.0"
        assert migrated["defaults"][0]["os_synced"] is False


class TestDefaultsStoreAutoMigration:
    """Test DefaultsStore automatic migration on load.

    Requirements: 8.4
    """

    def test_load_migrates_v1_0_0_file(self):
        """Test loading v1.0.0 file triggers automatic migration.

        Requirements: 8.4
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / ".vince"
            data_dir.mkdir(exist_ok=True)

            # Write v1.0.0 file directly
            v1_data = {
                "version": "1.0.0",
                "defaults": [
                    {
                        "id": "def-md-000",
                        "extension": ".md",
                        "application_path": "/usr/bin/vim",
                        "state": "active",
                        "created_at": "2024-01-01T00:00:00+00:00",
                    }
                ],
            }
            defaults_path = data_dir / "defaults.json"
            defaults_path.write_text(json.dumps(v1_data))

            # Load through DefaultsStore
            store = DefaultsStore(data_dir)
            loaded = store.load()

            # Verify migration occurred
            assert loaded["version"] == "1.1.0"
            assert loaded["defaults"][0]["os_synced"] is False

    def test_load_saves_migrated_data(self):
        """Test loading v1.0.0 file saves migrated data to disk.

        Requirements: 8.4
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / ".vince"
            data_dir.mkdir(exist_ok=True)

            # Write v1.0.0 file directly
            v1_data = {
                "version": "1.0.0",
                "defaults": [
                    {
                        "id": "def-md-000",
                        "extension": ".md",
                        "application_path": "/usr/bin/vim",
                        "state": "active",
                        "created_at": "2024-01-01T00:00:00+00:00",
                    }
                ],
            }
            defaults_path = data_dir / "defaults.json"
            defaults_path.write_text(json.dumps(v1_data))

            # Load through DefaultsStore (triggers migration)
            store = DefaultsStore(data_dir)
            store.load()

            # Read file directly to verify it was updated
            saved_data = json.loads(defaults_path.read_text())
            assert saved_data["version"] == "1.1.0"
            assert saved_data["defaults"][0]["os_synced"] is False

    def test_load_v1_1_0_does_not_rewrite(self):
        """Test loading v1.1.0 file does not trigger unnecessary write.

        Requirements: 8.4
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / ".vince"
            data_dir.mkdir(exist_ok=True)

            # Write v1.1.0 file directly
            v1_1_data = {
                "version": "1.1.0",
                "defaults": [
                    {
                        "id": "def-md-000",
                        "extension": ".md",
                        "application_path": "/usr/bin/vim",
                        "state": "active",
                        "os_synced": True,
                        "created_at": "2024-01-01T00:00:00+00:00",
                    }
                ],
            }
            defaults_path = data_dir / "defaults.json"
            defaults_path.write_text(json.dumps(v1_1_data))

            # Get modification time before load
            mtime_before = defaults_path.stat().st_mtime

            # Load through DefaultsStore
            store = DefaultsStore(data_dir)
            loaded = store.load()

            # Get modification time after load
            mtime_after = defaults_path.stat().st_mtime

            # Verify file was not modified
            assert mtime_before == mtime_after
            assert loaded["version"] == "1.1.0"


# =============================================================================
# Property-Based Tests for Schema Migration (Task 11.2)
# =============================================================================


@st.composite
def valid_extensions_strategy(draw):
    """Generate valid file extensions from the supported set."""
    return draw(st.sampled_from(list(SUPPORTED_EXTENSIONS)))


@st.composite
def valid_application_paths_strategy(draw):
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
def valid_states_strategy(draw):
    """Generate valid default states."""
    return draw(st.sampled_from(["pending", "active", "removed"]))


@st.composite
def v1_0_0_entry_strategy(draw):
    """Generate a valid v1.0.0 default entry (without os_synced)."""
    ext = draw(valid_extensions_strategy())
    idx = draw(st.integers(min_value=0, max_value=999))
    return {
        "id": f"def-{ext[1:]}-{idx:03d}",
        "extension": ext,
        "application_path": draw(valid_application_paths_strategy()),
        "state": draw(valid_states_strategy()),
        "created_at": "2024-01-01T00:00:00+00:00",
    }


@st.composite
def v1_0_0_data_strategy(draw):
    """Generate valid v1.0.0 defaults.json data."""
    num_entries = draw(st.integers(min_value=0, max_value=10))
    entries = [draw(v1_0_0_entry_strategy()) for _ in range(num_entries)]
    return {"version": "1.0.0", "defaults": entries}


class TestSchemaMigrationProperty:
    """Feature: coverage-completion, Property 5: Schema Migration Correctness

    *For any* valid v1.0.0 defaults.json file, loading it through DefaultsStore
    SHALL produce a valid v1.1.0 structure with os_synced=False for all existing
    entries and the version field updated to "1.1.0".

    **Validates: Requirements 8.4**
    """

    @given(v1_data=v1_0_0_data_strategy())
    @settings(max_examples=100)
    def test_migration_produces_v1_1_0_structure(self, v1_data):
        """Property 5: Schema Migration Correctness.

        **Validates: Requirements 8.4**

        For any valid v1.0.0 defaults.json file, migration SHALL produce
        a valid v1.1.0 structure.
        """
        # Migrate
        migrated = migrate_schema(v1_data.copy())

        # Verify version is updated to 1.1.0
        assert migrated["version"] == "1.1.0"

        # Verify all entries have os_synced=False
        for entry in migrated["defaults"]:
            assert "os_synced" in entry
            assert entry["os_synced"] is False

    @given(v1_data=v1_0_0_data_strategy())
    @settings(max_examples=100)
    def test_migration_preserves_entry_count(self, v1_data):
        """Property: Migration preserves the number of entries.

        **Validates: Requirements 8.4**
        """
        original_count = len(v1_data["defaults"])

        # Migrate
        migrated = migrate_schema(v1_data.copy())

        # Verify entry count is preserved
        assert len(migrated["defaults"]) == original_count

    @given(v1_data=v1_0_0_data_strategy())
    @settings(max_examples=100)
    def test_migration_preserves_original_fields(self, v1_data):
        """Property: Migration preserves all original entry fields.

        **Validates: Requirements 8.4**
        """
        # Make a deep copy for comparison
        import copy

        original_entries = copy.deepcopy(v1_data["defaults"])

        # Migrate
        migrated = migrate_schema(v1_data.copy())

        # Verify all original fields are preserved
        for i, entry in enumerate(migrated["defaults"]):
            original = original_entries[i]
            assert entry["id"] == original["id"]
            assert entry["extension"] == original["extension"]
            assert entry["application_path"] == original["application_path"]
            assert entry["state"] == original["state"]
            assert entry["created_at"] == original["created_at"]

    @given(v1_data=v1_0_0_data_strategy())
    @settings(max_examples=100)
    def test_migration_idempotence(self, v1_data):
        """Property: Migrating already-migrated data is idempotent.

        **Validates: Requirements 8.4**
        """
        # First migration
        migrated_once = migrate_schema(v1_data.copy())

        # Second migration (should be no-op)
        migrated_twice = migrate_schema(migrated_once.copy())

        # Verify data is identical
        assert migrated_once["version"] == migrated_twice["version"]
        assert len(migrated_once["defaults"]) == len(migrated_twice["defaults"])

        for i, entry in enumerate(migrated_twice["defaults"]):
            original = migrated_once["defaults"][i]
            assert entry == original

    @given(v1_data=v1_0_0_data_strategy())
    @settings(max_examples=100)
    def test_store_load_produces_v1_1_0(self, v1_data):
        """Property: Loading v1.0.0 through DefaultsStore produces v1.1.0.

        **Validates: Requirements 8.4**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            data_dir = Path(tmp_dir) / f".vince_{unique_id}"
            data_dir.mkdir(exist_ok=True)

            # Write v1.0.0 file directly
            defaults_path = data_dir / "defaults.json"
            defaults_path.write_text(json.dumps(v1_data))

            # Load through DefaultsStore
            store = DefaultsStore(data_dir)
            loaded = store.load()

            # Verify migration occurred
            assert loaded["version"] == "1.1.0"

            # Verify all entries have os_synced=False
            for entry in loaded["defaults"]:
                assert "os_synced" in entry
                assert entry["os_synced"] is False
