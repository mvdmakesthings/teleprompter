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

        # Load theme
        color_themes = list(config.COLOR_THEMES.keys())
        saved_theme = self.settings.value("color_theme", color_themes[0])
        if saved_theme in color_themes:
            preferences["theme_index"] = color_themes.index(saved_theme)
        else:
            preferences["theme_index"] = 0

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
        color_themes = list(config.COLOR_THEMES.keys())

        if "font_preset_index" in preferences:
            font_preset = font_presets[preferences["font_preset_index"]]
            self.settings.setValue("font_preset", font_preset)

        if "theme_index" in preferences:
            theme = color_themes[preferences["theme_index"]]
            self.settings.setValue("color_theme", theme)

        if "geometry" in preferences:
            self.settings.setValue("geometry", preferences["geometry"])

        if "speed" in preferences:
            self.settings.setValue("scroll_speed", preferences["speed"])

    def get_font_presets(self) -> list:
        """Get list of available font presets."""
        return list(config.FONT_PRESETS.keys())

    def get_color_themes(self) -> list:
        """Get list of available color themes."""
        return list(config.COLOR_THEMES.keys())
