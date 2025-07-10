"""Protocol definitions for the teleprompter application.

This module defines interfaces (protocols) that establish contracts for various
components in the application, promoting loose coupling and testability.
"""

from typing import Any, Protocol, runtime_checkable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


@runtime_checkable
class FileLoaderProtocol(Protocol):
    """Protocol for file loading implementations."""

    def load_file(self, file_path: str) -> str:
        """Load content from a file."""
        ...

    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded."""
        ...

    def get_supported_extensions(self) -> list[str]:
        """Return list of supported file extensions."""
        ...


@runtime_checkable
class FileManagerProtocol(Protocol):
    """Protocol for file management operations."""

    def load_file(self, file_path: str) -> str:
        """Load content from a file."""
        ...

    def save_file(self, file_path: str, content: str) -> bool:
        """Save content to a file."""
        ...

    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded."""
        ...


@runtime_checkable
class HtmlContentAnalyzerProtocol(Protocol):
    """Protocol for HTML content analysis."""

    def count_words(self, html_content: str) -> int:
        """Count words in HTML content."""
        ...

    def find_sections(self, html_content: str) -> list[str]:
        """Find sections/headings in HTML content."""
        ...

    def analyze_html(self, html_content: str) -> dict:
        """Analyze HTML content and return statistics."""
        ...


@runtime_checkable
class ContentParserProtocol(Protocol):
    """Protocol for content parsing implementations."""

    def parse(self, content: str) -> str:
        """Parse content and return formatted output."""
        ...

    def get_word_count(self, content: str) -> int:
        """Get word count from content."""
        ...


@runtime_checkable
class StyleProviderProtocol(Protocol):
    """Protocol for style/theme providers."""

    def get_stylesheet(self, component: str) -> str:
        """Get stylesheet for a specific component."""
        ...

    def get_theme_variables(self) -> dict[str, Any]:
        """Get theme variables."""
        ...

    def set_theme(self, theme_name: str) -> None:
        """Set the active theme."""
        ...


@runtime_checkable
class SettingsStorageProtocol(Protocol):
    """Protocol for settings storage implementations."""

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting value."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Store a setting value."""
        ...

    def remove(self, key: str) -> None:
        """Remove a setting."""
        ...

    def clear(self) -> None:
        """Clear all settings."""
        ...


@runtime_checkable
class VoiceDetectorProtocol(Protocol):
    """Protocol for voice detection implementations."""

    # Signals
    voice_detected: pyqtSignal
    voice_stopped: pyqtSignal
    error_occurred: pyqtSignal

    def start(self) -> None:
        """Start voice detection."""
        ...

    def stop(self) -> None:
        """Stop voice detection."""
        ...

    def is_running(self) -> bool:
        """Check if voice detection is running."""
        ...

    def set_sensitivity(self, level: int) -> None:
        """Set detection sensitivity (0-3)."""
        ...

    def get_audio_level(self) -> float:
        """Get current audio level (0.0-1.0)."""
        ...


@runtime_checkable
class ScrollControllerProtocol(Protocol):
    """Protocol for scroll control implementations."""

    def start_scrolling(self) -> None:
        """Start scrolling."""
        ...

    def stop_scrolling(self) -> None:
        """Stop scrolling."""
        ...

    def pause_scrolling(self) -> None:
        """Pause scrolling."""
        ...

    def set_speed(self, speed: float) -> None:
        """Set scrolling speed."""
        ...

    def get_progress(self) -> float:
        """Get current progress (0.0-1.0)."""
        ...

    def jump_to_position(self, position: float) -> None:
        """Jump to specific position (0.0-1.0)."""
        ...


@runtime_checkable
class ReadingMetricsProtocol(Protocol):
    """Protocol for reading metrics calculations."""

    def calculate_reading_time(self, word_count: int, wpm: float) -> float:
        """Calculate estimated reading time in seconds."""
        ...

    def calculate_words_per_minute(self, speed: float) -> float:
        """Calculate effective words per minute based on scroll speed."""
        ...

    def get_elapsed_time(self) -> float:
        """Get elapsed reading time in seconds."""
        ...

    def get_remaining_time(self) -> float:
        """Get remaining reading time in seconds."""
        ...


@runtime_checkable
class ToolbarFactoryProtocol(Protocol):
    """Protocol for toolbar creation."""

    def create_toolbar(self, parent: QWidget) -> QWidget:
        """Create and return a toolbar widget."""
        ...

    def connect_signals(self, controller: Any) -> None:
        """Connect toolbar signals to controller."""
        ...


@runtime_checkable
class IconProviderProtocol(Protocol):
    """Protocol for icon providers."""

    def get_icon(self, name: str, size: int | None = None) -> Any:
        """Get an icon by name."""
        ...

    def has_icon(self, name: str) -> bool:
        """Check if an icon exists."""
        ...

    def get_fallback_icon(self, name: str) -> str:
        """Get fallback text/unicode for an icon."""
        ...


class ManagerProtocol(Protocol):
    """Base protocol for all manager classes."""

    def initialize(self) -> None:
        """Initialize the manager."""
        ...

    def cleanup(self) -> None:
        """Clean up resources."""
        ...


class AnimatedWidgetProtocol(Protocol):
    """Protocol for animated widgets."""

    def start_animation(self) -> None:
        """Start the widget animation."""
        ...

    def stop_animation(self) -> None:
        """Stop the widget animation."""
        ...

    def set_animation_duration(self, duration: int) -> None:
        """Set animation duration in milliseconds."""
        ...


@runtime_checkable
class ResponsiveLayoutProtocol(Protocol):
    """Protocol for responsive layout management."""

    def get_device_category(self, width: int) -> str:
        """Determine device category based on width."""
        ...

    def update_layout(self, screen: Any) -> None:
        """Update layout based on screen."""
        ...

    def get_current_category(self) -> str:
        """Get current device category."""
        ...

    def get_responsive_settings(self, category: str | None = None) -> dict:
        """Get responsive settings for category."""
        ...

    def calculate_responsive_font_size(self, base_size: int) -> int:
        """Calculate responsive font size."""
        ...

    def get_optimal_line_height(self, font_size: int) -> float:
        """Get optimal line height."""
        ...

    def get_optimal_letter_spacing(self, font_size: int) -> str:
        """Get optimal letter spacing."""
        ...
