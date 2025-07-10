"""Unit tests for scroll controller."""

from unittest.mock import Mock, patch

import pytest

from teleprompter.domain.reading import ScrollController


class TestScrollController:
    """Test the ScrollController class."""

    @pytest.fixture
    def controller(self):
        """Create a ScrollController instance."""
        return ScrollController()

    def test_initialization(self, controller):
        """Test controller initialization."""
        assert controller._speed == 1.0
        assert controller._is_playing is False
        assert controller._position == 0.0
        assert controller._max_position == 0.0
        assert controller._update_callback is None

    def test_set_speed(self, controller):
        """Test setting scroll speed."""
        controller.set_speed(2.5)
        assert controller._speed == 2.5

        # Test with callback
        mock_callback = Mock()
        controller.set_update_callback(mock_callback)
        controller.set_speed(3.0)
        mock_callback.assert_called_once()

    def test_set_position(self, controller):
        """Test setting scroll position."""
        controller._max_position = 100.0

        # Normal position
        controller.set_position(50.0)
        assert controller._position == 50.0

        # Test clamping
        controller.set_position(150.0)
        assert controller._position == 100.0

        controller.set_position(-10.0)
        assert controller._position == 0.0

        # Test with callback
        mock_callback = Mock()
        controller.set_update_callback(mock_callback)
        controller.set_position(25.0)
        mock_callback.assert_called()

    def test_set_max_position(self, controller):
        """Test setting maximum position."""
        controller._position = 50.0

        # Set max position higher than current
        controller.set_max_position(100.0)
        assert controller._max_position == 100.0
        assert controller._position == 50.0  # Position unchanged

        # Set max position lower than current
        controller.set_max_position(30.0)
        assert controller._max_position == 30.0
        assert controller._position == 30.0  # Position clamped

    def test_play_pause(self, controller):
        """Test play/pause functionality."""
        assert controller.is_playing() is False

        controller.play()
        assert controller.is_playing() is True

        controller.pause()
        assert controller.is_playing() is False

        # Test toggle
        controller.toggle_play_pause()
        assert controller.is_playing() is True

        controller.toggle_play_pause()
        assert controller.is_playing() is False

    def test_reset(self, controller):
        """Test resetting controller."""
        # Set up some state
        controller._position = 50.0
        controller._max_position = 100.0
        controller._speed = 2.0
        controller._is_playing = True

        # Reset
        controller.reset()

        assert controller._position == 0.0
        assert controller._max_position == 0.0
        assert controller._speed == 1.0
        assert controller._is_playing is False

    def test_jump_forward(self, controller):
        """Test jumping forward."""
        controller._max_position = 100.0
        controller._position = 30.0

        # Normal jump
        controller.jump_forward(20.0)
        assert controller._position == 50.0

        # Jump beyond max
        controller.jump_forward(60.0)
        assert controller._position == 100.0

    def test_jump_backward(self, controller):
        """Test jumping backward."""
        controller._position = 50.0

        # Normal jump
        controller.jump_backward(20.0)
        assert controller._position == 30.0

        # Jump below zero
        controller.jump_backward(40.0)
        assert controller._position == 0.0

    def test_go_to_start(self, controller):
        """Test going to start."""
        controller._position = 50.0
        controller.go_to_start()
        assert controller._position == 0.0

    def test_go_to_end(self, controller):
        """Test going to end."""
        controller._max_position = 100.0
        controller._position = 50.0
        controller.go_to_end()
        assert controller._position == 100.0

    def test_get_progress(self, controller):
        """Test getting progress percentage."""
        # No content
        assert controller.get_progress() == 0.0

        # With content
        controller._max_position = 100.0
        controller._position = 0.0
        assert controller.get_progress() == 0.0

        controller._position = 50.0
        assert controller.get_progress() == 0.5

        controller._position = 100.0
        assert controller.get_progress() == 1.0

    def test_set_progress(self, controller):
        """Test setting progress by percentage."""
        controller._max_position = 200.0

        controller.set_progress(0.0)
        assert controller._position == 0.0

        controller.set_progress(0.5)
        assert controller._position == 100.0

        controller.set_progress(1.0)
        assert controller._position == 200.0

        # Test clamping
        controller.set_progress(1.5)
        assert controller._position == 200.0

        controller.set_progress(-0.5)
        assert controller._position == 0.0

    def test_update_callback(self, controller):
        """Test update callback mechanism."""
        mock_callback = Mock()

        # Set callback
        controller.set_update_callback(mock_callback)

        # Trigger updates
        controller.set_position(50.0)
        controller.set_speed(2.0)
        controller.play()

        assert mock_callback.call_count == 3

        # Remove callback
        controller.set_update_callback(None)
        controller.pause()
        assert mock_callback.call_count == 3  # No additional calls

    def test_speed_adjustment(self, controller):
        """Test speed adjustment methods."""
        controller._speed = 1.0

        # Increase speed
        controller.increase_speed(0.5)
        assert controller._speed == 1.5

        # Decrease speed
        controller.decrease_speed(0.25)
        assert controller._speed == 1.25

        # Don't go below minimum
        controller._speed = 0.1
        controller.decrease_speed(0.5)
        assert controller._speed >= 0.05  # Minimum speed

    def test_smooth_scroll_to(self, controller):
        """Test smooth scrolling to position."""
        controller._max_position = 100.0
        controller._position = 0.0

        # Mock the animation timer
        with patch.object(controller, '_start_smooth_scroll') as mock_start:
            controller.smooth_scroll_to(50.0)
            mock_start.assert_called_once()

        # Test invalid targets
        controller.smooth_scroll_to(-10.0)  # Should clamp to 0
        controller.smooth_scroll_to(150.0)  # Should clamp to max

    def test_is_at_start(self, controller):
        """Test checking if at start position."""
        controller._position = 0.0
        assert controller.is_at_start() is True

        controller._position = 0.5
        assert controller.is_at_start() is False

    def test_is_at_end(self, controller):
        """Test checking if at end position."""
        controller._max_position = 100.0

        controller._position = 100.0
        assert controller.is_at_end() is True

        controller._position = 99.5
        assert controller.is_at_end() is False

    def test_get_state(self, controller):
        """Test getting controller state."""
        controller._position = 50.0
        controller._max_position = 100.0
        controller._speed = 1.5
        controller._is_playing = True

        state = controller.get_state()

        assert state["position"] == 50.0
        assert state["max_position"] == 100.0
        assert state["speed"] == 1.5
        assert state["is_playing"] is True
        assert state["progress"] == 0.5
