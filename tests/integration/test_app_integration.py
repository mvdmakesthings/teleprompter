"""Integration tests for the teleprompter application."""

import os
import tempfile

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from teleprompter.container import configure_container
from teleprompter.ui.app import TeleprompterApp


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def app(qapp):
    """Create TeleprompterApp instance."""
    configure_container()
    app = TeleprompterApp()
    app.show()
    QTest.qWaitForWindowExposed(app)
    yield app
    app.close()


@pytest.fixture
def sample_markdown_file():
    """Create a sample markdown file for testing."""
    content = """# Test Document

This is a test document for integration testing.

## Section 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Section 2

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
Nisi ut aliquip ex ea commodo consequat.

### Subsection 2.1

Duis aute irure dolor in reprehenderit in voluptate velit esse.
Cillum dolore eu fugiat nulla pariatur.

## Section 3

Excepteur sint occaecat cupidatat non proident, sunt in culpa.
Qui officia deserunt mollit anim id est laborum.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        file_path = f.name

    yield file_path

    # Cleanup
    os.unlink(file_path)


class TestApplicationIntegration:
    """Test application integration."""

    def test_application_startup(self, app):
        """Test that the application starts correctly."""
        assert app.isVisible()
        assert app.windowTitle() == "Teleprompter"
        assert app.teleprompter_widget is not None
        assert app.toolbar is not None

    def test_file_loading(self, app, sample_markdown_file):
        """Test loading a markdown file."""
        # Load file
        app.file_manager.load_file(sample_markdown_file)

        # Wait for loading to complete
        QTest.qWait(1000)

        # Check that content is loaded
        assert app.teleprompter_widget.current_content != ""
        assert app.teleprompter_widget.content_sections != []

    def test_play_pause_functionality(self, app, sample_markdown_file):
        """Test play/pause functionality."""
        # Load file first
        app.file_manager.load_file(sample_markdown_file)
        QTest.qWait(500)

        # Test play
        app.teleprompter_widget.play()
        assert app.teleprompter_widget.is_playing

        # Wait a bit
        QTest.qWait(500)

        # Test pause
        app.teleprompter_widget.pause()
        assert not app.teleprompter_widget.is_playing

    def test_speed_adjustment(self, app):
        """Test speed adjustment."""
        initial_speed = app.teleprompter_widget.current_speed

        # Increase speed
        app.teleprompter_widget.set_speed(2.0)
        assert app.teleprompter_widget.current_speed == 2.0

        # Decrease speed
        app.teleprompter_widget.set_speed(0.5)
        assert app.teleprompter_widget.current_speed == 0.5

        # Reset
        app.teleprompter_widget.set_speed(initial_speed)

    def test_font_size_adjustment(self, app):
        """Test font size adjustment."""
        # Set font size
        app.teleprompter_widget.set_font_size(36)
        assert app.teleprompter_widget.current_font_size == 36

        # Test limits
        app.teleprompter_widget.set_font_size(200)  # Too large
        assert app.teleprompter_widget.current_font_size <= 120

        app.teleprompter_widget.set_font_size(10)  # Too small
        assert app.teleprompter_widget.current_font_size >= 16

    def test_keyboard_shortcuts(self, app, sample_markdown_file):
        """Test keyboard shortcuts."""
        # Load file
        app.file_manager.load_file(sample_markdown_file)
        QTest.qWait(500)

        # Focus widget
        app.teleprompter_widget.setFocus()

        # Test space key (play/pause)
        QTest.keyClick(app.teleprompter_widget, Qt.Key.Key_Space)
        assert app.teleprompter_widget.is_playing

        QTest.keyClick(app.teleprompter_widget, Qt.Key.Key_Space)
        assert not app.teleprompter_widget.is_playing

        # Test R key (reset)
        QTest.keyClick(app.teleprompter_widget, Qt.Key.Key_R)
        assert app.teleprompter_widget.current_position == 0

    def test_toolbar_integration(self, app):
        """Test toolbar button functionality."""
        # Test play button
        play_button = app.play_button
        assert play_button is not None

        # Click play
        QTest.mouseClick(play_button, Qt.MouseButton.LeftButton)
        assert app.teleprompter_widget.is_playing

        # Click pause (same button)
        QTest.mouseClick(play_button, Qt.MouseButton.LeftButton)
        assert not app.teleprompter_widget.is_playing

    def test_settings_persistence(self, app):
        """Test that settings are saved and loaded."""
        # Change some settings
        app.teleprompter_widget.set_speed(1.5)
        app.teleprompter_widget.set_font_size(32)

        # Save settings
        app._save_settings()

        # Create new app instance
        new_app = TeleprompterApp()

        # Check settings are restored
        assert new_app.teleprompter_widget.current_speed == 1.5
        assert new_app.teleprompter_widget.current_font_size == 32

        new_app.close()

    def test_voice_control_toggle(self, app):
        """Test voice control toggle."""
        # Initially disabled
        assert not app.teleprompter_widget.voice_control_enabled

        # Enable voice control
        app.teleprompter_widget.enable_voice_control(True)
        assert app.teleprompter_widget.voice_control_enabled

        # Disable voice control
        app.teleprompter_widget.enable_voice_control(False)
        assert not app.teleprompter_widget.voice_control_enabled

    def test_section_navigation(self, app, sample_markdown_file):
        """Test section navigation."""
        # Load file
        app.file_manager.load_file(sample_markdown_file)
        QTest.qWait(500)

        # Get sections
        sections = app.teleprompter_widget.get_section_list()
        assert len(sections) > 0

        # Navigate to section
        app.teleprompter_widget.navigate_to_section(1)
        QTest.qWait(500)

        # Check current section
        section_info = app.teleprompter_widget.get_current_section_info()
        assert section_info["index"] >= 0

    def test_progress_tracking(self, app, sample_markdown_file):
        """Test progress tracking during scrolling."""
        # Load file
        app.file_manager.load_file(sample_markdown_file)
        QTest.qWait(500)

        progress_values = []

        def capture_progress(value):
            progress_values.append(value)

        # Connect to progress signal
        app.teleprompter_widget.progress_changed.connect(capture_progress)

        # Start scrolling
        app.teleprompter_widget.play()
        QTest.qWait(2000)  # Scroll for 2 seconds
        app.teleprompter_widget.pause()

        # Check progress was tracked
        assert len(progress_values) > 0
        assert all(0 <= p <= 1 for p in progress_values)

        # Disconnect signal
        app.teleprompter_widget.progress_changed.disconnect(capture_progress)


class TestResponsiveDesign:
    """Test responsive design features."""

    def test_window_resizing(self, app):
        """Test application responds to window resizing."""
        # Initial size
        initial_size = app.size()

        # Resize window
        app.resize(800, 600)
        QTest.qWait(100)

        # Check responsive manager updated
        assert app.teleprompter_widget.responsive_manager is not None

        # Resize to mobile size
        app.resize(400, 700)
        QTest.qWait(100)

        # Restore
        app.resize(initial_size)

    def test_fullscreen_mode(self, app):
        """Test fullscreen functionality."""
        # Enter fullscreen
        app.showFullScreen()
        QTest.qWait(500)
        assert app.isFullScreen()

        # Exit fullscreen
        app.showNormal()
        QTest.qWait(500)
        assert not app.isFullScreen()


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_file_loading(self, app):
        """Test loading an invalid file."""
        error_emitted = False

        def on_error(msg, error_type):
            nonlocal error_emitted
            error_emitted = True

        # Connect to error signal
        app.file_manager.error_occurred.connect(on_error)

        # Try to load non-existent file
        app.file_manager.load_file("/path/to/nonexistent/file.md")
        QTest.qWait(500)

        assert error_emitted

        # Disconnect
        app.file_manager.error_occurred.disconnect(on_error)

    def test_empty_file_handling(self, app):
        """Test handling of empty files."""
        # Create empty file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            file_path = f.name

        try:
            # Load empty file
            app.file_manager.load_file(file_path)
            QTest.qWait(500)

            # Should handle gracefully
            assert (
                app.teleprompter_widget.current_content != ""
            )  # Should show empty state
        finally:
            os.unlink(file_path)


@pytest.mark.parametrize("speed", [0.5, 1.0, 2.0, 5.0])
def test_different_scroll_speeds(app, sample_markdown_file, speed):
    """Test scrolling at different speeds."""
    # Load file
    app.file_manager.load_file(sample_markdown_file)
    QTest.qWait(500)

    # Set speed
    app.teleprompter_widget.set_speed(speed)

    # Start scrolling
    initial_position = app.teleprompter_widget.current_position
    app.teleprompter_widget.play()
    QTest.qWait(1000)
    app.teleprompter_widget.pause()
    final_position = app.teleprompter_widget.current_position

    # Check that position changed
    assert final_position > initial_position


def test_memory_usage_during_long_session(app, sample_markdown_file):
    """Test that memory usage remains stable during extended use."""
    import os

    import psutil

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Perform multiple operations
    for i in range(5):
        # Load file
        app.file_manager.load_file(sample_markdown_file)
        QTest.qWait(200)

        # Play and pause
        app.teleprompter_widget.play()
        QTest.qWait(500)
        app.teleprompter_widget.pause()

        # Change settings
        app.teleprompter_widget.set_speed(1.5 + i * 0.5)
        app.teleprompter_widget.set_font_size(24 + i * 4)

    # Check memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    # Memory increase should be reasonable (less than 50MB)
    assert memory_increase < 50, f"Memory increased by {memory_increase}MB"
