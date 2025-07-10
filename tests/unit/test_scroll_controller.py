"""Unit tests for scroll controller."""

import pytest

from src.teleprompter.domain.reading.controller import ScrollController


class TestScrollController:
    """Test the ScrollController class."""

    @pytest.fixture
    def controller(self):
        """Create a ScrollController instance."""
        return ScrollController()

    def test_initialization(self, controller):
        """Test controller initialization."""
        assert controller._speed == 1.0
        assert controller._is_scrolling is False
        assert controller._is_paused is False
        assert controller._progress == 0.0
        assert controller._scroll_position == 0
        assert controller._viewport_height == 0
        assert controller._content_height == 0

    def test_set_speed(self, controller):
        """Test setting scroll speed."""
        controller.set_speed(2.5)
        assert controller.get_speed() == 2.5

        # Test clamping
        controller.set_speed(10.0)
        assert controller.get_speed() == 5.0  # MAX_SPEED

        controller.set_speed(0.01)
        assert controller.get_speed() == 0.05  # MIN_SPEED

    def test_set_position(self, controller):
        """Test setting scroll position."""
        controller.set_viewport_dimensions(100, 200)

        # Normal position
        controller.set_position(50)
        assert controller._scroll_position == 50

        # Test update_scroll_position
        controller.update_scroll_position(75)
        assert controller._scroll_position == 75
        assert controller._progress == 0.75  # 75/100 (max_scroll)

    def test_set_viewport_dimensions(self, controller):
        """Test setting viewport dimensions."""
        controller.set_viewport_dimensions(600, 1200)
        assert controller._viewport_height == 600
        assert controller._content_height == 1200

        # Test negative values (should be clamped to 0)
        controller.set_viewport_dimensions(-100, -200)
        assert controller._viewport_height == 0
        assert controller._content_height == 0

    def test_play_pause(self, controller):
        """Test play/pause functionality."""
        assert controller.is_scrolling() is False

        controller.start_scrolling()
        assert controller.is_scrolling() is True
        assert controller.is_active() is True

        controller.pause_scrolling()
        assert controller.is_scrolling() is False
        assert controller.is_active() is True

        controller.resume_scrolling()
        assert controller.is_scrolling() is True

        # Test toggle
        controller.toggle_scrolling()
        assert controller.is_scrolling() is False  # paused

        controller.toggle_scrolling()
        assert controller.is_scrolling() is True  # resumed

    def test_stop_scrolling(self, controller):
        """Test stopping and resetting controller."""
        # Set up some state
        controller._scroll_position = 50
        controller._progress = 0.5
        controller._speed = 2.0
        controller._is_scrolling = True
        controller._is_paused = True

        # Stop scrolling
        controller.stop_scrolling()

        assert controller._scroll_position == 0
        assert controller._progress == 0.0
        assert controller._is_scrolling is False
        assert controller._is_paused is False
        # Speed is not reset by stop_scrolling
        assert controller._speed == 2.0

    def test_jump_to_position(self, controller):
        """Test jumping to specific positions."""
        controller.set_viewport_dimensions(100, 200)

        # Normal jump
        controller.jump_to_position(0.5)
        assert controller._progress == 0.5
        assert controller._scroll_position == 50  # 0.5 * 100

        # Jump to start
        controller.jump_to_position(0.0)
        assert controller._progress == 0.0
        assert controller._scroll_position == 0

        # Jump to end
        controller.jump_to_position(1.0)
        assert controller._progress == 1.0
        assert controller._scroll_position == 100

        # Test clamping
        controller.jump_to_position(1.5)
        assert controller._progress == 1.0

        controller.jump_to_position(-0.5)
        assert controller._progress == 0.0

    def test_get_progress(self, controller):
        """Test getting progress percentage."""
        # No content (viewport >= content)
        controller.set_viewport_dimensions(100, 50)
        assert controller.get_progress() == 0.0

        # With content
        controller.set_viewport_dimensions(100, 200)
        controller.update_scroll_position(0)
        assert controller.get_progress() == 0.0

        controller.update_scroll_position(50)
        assert controller.get_progress() == 0.5

        controller.update_scroll_position(100)
        assert controller.get_progress() == 1.0

    def test_calculate_next_position(self, controller):
        """Test calculating next scroll position."""
        controller.set_viewport_dimensions(100, 300)
        controller._scroll_position = 50

        # Not scrolling - should return current position
        next_pos = controller.calculate_next_position(0.1)
        assert next_pos == 50

        # Start scrolling
        controller.start_scrolling()
        controller.set_speed(1.0)

        # Should advance by BASE_SCROLL_RATE * speed * delta_time
        # 100 * 1.0 * 0.1 = 10 pixels
        next_pos = controller.calculate_next_position(0.1)
        assert next_pos == 60

        # Test with different speed
        controller.set_speed(2.0)
        next_pos = controller.calculate_next_position(0.1)
        assert next_pos == 70  # 50 + (100 * 2.0 * 0.1)

        # Test clamping at end
        controller._scroll_position = 195
        next_pos = controller.calculate_next_position(0.1)
        assert next_pos == 200  # Clamped to max

    def test_has_reached_end(self, controller):
        """Test checking if reached end of content."""
        controller.set_viewport_dimensions(100, 200)

        controller._progress = 0.5
        assert controller.has_reached_end() is False

        controller._progress = 0.98
        assert controller.has_reached_end() is False

        controller._progress = 0.99
        assert controller.has_reached_end() is True

        controller._progress = 1.0
        assert controller.has_reached_end() is True

    def test_adjust_speed(self, controller):
        """Test speed adjustment methods."""
        controller.set_speed(1.0)

        # Increase speed
        controller.adjust_speed(0.5)
        assert controller.get_speed() == 1.5

        # Decrease speed
        controller.adjust_speed(-0.25)
        assert controller.get_speed() == 1.25

        # Don't go below minimum
        controller.set_speed(0.1)
        controller.adjust_speed(-0.1)
        assert controller.get_speed() == 0.05  # MIN_SPEED

        # Don't go above maximum
        controller.set_speed(4.8)
        controller.adjust_speed(0.5)
        assert controller.get_speed() == 5.0  # MAX_SPEED

    def test_pause_resume_behavior(self, controller):
        """Test pause/resume edge cases."""
        # Pausing when not scrolling does nothing
        controller.pause_scrolling()
        assert controller._is_paused is False

        # Start scrolling then pause
        controller.start_scrolling()
        controller.pause_scrolling()
        assert controller._is_paused is True
        assert controller.is_scrolling() is False
        assert controller.is_active() is True

        # Resume when not paused does nothing
        controller.stop_scrolling()
        controller.resume_scrolling()
        assert controller._is_scrolling is False

    def test_get_state(self, controller):
        """Test getting controller state."""
        controller.set_viewport_dimensions(100, 200)
        controller.update_scroll_position(50)
        controller.set_speed(1.5)
        controller.start_scrolling()

        state = controller.get_state()

        assert state["scroll_position"] == 50
        assert state["viewport_height"] == 100
        assert state["content_height"] == 200
        assert state["speed"] == 1.5
        assert state["is_scrolling"] is True
        assert state["is_paused"] is False
        assert state["progress"] == 0.5
        assert state["has_reached_end"] is False
