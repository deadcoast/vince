"""
Property-Based Tests for Vince CLI Configuration System

Feature: vince-cli-implementation
Each test validates a specific correctness property from the design document.
"""

import json
import tempfile
import uuid
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vince.config import (DEFAULT_CONFIG, VALID_COLOR_THEMES,
                          VALID_CONFIG_KEYS, get_config, load_config_file,
                          merge_configs, validate_config,
                          validate_config_option)
from vince.errors import ConfigMalformedError, InvalidConfigOptionError

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def valid_versions(draw):
    """Generate valid semver version strings."""
    major = draw(st.integers(min_value=0, max_value=99))
    minor = draw(st.integers(min_value=0, max_value=99))
    patch = draw(st.integers(min_value=0, max_value=99))
    return f"{major}.{minor}.{patch}"


@st.composite
def valid_color_themes(draw):
    """Generate valid color theme values."""
    return draw(st.sampled_from(list(VALID_COLOR_THEMES)))


@st.composite
def valid_max_backups(draw):
    """Generate valid max_backups values (0-100)."""
    return draw(st.integers(min_value=0, max_value=100))


@st.composite
def valid_config_dicts(draw):
    """Generate valid configuration dictionaries."""
    config = {"version": draw(valid_versions())}

    # Optionally add other fields
    if draw(st.booleans()):
        config["data_dir"] = draw(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip())
        )
    if draw(st.booleans()):
        config["verbose"] = draw(st.booleans())
    if draw(st.booleans()):
        config["color_theme"] = draw(valid_color_themes())
    if draw(st.booleans()):
        config["backup_enabled"] = draw(st.booleans())
    if draw(st.booleans()):
        config["max_backups"] = draw(valid_max_backups())
    if draw(st.booleans()):
        config["confirm_destructive"] = draw(st.booleans())

    return config


# =============================================================================
# Property 10: Config Precedence Correctness
# Validates: Requirements 6.2, 6.3, 6.4
# =============================================================================


class TestConfigPrecedence:
    """Feature: vince-cli-implementation, Property 10: Config Precedence Correctness

    *For any* configuration key that exists at multiple levels (default, user, project),
    the value from the highest precedence level SHALL be used.
    Precedence order: project > user > default.
    """

    @given(user_verbose=st.booleans(), project_verbose=st.booleans())
    @settings(max_examples=100)
    def test_project_overrides_user(self, user_verbose, project_verbose):
        """Property 10: Project config overrides user config.

        **Validates: Requirements 6.2, 6.3, 6.4**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            base_dir = Path(tmp_dir) / unique_id

            # Create user config
            user_dir = base_dir / "user" / ".vince"
            user_dir.mkdir(parents=True)
            user_config_path = user_dir / "config.json"
            user_config = {"version": "1.0.0", "verbose": user_verbose}
            user_config_path.write_text(json.dumps(user_config))

            # Create project config
            project_dir = base_dir / "project" / ".vince"
            project_dir.mkdir(parents=True)
            project_config_path = project_dir / "config.json"
            project_config = {"version": "1.0.0", "verbose": project_verbose}
            project_config_path.write_text(json.dumps(project_config))

            # Load merged config
            merged = get_config(
                user_config_path=user_config_path,
                project_config_path=project_config_path,
            )

            # Project should override user
            assert merged["verbose"] == project_verbose

    @given(user_verbose=st.booleans())
    @settings(max_examples=100)
    def test_user_overrides_default(self, user_verbose):
        """Property 10: User config overrides default config.

        **Validates: Requirements 6.2, 6.3**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            base_dir = Path(tmp_dir) / unique_id

            # Create user config
            user_dir = base_dir / "user" / ".vince"
            user_dir.mkdir(parents=True)
            user_config_path = user_dir / "config.json"
            user_config = {"version": "1.0.0", "verbose": user_verbose}
            user_config_path.write_text(json.dumps(user_config))

            # No project config
            project_config_path = base_dir / "nonexistent" / "config.json"

            # Load merged config
            merged = get_config(
                user_config_path=user_config_path,
                project_config_path=project_config_path,
            )

            # User should override default
            assert merged["verbose"] == user_verbose

    @given(user_theme=valid_color_themes(), project_max_backups=valid_max_backups())
    @settings(max_examples=100)
    def test_partial_overrides_preserve_other_values(
        self, user_theme, project_max_backups
    ):
        """Property 10: Partial configs preserve values from lower precedence levels.

        **Validates: Requirements 6.2, 6.3, 6.4**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            base_dir = Path(tmp_dir) / unique_id

            # User config sets color_theme
            user_dir = base_dir / "user" / ".vince"
            user_dir.mkdir(parents=True)
            user_config_path = user_dir / "config.json"
            user_config = {"version": "1.0.0", "color_theme": user_theme}
            user_config_path.write_text(json.dumps(user_config))

            # Project config sets max_backups
            project_dir = base_dir / "project" / ".vince"
            project_dir.mkdir(parents=True)
            project_config_path = project_dir / "config.json"
            project_config = {"version": "1.0.0", "max_backups": project_max_backups}
            project_config_path.write_text(json.dumps(project_config))

            # Load merged config
            merged = get_config(
                user_config_path=user_config_path,
                project_config_path=project_config_path,
            )

            # User's color_theme should be preserved
            assert merged["color_theme"] == user_theme
            # Project's max_backups should be used
            assert merged["max_backups"] == project_max_backups
            # Default values should be used for unset options
            assert merged["backup_enabled"] == DEFAULT_CONFIG["backup_enabled"]
            assert (
                merged["confirm_destructive"] == DEFAULT_CONFIG["confirm_destructive"]
            )

    @settings(max_examples=100)
    @given(st.data())
    def test_missing_configs_use_defaults(self, data):
        """Property 10: Missing config files fall back to defaults.

        **Validates: Requirements 6.2**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            base_dir = Path(tmp_dir) / unique_id

            # Non-existent paths
            user_config_path = base_dir / "nonexistent_user" / "config.json"
            project_config_path = base_dir / "nonexistent_project" / "config.json"

            # Load merged config
            merged = get_config(
                user_config_path=user_config_path,
                project_config_path=project_config_path,
            )

            # All values should be defaults
            for key, default_value in DEFAULT_CONFIG.items():
                assert (
                    merged[key] == default_value
                ), f"Key {key} should be default value"

    @given(
        default_id=valid_versions(),
        user_id=valid_versions(),
        project_id=valid_versions(),
    )
    @settings(max_examples=100)
    def test_full_precedence_chain(self, default_id, user_id, project_id):
        """Property 10: Full precedence chain works correctly.

        **Validates: Requirements 6.2, 6.3, 6.4**
        """
        # Test merge_configs directly with all three levels
        default = {"version": default_id, "verbose": False}
        user = {"version": user_id, "color_theme": "dark"}
        project = {"version": project_id, "max_backups": 10}

        merged = merge_configs(default, user, project)

        # Project version wins (highest priority)
        assert merged["version"] == project_id
        # User color_theme is preserved (not in project)
        assert merged["color_theme"] == "dark"
        # Project max_backups is used
        assert merged["max_backups"] == 10
        # Default verbose is preserved (not in user or project)
        assert merged["verbose"] is False


# =============================================================================
# Property 11: Config Error Handling
# Validates: Requirements 6.5, 6.6
# =============================================================================


class TestConfigErrorHandling:
    """Feature: vince-cli-implementation, Property 11: Config Error Handling

    *For any* malformed JSON config file, loading SHALL raise ConfigMalformedError (VE402).
    *For any* invalid config option value, loading SHALL raise InvalidConfigOptionError (VE401).
    """

    @given(
        st.text(min_size=1, max_size=100).filter(
            lambda x: x.strip() and not x.strip().startswith("{")
        )
    )
    @settings(max_examples=100)
    def test_malformed_json_raises_ve402(self, invalid_json):
        """Property 11: Malformed JSON raises ConfigMalformedError (VE402).

        **Validates: Requirements 6.5**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            config_path = Path(tmp_dir) / unique_id / "config.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(invalid_json)

            with pytest.raises(ConfigMalformedError) as exc_info:
                load_config_file(config_path)

            assert exc_info.value.code == "VE402"

    @given(
        st.sampled_from(
            [
                '{"version": "1.0.0",}',  # Trailing comma
                '{"version": "1.0.0"',  # Missing closing brace
                "{'version': '1.0.0'}",  # Single quotes
                '{"version": 1.0.0}',  # Unquoted value
            ]
        )
    )
    @settings(max_examples=100)
    def test_json_syntax_errors_raise_ve402(self, malformed_json):
        """Property 11: JSON syntax errors raise ConfigMalformedError (VE402).

        **Validates: Requirements 6.5**
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            unique_id = str(uuid.uuid4())
            config_path = Path(tmp_dir) / unique_id / "config.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(malformed_json)

            with pytest.raises(ConfigMalformedError) as exc_info:
                load_config_file(config_path)

            assert exc_info.value.code == "VE402"

    @given(
        st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x not in VALID_CONFIG_KEYS and x.isidentifier()
        )
    )
    @settings(max_examples=100)
    def test_unknown_config_key_raises_ve401(self, unknown_key):
        """Property 11: Unknown config keys raise InvalidConfigOptionError (VE401).

        **Validates: Requirements 6.6**
        """
        with pytest.raises(InvalidConfigOptionError) as exc_info:
            validate_config_option(unknown_key, "some_value")

        assert exc_info.value.code == "VE401"

    @given(
        st.sampled_from(
            [
                ("verbose", "yes"),  # String instead of bool
                ("verbose", 1),  # Int instead of bool
                ("verbose", [True]),  # List instead of bool
                ("backup_enabled", "true"),  # String instead of bool
                ("backup_enabled", 0),  # Int instead of bool
                ("confirm_destructive", "false"),  # String instead of bool
            ]
        )
    )
    @settings(max_examples=100)
    def test_invalid_boolean_type_raises_ve401(self, key_value):
        """Property 11: Invalid boolean types raise InvalidConfigOptionError (VE401).

        **Validates: Requirements 6.6**
        """
        key, value = key_value
        with pytest.raises(InvalidConfigOptionError) as exc_info:
            validate_config_option(key, value)

        assert exc_info.value.code == "VE401"

    @given(
        st.sampled_from(
            [
                ("color_theme", "blue"),  # Invalid enum value
                ("color_theme", "DARK"),  # Case-sensitive
                ("color_theme", "Default"),  # Case-sensitive
                ("color_theme", 123),  # Wrong type
            ]
        )
    )
    @settings(max_examples=100)
    def test_invalid_enum_value_raises_ve401(self, key_value):
        """Property 11: Invalid enum values raise InvalidConfigOptionError (VE401).

        **Validates: Requirements 6.6**
        """
        key, value = key_value
        with pytest.raises(InvalidConfigOptionError) as exc_info:
            validate_config_option(key, value)

        assert exc_info.value.code == "VE401"

    @given(
        st.sampled_from(
            [
                -1,  # Below minimum
                -100,  # Way below minimum
                101,  # Above maximum
                500,  # Way above maximum
            ]
        )
    )
    @settings(max_examples=100)
    def test_max_backups_out_of_range_raises_ve401(self, invalid_value):
        """Property 11: max_backups out of range raises InvalidConfigOptionError (VE401).

        **Validates: Requirements 6.6**
        """
        with pytest.raises(InvalidConfigOptionError) as exc_info:
            validate_config_option("max_backups", invalid_value)

        assert exc_info.value.code == "VE401"

    @given(
        st.sampled_from(
            [
                "5",  # String instead of int
                5.0,  # Float instead of int
                True,  # Bool instead of int (bool is subclass of int in Python)
                [5],  # List instead of int
            ]
        )
    )
    @settings(max_examples=100)
    def test_max_backups_invalid_type_raises_ve401(self, invalid_value):
        """Property 11: max_backups with invalid type raises InvalidConfigOptionError (VE401).

        **Validates: Requirements 6.6**
        """
        with pytest.raises(InvalidConfigOptionError) as exc_info:
            validate_config_option("max_backups", invalid_value)

        assert exc_info.value.code == "VE401"

    @given(
        st.sampled_from(
            [
                "1.0",  # Missing patch
                "1",  # Only major
                "v1.0.0",  # Prefix
                "1.0.0-beta",  # Suffix
                "1.0.0.0",  # Extra segment
                123,  # Not a string
            ]
        )
    )
    @settings(max_examples=100)
    def test_invalid_version_format_raises_ve401(self, invalid_version):
        """Property 11: Invalid version format raises InvalidConfigOptionError (VE401).

        **Validates: Requirements 6.6**
        """
        with pytest.raises(InvalidConfigOptionError) as exc_info:
            validate_config_option("version", invalid_version)

        assert exc_info.value.code == "VE401"

    @given(valid_config_dicts())
    @settings(max_examples=100)
    def test_valid_configs_do_not_raise(self, config):
        """Property 11: Valid configurations do not raise errors.

        **Validates: Requirements 6.5, 6.6**
        """
        # Should not raise any exception
        validate_config(config)

    @given(
        valid_config=valid_config_dicts(),
        invalid_key=st.text(min_size=1, max_size=10).filter(
            lambda x: x.strip() and x not in VALID_CONFIG_KEYS and x.isidentifier()
        ),
    )
    @settings(max_examples=100)
    def test_config_with_unknown_key_raises_ve401(self, valid_config, invalid_key):
        """Property 11: Config with unknown key raises InvalidConfigOptionError (VE401).

        **Validates: Requirements 6.6**
        """
        # Add an unknown key to an otherwise valid config
        config_with_unknown = valid_config.copy()
        config_with_unknown[invalid_key] = "some_value"

        with pytest.raises(InvalidConfigOptionError) as exc_info:
            validate_config(config_with_unknown)

        assert exc_info.value.code == "VE401"
