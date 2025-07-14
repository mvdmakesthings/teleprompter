"""JSON-based settings storage implementation."""

import json
import os
from pathlib import Path
from typing import Any

from .protocols import SettingsStorageProtocol


class JsonSettingsStorage(SettingsStorageProtocol):
    """JSON file-based settings storage implementation.

    This implementation provides persistent storage of application settings
    using JSON files, making it framework-agnostic and portable.
    """

    def __init__(self, settings_file: str | Path | None = None):
        """Initialize the JSON settings storage.

        Args:
            settings_file: Path to the settings file. If None, uses default location.
        """
        if settings_file is None:
            settings_file = self._get_default_settings_path()

        self.settings_file = Path(settings_file)
        self._settings: dict[str, Any] = {}
        self._load_settings()

    def _get_default_settings_path(self) -> Path:
        """Get the default settings file path."""
        # Use XDG config directory on Linux/Mac, AppData on Windows
        if os.name == "nt":  # Windows
            appdata = os.environ.get("APPDATA")
            if appdata:
                config_dir = Path(appdata) / "teleprompter"
            else:
                config_dir = Path.home() / "AppData" / "Roaming" / "teleprompter"
        else:  # Linux/Mac
            config_dir = Path.home() / ".config" / "teleprompter"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "settings.json"

    def _load_settings(self) -> None:
        """Load settings from the JSON file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, encoding='utf-8') as f:
                    self._settings = json.load(f)
            except (OSError, json.JSONDecodeError):
                # If file is corrupted or can't be read, start with empty settings
                self._settings = {}
        else:
            self._settings = {}

    def _save_settings(self) -> None:
        """Save settings to the JSON file."""
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, sort_keys=True)
        except OSError:
            # Silently ignore save errors to prevent application crashes
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting value.

        Args:
            key: The setting key to retrieve.
            default: Default value to return if the key is not found.

        Returns:
            The stored value for the key, or the default value if not found.
        """
        # Support dot notation for nested values
        keys = key.split('.')
        value = self._settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Store a setting value.

        Args:
            key: The setting key to store.
            value: The value to store. Should be JSON-serializable.

        Raises:
            TypeError: If the value cannot be serialized to JSON.
        """
        # Test if value is JSON-serializable
        try:
            json.dumps(value)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Value for key '{key}' is not JSON-serializable") from e

        # Support dot notation for nested values
        keys = key.split('.')
        target = self._settings

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value
        self._save_settings()

    def remove(self, key: str) -> None:
        """Remove a setting.

        Args:
            key: The setting key to remove.
        """
        # Support dot notation for nested values
        keys = key.split('.')
        target = self._settings

        # Navigate to parent
        for k in keys[:-1]:
            if isinstance(target, dict) and k in target:
                target = target[k]
            else:
                return  # Key doesn't exist, nothing to remove

        # Remove the final key
        if isinstance(target, dict) and keys[-1] in target:
            del target[keys[-1]]
            self._save_settings()

    def clear(self) -> None:
        """Clear all settings.

        Removes all stored settings from the storage backend.
        """
        self._settings.clear()
        self._save_settings()

    def get_all(self) -> dict[str, Any]:
        """Get all settings as a dictionary.

        Returns:
            Dictionary containing all stored settings.
        """
        return self._settings.copy()

    def has(self, key: str) -> bool:
        """Check if a setting key exists.

        Args:
            key: The setting key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        return self.get(key, sentinel := object()) is not sentinel
