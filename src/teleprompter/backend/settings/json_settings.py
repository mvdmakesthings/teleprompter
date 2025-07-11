"""JSON-based settings management for the teleprompter application."""

import json
import os
from pathlib import Path
from typing import Any

from teleprompter.core.config import APPLICATION_NAME, DEFAULT_SPEED, ORGANIZATION_NAME


class JsonSettingsManager:
    """Manages application settings using JSON file storage."""

    def __init__(self, settings_file: str | None = None):
        """Initialize the JSON settings manager.
        
        Args:
            settings_file: Optional path to settings file. If not provided,
                         uses platform-specific default location.
        """
        if settings_file:
            self.settings_path = Path(settings_file)
        else:
            self.settings_path = self._get_default_settings_path()

        # Ensure directory exists
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing settings or create new
        self._settings = self._load_settings()

    def _get_default_settings_path(self) -> Path:
        """Get platform-specific default settings path."""
        # Use platform-specific config directories
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', ''))
        elif os.name == 'posix':
            if 'darwin' in os.sys.platform:  # macOS
                base_dir = Path.home() / 'Library' / 'Application Support'
            else:  # Linux
                base_dir = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
        else:
            base_dir = Path.home()

        return base_dir / ORGANIZATION_NAME / APPLICATION_NAME / 'settings.json'

    def _load_settings(self) -> dict:
        """Load settings from JSON file."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path) as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                # Return empty dict if file is corrupted or unreadable
                return {}
        return {}

    def _save_settings(self) -> None:
        """Save settings to JSON file."""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except OSError as e:
            # Log error but don't crash
            print(f"Error saving settings: {e}")

    def load_preferences(self) -> dict:
        """Load user preferences from settings.
        
        Returns:
            dict: Dictionary containing all user preferences
        """
        preferences = {}

        # Load window geometry
        preferences["geometry"] = self._settings.get("geometry")

        # Load speed setting
        saved_speed = self._settings.get("scroll_speed", DEFAULT_SPEED)
        try:
            preferences["speed"] = float(saved_speed)
        except (ValueError, TypeError):
            preferences["speed"] = DEFAULT_SPEED

        # Load auto-reload setting (default: enabled)
        preferences["auto_reload"] = self._settings.get("auto_reload", True)

        return preferences

    def save_preferences(self, preferences: dict) -> None:
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
        if key in self._settings:
            del self._settings[key]
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

    def get_all_settings(self) -> dict:
        """Get a copy of all settings.
        
        Returns:
            dict: Copy of all settings
        """
        return self._settings.copy()

    def update_settings(self, settings: dict) -> None:
        """Update multiple settings at once.
        
        Args:
            settings: Dictionary of settings to update
        """
        self._settings.update(settings)
        self._save_settings()
