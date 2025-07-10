"""Settings management for persistent user preferences."""

import contextlib

from PyQt6.QtCore import QSettings

from . import config


class SettingsManager:
    """Manages application settings and user preferences."""

    def __init__(self):
        """Initialize the settings manager."""
        self.settings = QSettings("Teleprompter", "TeleprompterApp")

    def load_preferences(self) -> dict:
        """Load user preferences from settings.

        Returns:
            dict: Dictionary containing all user preferences
        """
        preferences = {}

        # Load font preset
        font_presets = list(config.FONT_PRESETS.keys())
        saved_font_preset = self.settings.value("font_preset", font_presets[0])
        if saved_font_preset in font_presets:
            preferences["font_preset_index"] = font_presets.index(saved_font_preset)
        else:
            preferences["font_preset_index"] = 0

        # Load window geometry
        preferences["geometry"] = self.settings.value("geometry")

        # Load speed setting
        saved_speed = self.settings.value("scroll_speed", config.DEFAULT_SPEED)
        with contextlib.suppress(ValueError, TypeError):
            preferences["speed"] = float(saved_speed)
        if "speed" not in preferences:
            preferences["speed"] = config.DEFAULT_SPEED

        return preferences

    def save_preferences(self, preferences: dict):
        """Save user preferences to settings.

        Args:
            preferences: Dictionary containing preferences to save
        """
        font_presets = list(config.FONT_PRESETS.keys())

        if "font_preset_index" in preferences:
            font_preset = font_presets[preferences["font_preset_index"]]
            self.settings.setValue("font_preset", font_preset)

        if "geometry" in preferences:
            self.settings.setValue("geometry", preferences["geometry"])

        if "speed" in preferences:
            self.settings.setValue("scroll_speed", preferences["speed"])

    def get_font_presets(self) -> list:
        """Get list of available font presets."""
        return list(config.FONT_PRESETS.keys())
