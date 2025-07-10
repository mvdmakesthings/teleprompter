"""Settings management for the teleprompter application."""

import contextlib
from typing import Any

from PyQt6.QtCore import QSettings

from ..core.config import APPLICATION_NAME, DEFAULT_SPEED


class SettingsManager:
    """Manages application settings and user preferences."""

    def __init__(self):
        """Initialize the settings manager."""
        self.settings = QSettings("Teleprompter", APPLICATION_NAME)

    def load_preferences(self) -> dict:
        """Load user preferences from application settings.

        Returns:
            dict: Dictionary containing all user preferences
        """
        preferences = {}

        # Load window geometry
        preferences["geometry"] = self.settings.value("geometry")

        # Load speed setting
        saved_speed = self.settings.value("scroll_speed", DEFAULT_SPEED)
        with contextlib.suppress(ValueError, TypeError):
            preferences["speed"] = float(saved_speed)
        if "speed" not in preferences:
            preferences["speed"] = DEFAULT_SPEED

        return preferences

    def save_preferences(self, preferences: dict):
        """Save user preferences to settings.

        Args:
            preferences: Dictionary containing preferences to save
        """
        if "geometry" in preferences:
            self.settings.setValue("geometry", preferences["geometry"])

        if "speed" in preferences:
            self.settings.setValue("scroll_speed", preferences["speed"])

    # SettingsStorageProtocol implementation
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting value."""
        return self.settings.value(key, default)

    def set(self, key: str, value: Any) -> None:
        """Store a setting value."""
        self.settings.setValue(key, value)

    def remove(self, key: str) -> None:
        """Remove a setting."""
        self.settings.remove(key)

    def clear(self) -> None:
        """Clear all settings."""
        self.settings.clear()
