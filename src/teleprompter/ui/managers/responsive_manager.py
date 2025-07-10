"""Responsive layout management for the teleprompter application."""

from collections.abc import Callable

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QScreen

from ...core import config


class ResponsiveLayoutManager(QObject):
    """Manages responsive layout adaptations based on screen size and device type.

    This manager implements responsive design principles for the teleprompter
    application, automatically adjusting layouts, sizing, and behavior based
    on the current screen dimensions and device category.

    Device Categories:
    - mobile: ≤ 768px width - Simplified UI, larger touch targets
    - tablet: ≤ 1024px width - Medium density UI, touch-friendly
    - desktop: ≤ 1440px width - Standard desktop interface
    - large_desktop: > 1440px width - Spacious layout with extra features

    The manager provides callbacks for layout changes and maintains
    device-specific settings for optimal user experience across
    different screen sizes and input methods.

    Signals:
        category_changed (str): Emitted when device category changes.

    Attributes:
        _current_category (str): Current active device category.
        _callbacks (dict): Registered callbacks for each device category.
    """

    # Signal emitted when device category changes
    category_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize the responsive layout manager.

        Args:
            parent: Parent QObject for proper Qt object hierarchy.

        Sets up the manager with desktop as the default category and
        initializes empty callback lists for all device categories.
        """
        super().__init__(parent)
        self._current_category = "desktop"
        self._callbacks: dict[str, list[Callable]] = {
            "mobile": [],
            "tablet": [],
            "desktop": [],
            "large_desktop": [],
        }

    def get_device_category(self, width: int) -> str:
        """Determine device category based on screen width.

        Uses predefined breakpoints to categorize devices for appropriate
        UI adaptations. The categorization follows common responsive design
        patterns and ensures optimal user experience across device types.

        Args:
            width (int): Screen width in pixels.

        Returns:
            str: Device category - one of 'mobile', 'tablet', 'desktop',
                or 'large_desktop'.

        Note:
            Breakpoints are defined in the application configuration and
            can be adjusted for different responsive behavior requirements.
        """
        if width <= config.BREAKPOINTS["mobile"]:
            return "mobile"
        elif width <= config.BREAKPOINTS["tablet"]:
            return "tablet"
        elif width <= config.BREAKPOINTS["desktop"]:
            return "desktop"
        else:
            return "large_desktop"

    def register_layout_callback(self, category: str, callback: Callable) -> None:
        """Register a callback function for specific device category activation.

        Allows components to register functions that should be called when
        the application switches to a particular device category. This enables
        dynamic layout adjustments and feature toggling based on screen size.

        Args:
            category (str): Target device category - must be one of:
                'mobile', 'tablet', 'desktop', or 'large_desktop'.
            callback (Callable): Function to call when the category becomes active.
                Should accept no arguments and handle layout changes internally.

        Example:
            def setup_mobile_layout():
                # Adjust UI for mobile devices
                pass

            manager.register_layout_callback('mobile', setup_mobile_layout)

        Note:
            Callbacks are executed immediately when the device category changes.
            Multiple callbacks can be registered for the same category.
        """
        if category in self._callbacks:
            self._callbacks[category].append(callback)

    def update_layout(self, screen: QScreen) -> None:
        """Update layout based on current screen size.

        Args:
            screen: Current QScreen object
        """
        width = screen.size().width()
        new_category = self.get_device_category(width)

        if new_category != self._current_category:
            self._current_category = new_category
            self.category_changed.emit(new_category)

            # Call registered callbacks for this category
            for callback in self._callbacks.get(new_category, []):
                callback()

    def get_current_category(self) -> str:
        """Get the current device category."""
        return self._current_category

    def get_responsive_settings(self, category: str | None = None) -> dict:
        """Get responsive settings for a device category.

        Args:
            category: Device category (uses current if None)

        Returns:
            Dictionary of responsive settings
        """
        if category is None:
            category = self._current_category

        settings = {
            "mobile": {
                "progress_bar_height": 8,
                "info_overlay_height": 60,
                "font_size_multiplier": 0.9,
                "padding_multiplier": 1.2,
                "touch_target_size": 44,  # iOS HIG minimum
            },
            "tablet": {
                "progress_bar_height": 6,
                "info_overlay_height": 50,
                "font_size_multiplier": 0.95,
                "padding_multiplier": 1.1,
                "touch_target_size": 40,
            },
            "desktop": {
                "progress_bar_height": 4,
                "info_overlay_height": 40,
                "font_size_multiplier": 1.0,
                "padding_multiplier": 1.0,
                "touch_target_size": 32,
            },
            "large_desktop": {
                "progress_bar_height": 4,
                "info_overlay_height": 40,
                "font_size_multiplier": 1.1,
                "padding_multiplier": 1.0,
                "touch_target_size": 32,
            },
        }

        return settings.get(category, settings["desktop"])

    def calculate_responsive_font_size(self, base_size: int) -> int:
        """Calculate responsive font size based on current device category.

        Args:
            base_size: Base font size

        Returns:
            Adjusted font size
        """
        settings = self.get_responsive_settings()
        multiplier = settings.get("font_size_multiplier", 1.0)
        return int(base_size * multiplier)

    def get_optimal_line_height(self, font_size: int) -> float:
        """Calculate optimal line height based on font size and device.

        Args:
            font_size: Current font size

        Returns:
            Optimal line height multiplier
        """
        # Adjust line height based on device category
        base_line_height = self._calculate_base_line_height(font_size)

        if self._current_category == "mobile":
            # More line height on mobile for better readability
            return base_line_height * 1.1
        elif self._current_category == "tablet":
            return base_line_height * 1.05
        else:
            return base_line_height

    def _calculate_base_line_height(self, font_size: int) -> float:
        """Calculate base line height based on font size."""
        if font_size <= 20:
            return 1.7
        elif font_size <= 30:
            return 1.6
        elif font_size <= 40:
            return 1.5
        else:
            return 1.4

    def get_optimal_letter_spacing(self, font_size: int) -> str:
        """Calculate optimal letter spacing based on font size and device.

        Args:
            font_size: Current font size

        Returns:
            CSS letter-spacing value
        """
        # Base letter spacing calculation
        if font_size <= 20:
            base_spacing = 0.02
        elif font_size <= 30:
            base_spacing = 0.01
        elif font_size <= 40:
            base_spacing = 0.005
        else:
            base_spacing = -0.01

        # Adjust for device category
        if self._current_category == "mobile":
            # Slightly more spacing on mobile
            base_spacing += 0.005

        return f"{base_spacing}em"
