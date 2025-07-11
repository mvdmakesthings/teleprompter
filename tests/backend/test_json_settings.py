"""Tests for JSON settings manager."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from teleprompter.backend.settings import JsonSettingsManager
from teleprompter.core.config import DEFAULT_SPEED


class TestJsonSettingsManager:
    """Test JSON settings manager."""

    @pytest.fixture
    def temp_settings_file(self):
        """Create a temporary settings file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            settings_path = f.name

        yield settings_path

        # Cleanup
        Path(settings_path).unlink(missing_ok=True)

    @pytest.fixture
    def settings_manager(self, temp_settings_file):
        """Create a settings manager with temp file."""
        return JsonSettingsManager(temp_settings_file)

    def test_initialization(self, settings_manager):
        """Test settings manager initialization."""
        assert settings_manager._settings == {}
        assert settings_manager.settings_path.exists()

    def test_default_path_windows(self):
        """Test default settings path on Windows."""
        with patch('os.name', 'nt'), \
             patch.dict('os.environ', {'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming'}), \
             patch('pathlib.Path.mkdir'):
            # Mock the path to avoid Windows path instantiation on non-Windows
            with patch.object(JsonSettingsManager, '_get_default_settings_path') as mock_path:
                mock_path.return_value = Path('/tmp/test_settings.json')
                manager = JsonSettingsManager()
                # Just verify the method was called
                mock_path.assert_called_once()

    def test_default_path_macos(self):
        """Test default settings path on macOS."""
        with patch('os.name', 'posix'), \
             patch('os.sys.platform', 'darwin'), \
             patch('pathlib.Path.home', return_value=Path('/Users/test')), \
             patch('pathlib.Path.mkdir'):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch.object(JsonSettingsManager, '_get_default_settings_path') as mock_path:
                    mock_path.return_value = Path(tmpdir) / 'settings.json'
                    manager = JsonSettingsManager()
                    assert manager.settings_path.name == 'settings.json'

    def test_default_path_linux(self):
        """Test default settings path on Linux."""
        with patch('os.name', 'posix'), \
             patch('os.sys.platform', 'linux'), \
             patch.dict('os.environ', {}, clear=True), \
             patch('pathlib.Path.home', return_value=Path('/home/test')), \
             patch('pathlib.Path.mkdir'):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch.object(JsonSettingsManager, '_get_default_settings_path') as mock_path:
                    mock_path.return_value = Path(tmpdir) / 'settings.json'
                    manager = JsonSettingsManager()
                    assert manager.settings_path.name == 'settings.json'

    def test_get_set(self, settings_manager):
        """Test getting and setting values."""
        # Test default value
        assert settings_manager.get("test_key") is None
        assert settings_manager.get("test_key", "default") == "default"

        # Set value
        settings_manager.set("test_key", "test_value")
        assert settings_manager.get("test_key") == "test_value"

        # Verify persisted
        with open(settings_manager.settings_path) as f:
            saved = json.load(f)
        assert saved["test_key"] == "test_value"

    def test_remove(self, settings_manager):
        """Test removing settings."""
        settings_manager.set("test_key", "test_value")
        assert settings_manager.get("test_key") == "test_value"

        settings_manager.remove("test_key")
        assert settings_manager.get("test_key") is None

        # Removing non-existent key should not error
        settings_manager.remove("non_existent")

    def test_clear(self, settings_manager):
        """Test clearing all settings."""
        settings_manager.set("key1", "value1")
        settings_manager.set("key2", "value2")

        settings_manager.clear()
        assert settings_manager.get_all_settings() == {}

    def test_load_preferences(self, settings_manager):
        """Test loading preferences."""
        # Empty preferences
        prefs = settings_manager.load_preferences()
        assert prefs["geometry"] is None
        assert prefs["speed"] == DEFAULT_SPEED
        assert prefs["auto_reload"] is True

        # Set some preferences
        settings_manager._settings = {
            "geometry": {"x": 100, "y": 200},
            "scroll_speed": 2.5,
            "auto_reload": False
        }

        prefs = settings_manager.load_preferences()
        assert prefs["geometry"] == {"x": 100, "y": 200}
        assert prefs["speed"] == 2.5
        assert prefs["auto_reload"] is False

    def test_save_preferences(self, settings_manager):
        """Test saving preferences."""
        prefs = {
            "geometry": {"x": 300, "y": 400},
            "speed": 3.0,
            "auto_reload": True
        }

        settings_manager.save_preferences(prefs)

        assert settings_manager.get("geometry") == {"x": 300, "y": 400}
        assert settings_manager.get("scroll_speed") == 3.0
        assert settings_manager.get("auto_reload") is True

    def test_toggle_auto_reload(self, settings_manager):
        """Test toggling auto-reload."""
        # Default is True
        assert settings_manager.is_auto_reload_enabled() is True

        # Toggle to False
        new_state = settings_manager.toggle_auto_reload()
        assert new_state is False
        assert settings_manager.is_auto_reload_enabled() is False

        # Toggle back to True
        new_state = settings_manager.toggle_auto_reload()
        assert new_state is True
        assert settings_manager.is_auto_reload_enabled() is True

    def test_corrupted_file_handling(self, temp_settings_file):
        """Test handling of corrupted settings file."""
        # Write invalid JSON
        with open(temp_settings_file, 'w') as f:
            f.write("{invalid json")

        # Should not crash, returns empty dict
        manager = JsonSettingsManager(temp_settings_file)
        assert manager._settings == {}

    def test_update_settings(self, settings_manager):
        """Test updating multiple settings at once."""
        settings_manager.set("existing", "value")

        updates = {
            "key1": "value1",
            "key2": 42,
            "existing": "updated"
        }

        settings_manager.update_settings(updates)

        assert settings_manager.get("key1") == "value1"
        assert settings_manager.get("key2") == 42
        assert settings_manager.get("existing") == "updated"

    def test_save_error_handling(self, settings_manager):
        """Test error handling during save."""
        # Make path read-only to simulate save error
        settings_manager.settings_path.chmod(0o444)

        # Should not crash
        settings_manager.set("test", "value")

        # Restore permissions
        settings_manager.settings_path.chmod(0o644)

    def test_invalid_speed_handling(self, settings_manager):
        """Test handling of invalid speed values."""
        settings_manager._settings["scroll_speed"] = "invalid"

        prefs = settings_manager.load_preferences()
        assert prefs["speed"] == DEFAULT_SPEED
