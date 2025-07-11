"""Scroll controller for managing scrolling behavior and state."""

from teleprompter.core.protocols import ScrollControllerProtocol
from teleprompter.utils.logging import LoggerMixin, log_method_calls


class ScrollController(ScrollControllerProtocol, LoggerMixin):
    """Controller for managing scroll behavior and state.

    This controller handles scrolling logic including speed control,
    position tracking, and scroll state management.
    """

    # Constants
    MIN_SPEED = 0.05
    MAX_SPEED = 5.0
    BASE_SCROLL_RATE = 100  # pixels per second at speed 1.0

    def __init__(self):
        """Initialize the scroll controller with default values."""
        self._is_scrolling: bool = False
        self._is_paused: bool = False
        self._speed: float = 1.0
        self._progress: float = 0.0
        self._viewport_height: int = 0
        self._content_height: int = 0
        self._scroll_position: int = 0

    def set_viewport_dimensions(
        self, viewport_height: int, content_height: int
    ) -> None:
        """Update viewport dimensions for scroll calculations.

        Args:
            viewport_height: Height of the visible viewport in pixels
            content_height: Total height of the content in pixels
        """
        self._viewport_height = max(0, viewport_height)
        self._content_height = max(0, content_height)
        self.log_debug(
            f"Viewport dimensions updated: viewport={viewport_height}px, "
            f"content={content_height}px"
        )

    @log_method_calls()
    def start_scrolling(self) -> None:
        """Start scrolling from current position."""
        self._is_scrolling = True
        self._is_paused = False
        self.log_info("Scrolling started")

    @log_method_calls()
    def stop_scrolling(self) -> None:
        """Stop scrolling completely and reset position."""
        self._is_scrolling = False
        self._is_paused = False
        self._scroll_position = 0
        self._progress = 0.0
        self.log_info("Scrolling stopped and reset")

    def pause_scrolling(self) -> None:
        """Pause scrolling (can be resumed)."""
        if self._is_scrolling:
            self._is_paused = True
            self.log_debug("Scrolling paused")

    def resume_scrolling(self) -> None:
        """Resume scrolling from pause."""
        if self._is_scrolling and self._is_paused:
            self._is_paused = False
            self.log_debug("Scrolling resumed")

    def toggle_scrolling(self) -> None:
        """Toggle between play and pause states."""
        if not self._is_scrolling:
            self.start_scrolling()
        elif self._is_paused:
            self.resume_scrolling()
        else:
            self.pause_scrolling()

    def set_speed(self, speed: float) -> None:
        """Set scrolling speed with validation.

        Args:
            speed: Scroll speed multiplier (0.05 to 5.0)
        """
        old_speed = self._speed
        self._speed = max(self.MIN_SPEED, min(self.MAX_SPEED, speed))

        if self._speed != old_speed:
            self.log_debug(f"Speed changed from {old_speed:.2f} to {self._speed:.2f}")

    def adjust_speed(self, delta: float) -> None:
        """Adjust speed by a delta amount.

        Args:
            delta: Amount to adjust speed by (positive or negative)
        """
        self.set_speed(self._speed + delta)

    def get_speed(self) -> float:
        """Get current scrolling speed.

        Returns:
            Current speed multiplier
        """
        return self._speed

    def is_scrolling(self) -> bool:
        """Check if currently scrolling (not paused).

        Returns:
            True if actively scrolling, False if stopped or paused
        """
        return self._is_scrolling and not self._is_paused

    def is_active(self) -> bool:
        """Check if scrolling is active (may be paused).

        Returns:
            True if in scrolling mode (even if paused)
        """
        return self._is_scrolling

    def get_progress(self) -> float:
        """Get current progress through the content.

        Returns:
            Progress as a value between 0.0 and 1.0
        """
        return self._progress

    def jump_to_position(self, position: float) -> None:
        """Jump to a specific position in the content.

        Args:
            position: Target position as a value between 0.0 and 1.0
        """
        self._progress = max(0.0, min(1.0, position))

        if self._content_height > self._viewport_height:
            max_scroll = self._content_height - self._viewport_height
            self._scroll_position = int(self._progress * max_scroll)
        else:
            self._scroll_position = 0

        self.log_debug(f"Jumped to position {self._progress:.2%}")

    def set_position(self, position: int) -> None:
        """Set scroll position directly (for backward compatibility).

        Args:
            position: Scroll position in pixels
        """
        self.update_scroll_position(position)

    def update_scroll_position(self, position: int) -> None:
        """Update scroll position and calculate progress.

        Args:
            position: New scroll position in pixels
        """
        self._scroll_position = max(0, position)

        if self._content_height > self._viewport_height:
            max_scroll = self._content_height - self._viewport_height
            self._progress = position / max_scroll if max_scroll > 0 else 0.0
        else:
            self._progress = 1.0

    def calculate_next_position(self, delta_time: float) -> int:
        """Calculate next scroll position based on speed and time delta.

        Args:
            delta_time: Time elapsed since last update in seconds

        Returns:
            Next scroll position in pixels
        """
        if not self.is_scrolling():
            return self._scroll_position

        # Calculate position change
        pixels_per_second = self.BASE_SCROLL_RATE * self._speed
        position_delta = pixels_per_second * delta_time
        new_position = self._scroll_position + position_delta

        # Clamp to valid range
        max_scroll = max(0, self._content_height - self._viewport_height)
        new_position = max(0, min(max_scroll, new_position))

        return int(new_position)

    def has_reached_end(self) -> bool:
        """Check if scrolling has reached the end of content.

        Returns:
            True if at the end of content
        """
        # Use 0.99 to account for floating point precision
        return self._progress >= 0.99

    def get_state(self) -> dict:
        """Get the current state of the scroll controller.

        Returns:
            Dictionary containing controller state
        """
        return {
            "is_scrolling": self._is_scrolling,
            "is_paused": self._is_paused,
            "speed": self._speed,
            "progress": self._progress,
            "scroll_position": self._scroll_position,
            "viewport_height": self._viewport_height,
            "content_height": self._content_height,
            "has_reached_end": self.has_reached_end(),
        }
