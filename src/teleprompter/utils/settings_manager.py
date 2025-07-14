"""Settings management for the teleprompter application."""

import contextlib
import json
import os
from pathlib import Path
from typing import Any

from ..core.config import DEFAULT_SPEED


class SettingsManager:
    """Manages application settings and user preferences."""

    def __init__(self):
        """Initialize the settings manager."""
        # Create settings directory in user config directory
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ['APPDATA']) / 'CueBird'
        else:  # macOS/Linux
            config_dir = Path.home() / '.config' / 'cuebird'

        config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = config_dir / 'settings.json'
        self._settings = self._load_settings()

    def _load_settings(self) -> dict:
        """Load settings from JSON file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file) as f:
                    return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
        return {}

    def _save_settings(self):
        """Save settings to JSON file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except OSError:
            pass

    def load_preferences(self) -> dict:
        """Load user preferences from application settings.

        Returns:
            dict: Dictionary containing all user preferences
        """
        preferences = {}

        # Load window geometry (ignore for backend-only)
        preferences["geometry"] = self._settings.get("geometry")

        # Load speed setting
        saved_speed = self._settings.get("scroll_speed", DEFAULT_SPEED)
        with contextlib.suppress(ValueError, TypeError):
            preferences["speed"] = float(saved_speed)
        if "speed" not in preferences:
            preferences["speed"] = DEFAULT_SPEED

        # Load auto-reload setting (default: enabled)
        preferences["auto_reload"] = self._settings.get("auto_reload", True)

        return preferences

    def save_preferences(self, preferences: dict):
        """Save user preferences to settings.

        Args:
            preferences: Dictionary containing preferences to save
        """
        if "geometry" in preferences:
            self._settings["geometry"] = preferences["geometry"]

        if "speed" in preferences:
            self._settings["scroll_speed"] = preferences["speed"]

        if "auto_reload" in preferences:
            self._settings["auto_reload"] = preferences["auto_reload"]

        self._save_settings()

    # SettingsStorageProtocol implementation
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Store a setting value."""
        self._settings[key] = value
        self._save_settings()

    def remove(self, key: str) -> None:
        """Remove a setting."""
        self._settings.pop(key, None)
        self._save_settings()

    def clear(self) -> None:
        """Clear all settings."""
        self._settings.clear()
        self._save_settings()

    def toggle_auto_reload(self) -> bool:
        """Toggle the auto-reload setting and return the new state.

        Returns:
            bool: The new auto-reload state
        """
        current_state = self.get("auto_reload", True)
        new_state = not current_state
        self.set("auto_reload", new_state)
        return new_state

    def is_auto_reload_enabled(self) -> bool:
        """Check if auto-reload is enabled.

        Returns:
            bool: True if auto-reload is enabled
        """
        return self.get("auto_reload", True)
