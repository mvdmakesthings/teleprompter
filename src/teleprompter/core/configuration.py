"""Configuration management for the teleprompter application."""

import json
import os
import sys
from pathlib import Path
from typing import Any

from teleprompter.core.exceptions import (
    ConfigurationError,
    InvalidConfigurationError,
    MissingConfigurationError,
)
from teleprompter.infrastructure.logging import LoggerMixin
from teleprompter.utils.validators import TeleprompterConfigValidator


class ConfigurationManager(LoggerMixin):
    """Manages application configuration with validation and persistence."""

    def _safe_log_info(self, message: str) -> None:
        """Safe logging that won't fail if logger is not initialized."""
        try:
            self.log_info(message)
        except Exception:
            # Fallback to print if logging is not set up
            print(f"INFO: {message}")

    def _safe_log_error(self, message: str) -> None:
        """Safe logging that won't fail if logger is not initialized."""
        try:
            self.log_error(message)
        except Exception:
            # Fallback to print if logging is not set up
            print(f"ERROR: {message}", file=sys.stderr)

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file (uses default if None)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.validator = TeleprompterConfigValidator()
        self._config: dict[str, Any] = {}
        self._defaults: dict[str, Any] = self._get_default_config()
        self._load_config()

    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path."""
        # Use XDG config directory on Linux/Mac, AppData on Windows
        if os.name == "nt":  # Windows
            appdata = os.environ.get("APPDATA")
            if appdata:
                config_dir = Path(appdata) / "teleprompter"
            else:
                # Fallback to user home if APPDATA is not set
                config_dir = Path.home() / "AppData" / "Roaming" / "teleprompter"
        else:  # Linux/Mac
            config_dir = Path.home() / ".config" / "teleprompter"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration values."""
        return {
            # Window settings
            "window_width": 1024,
            "window_height": 768,
            "window_x": None,  # None means center
            "window_y": None,
            "fullscreen": False,
            # Display settings
            "font_size": 32,
            "font_family": "Arial",
            "line_height": 1.5,
            "text_color": "#e0e0e0",
            "background_color": "#1a1a1a",
            "theme": "dark",
            # Scrolling settings
            "scroll_speed": 1.0,
            "default_wpm": 150,
            "smooth_scrolling": True,
            "scroll_fps": 60,
            # Voice control settings
            "voice_enabled": False,
            "voice_sensitivity": 1,
            "voice_device": None,  # None means default device
            # File settings
            "last_file": None,
            "recent_files": [],
            "max_recent_files": 10,
            # UI settings
            "show_toolbar": True,
            "show_progress": True,
            "auto_hide_cursor": True,
            "cursor_hide_delay": 3000,  # milliseconds
            # Performance settings
            "enable_animations": True,
            "animation_duration": 200,  # milliseconds
            # Advanced settings
            "log_level": "INFO",
            "log_file": None,
            "debug_mode": False,
        }

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    loaded_config = json.load(f)

                # Merge with defaults
                self._config = {**self._defaults, **loaded_config}

                # Validate configuration
                self._config = self.validator.validate(self._config)

                self._safe_log_info(f"Configuration loaded from {self.config_path}")
            except json.JSONDecodeError as e:
                self._safe_log_error(f"Invalid JSON in config file: {e}")
                self._config = self._defaults.copy()
            except Exception as e:
                self._safe_log_error(f"Failed to load configuration: {e}")
                self._config = self._defaults.copy()
        else:
            self._config = self._defaults.copy()
            self._save_config()  # Create default config file

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, sort_keys=True)

            self._safe_log_info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self._safe_log_error(f"Failed to save configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested values)
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            config.get("window_width")  # Get top-level value
            config.get("voice.sensitivity")  # Get nested value
        """
        # Support dot notation for nested values
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
            save: Whether to save to file immediately

        Raises:
            InvalidConfigurationError: If value fails validation
        """
        # Support dot notation
        keys = key.split(".")

        # Validate if it's a known key
        if len(keys) == 1 and key in self.validator.validators:
            try:
                value = self.validator.validators[key](value)
            except Exception as e:
                raise InvalidConfigurationError(key, value, str(e)) from e

        # Set the value
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

        if save:
            self._save_config()

    def update(self, updates: dict[str, Any], save: bool = True) -> None:
        """Update multiple configuration values.

        Args:
            updates: Dictionary of key-value pairs to update
            save: Whether to save to file immediately

        Raises:
            InvalidConfigurationError: If any value fails validation
        """
        # Validate all updates first
        validated_updates = self.validator.validate(updates)

        # Apply updates
        for key, value in validated_updates.items():
            self.set(key, value, save=False)

        if save:
            self._save_config()

    def reset(self, key: str | None = None, save: bool = True) -> None:
        """Reset configuration to defaults.

        Args:
            key: Specific key to reset (resets all if None)
            save: Whether to save to file immediately
        """
        if key is None:
            # Reset all
            self._config = self._defaults.copy()
        elif key in self._defaults:
            # Reset specific key
            self._config[key] = self._defaults[key]

        if save:
            self._save_config()

    def get_all(self) -> dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()

    def has(self, key: str) -> bool:
        """Check if a configuration key exists."""
        return self.get(key, sentinel := object()) is not sentinel

    def require(self, key: str) -> Any:
        """Get a required configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            MissingConfigurationError: If key not found
        """
        if not self.has(key):
            raise MissingConfigurationError(key)
        return self.get(key)

    def export_config(self, path: Path) -> None:
        """Export configuration to a file.

        Args:
            path: Path to export file
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, sort_keys=True)

    def import_config(self, path: Path, merge: bool = True) -> None:
        """Import configuration from a file.

        Args:
            path: Path to import file
            merge: Whether to merge with existing config or replace

        Raises:
            ConfigurationError: If import fails
        """
        try:
            with open(path, encoding="utf-8") as f:
                imported = json.load(f)

            # Validate imported config
            validated = self.validator.validate(imported)

            if merge:
                self._config.update(validated)
            else:
                self._config = {**self._defaults, **validated}

            self._save_config()
        except Exception as e:
            raise ConfigurationError(f"Failed to import configuration: {e}") from e


class EnvironmentConfig:
    """Manages environment-based configuration overrides."""

    PREFIX = "CUEBIRD_"

    @classmethod
    def get_overrides(cls) -> dict[str, Any]:
        """Get configuration overrides from environment variables.

        Environment variables should be prefixed with CUEBIRD_
        and use double underscores for nested values.

        Example:
            CUEBIRD_WINDOW_WIDTH=1920
            CUEBIRD_VOICE__SENSITIVITY=2
        """
        overrides = {}

        for key, value in os.environ.items():
            if key.startswith(cls.PREFIX):
                # Remove prefix and convert to lowercase
                config_key = key[len(cls.PREFIX) :].lower()

                # Convert double underscores to dots for nested values
                config_key = config_key.replace("__", ".")

                # Try to parse value as JSON first, then as string
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    parsed_value = value

                overrides[config_key] = parsed_value

        return overrides


# Global configuration instance
_config_manager: ConfigurationManager | None = None


def get_config() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()

        # Apply environment overrides
        env_overrides = EnvironmentConfig.get_overrides()
        if env_overrides:
            _config_manager.update(env_overrides)

    return _config_manager


def setup_config(config_path: Path | None = None) -> ConfigurationManager:
    """Set up the global configuration manager.

    Args:
        config_path: Custom configuration file path

    Returns:
        Configured ConfigurationManager instance
    """
    global _config_manager
    _config_manager = ConfigurationManager(config_path)

    # Apply environment overrides
    env_overrides = EnvironmentConfig.get_overrides()
    if env_overrides:
        _config_manager.update(env_overrides)

    return _config_manager
