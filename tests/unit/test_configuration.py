"""Unit tests for configuration management."""

import json
import os
from unittest.mock import patch

import pytest

from teleprompter.core.configuration import (
    ConfigurationManager,
    EnvironmentConfig,
    get_config,
    setup_config,
)
from teleprompter.core.exceptions import (
    InvalidConfigurationError,
    MissingConfigurationError,
)


class TestConfigurationManager:
    """Test the ConfigurationManager class."""

    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Create a temporary config file path."""
        return tmp_path / "test_config.json"

    @pytest.fixture
    def config_manager(self, temp_config_file):
        """Create a ConfigurationManager instance."""
        return ConfigurationManager(temp_config_file)

    def test_initialization_creates_default_config(self, config_manager, temp_config_file):
        """Test that initialization creates a default config file."""
        assert temp_config_file.exists()

        # Check default values
        assert config_manager.get("window_width") == 1024
        assert config_manager.get("window_height") == 768
        assert config_manager.get("font_size") == 32
        assert config_manager.get("theme") == "dark"

    def test_get_with_dot_notation(self, config_manager):
        """Test getting nested values with dot notation."""
        # Set a nested value
        config_manager._config["voice"] = {"sensitivity": 2, "enabled": True}

        assert config_manager.get("voice.sensitivity") == 2
        assert config_manager.get("voice.enabled") is True
        assert config_manager.get("voice.missing", "default") == "default"

    def test_set_value(self, config_manager, temp_config_file):
        """Test setting configuration values."""
        # Set a simple value
        config_manager.set("font_size", 48)
        assert config_manager.get("font_size") == 48

        # Verify it's saved
        with open(temp_config_file) as f:
            saved_config = json.load(f)
        assert saved_config["font_size"] == 48

    def test_set_with_validation(self, config_manager):
        """Test that set validates known keys."""
        # Valid value
        config_manager.set("window_width", 1920)
        assert config_manager.get("window_width") == 1920

        # Invalid value (out of range)
        with pytest.raises(InvalidConfigurationError) as exc_info:
            config_manager.set("window_width", 10000)
        assert "window_width" in str(exc_info.value)

    def test_update_multiple_values(self, config_manager):
        """Test updating multiple values at once."""
        updates = {
            "window_width": 1920,
            "window_height": 1080,
            "font_size": 36,
        }

        config_manager.update(updates)

        assert config_manager.get("window_width") == 1920
        assert config_manager.get("window_height") == 1080
        assert config_manager.get("font_size") == 36

    def test_update_with_validation_failure(self, config_manager):
        """Test that update validates all values."""
        updates = {
            "window_width": 1920,
            "font_size": 300,  # Invalid - too large
        }

        with pytest.raises(InvalidConfigurationError):
            config_manager.update(updates)

        # Ensure no partial updates
        assert config_manager.get("window_width") == 1024  # Original value

    def test_reset_all(self, config_manager):
        """Test resetting all configuration to defaults."""
        # Change some values
        config_manager.set("font_size", 48)
        config_manager.set("theme", "light")

        # Reset all
        config_manager.reset()

        assert config_manager.get("font_size") == 32
        assert config_manager.get("theme") == "dark"

    def test_reset_specific_key(self, config_manager):
        """Test resetting a specific key."""
        # Change values
        config_manager.set("font_size", 48)
        config_manager.set("theme", "light")

        # Reset only font_size
        config_manager.reset("font_size")

        assert config_manager.get("font_size") == 32
        assert config_manager.get("theme") == "light"  # Unchanged

    def test_has_key(self, config_manager):
        """Test checking if a key exists."""
        assert config_manager.has("window_width") is True
        assert config_manager.has("nonexistent_key") is False

        # Test nested keys
        config_manager._config["voice"] = {"sensitivity": 2}
        assert config_manager.has("voice.sensitivity") is True

    def test_require_existing_key(self, config_manager):
        """Test requiring an existing key."""
        assert config_manager.require("window_width") == 1024

    def test_require_missing_key(self, config_manager):
        """Test requiring a missing key raises exception."""
        with pytest.raises(MissingConfigurationError) as exc_info:
            config_manager.require("missing_key")
        assert "missing_key" in str(exc_info.value)

    def test_export_config(self, config_manager, tmp_path):
        """Test exporting configuration."""
        export_path = tmp_path / "exported_config.json"

        config_manager.set("font_size", 48)
        config_manager.export_config(export_path)

        assert export_path.exists()
        with open(export_path) as f:
            exported = json.load(f)
        assert exported["font_size"] == 48

    def test_import_config_merge(self, config_manager, tmp_path):
        """Test importing configuration with merge."""
        import_path = tmp_path / "import_config.json"
        import_data = {
            "font_size": 48,
            "theme": "light",
        }

        with open(import_path, "w") as f:
            json.dump(import_data, f)

        config_manager.import_config(import_path, merge=True)

        assert config_manager.get("font_size") == 48
        assert config_manager.get("theme") == "light"
        assert config_manager.get("window_width") == 1024  # Preserved

    def test_import_config_replace(self, config_manager, tmp_path):
        """Test importing configuration without merge."""
        import_path = tmp_path / "import_config.json"
        import_data = {
            "font_size": 48,
        }

        with open(import_path, "w") as f:
            json.dump(import_data, f)

        config_manager.import_config(import_path, merge=False)

        assert config_manager.get("font_size") == 48
        # Default values are still present
        assert config_manager.get("window_width") == 1024

    def test_load_corrupted_config(self, tmp_path):
        """Test loading a corrupted config file."""
        config_path = tmp_path / "corrupted_config.json"

        # Write invalid JSON
        with open(config_path, "w") as f:
            f.write("{invalid json}")

        # Should fall back to defaults
        config_manager = ConfigurationManager(config_path)
        assert config_manager.get("window_width") == 1024


class TestEnvironmentConfig:
    """Test the EnvironmentConfig class."""

    def test_get_overrides_simple(self):
        """Test getting simple environment overrides."""
        with patch.dict(os.environ, {
            "TELEPROMPTER_WINDOW_WIDTH": "1920",
            "TELEPROMPTER_FONT_SIZE": "48",
            "OTHER_VAR": "ignored",
        }):
            overrides = EnvironmentConfig.get_overrides()

            assert overrides == {
                "window_width": 1920,
                "font_size": 48,
            }

    def test_get_overrides_nested(self):
        """Test getting nested environment overrides."""
        with patch.dict(os.environ, {
            "TELEPROMPTER_VOICE__SENSITIVITY": "2",
            "TELEPROMPTER_VOICE__ENABLED": "true",
        }):
            overrides = EnvironmentConfig.get_overrides()

            assert overrides == {
                "voice.sensitivity": 2,
                "voice.enabled": True,
            }

    def test_get_overrides_json_values(self):
        """Test parsing JSON values from environment."""
        with patch.dict(os.environ, {
            "TELEPROMPTER_RECENT_FILES": '["file1.md", "file2.md"]',
            "TELEPROMPTER_DEBUG_MODE": "false",
        }):
            overrides = EnvironmentConfig.get_overrides()

            assert overrides == {
                "recent_files": ["file1.md", "file2.md"],
                "debug_mode": False,
            }


class TestGlobalConfiguration:
    """Test global configuration functions."""

    @patch('teleprompter.core.configuration._config_manager', None)
    def test_get_config_creates_instance(self):
        """Test that get_config creates a singleton instance."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2
        assert isinstance(config1, ConfigurationManager)

    @patch('teleprompter.core.configuration._config_manager', None)
    @patch.dict(os.environ, {"TELEPROMPTER_FONT_SIZE": "48"})
    def test_get_config_applies_env_overrides(self):
        """Test that get_config applies environment overrides."""
        config = get_config()
        assert config.get("font_size") == 48

    def test_setup_config_custom_path(self, tmp_path):
        """Test setting up config with custom path."""
        config_path = tmp_path / "custom_config.json"
        config = setup_config(config_path)

        assert isinstance(config, ConfigurationManager)
        assert config.config_path == config_path
        assert config_path.exists()
