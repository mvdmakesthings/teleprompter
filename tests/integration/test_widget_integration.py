"""Integration tests for widget components."""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from teleprompter.container import configure_container
from teleprompter.core.protocols import (
    ContentParserProtocol,
    FileManagerProtocol,
    HtmlContentAnalyzerProtocol,
    ReadingMetricsProtocol,
)
from teleprompter.ui.widgets.content_loader import ContentLoader, ContentLoadResult
from teleprompter.ui.widgets.teleprompter_widget import TeleprompterWidget


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def container():
    """Configure and provide the DI container."""
    return configure_container()


@pytest.fixture
def teleprompter_widget(qapp, container):
    """Create TeleprompterWidget instance."""
    widget = TeleprompterWidget()
    widget.show()
    QTest.qWaitForWindowExposed(widget)
    yield widget
    widget.close()


class TestContentLoaderIntegration:
    """Test content loader integration."""

    def test_content_loader_with_services(self, container):
        """Test content loader with real services."""
        # Get services from container
        file_manager = container.get(FileManagerProtocol)
        parser = container.get(ContentParserProtocol)
        analyzer = container.get(HtmlContentAnalyzerProtocol)
        metrics = container.get(ReadingMetricsProtocol)

        # Create content loader
        loader = ContentLoader(file_manager, parser, analyzer, metrics)

        # Test loading text
        result_received = False
        result_data = None

        def on_content_loaded(result: ContentLoadResult):
            nonlocal result_received, result_data
            result_received = True
            result_data = result

        loader.content_loaded.connect(on_content_loaded)

        # Load sample text
        sample_text = "# Test\n\nThis is a test document."
        loader.load_text(sample_text)

        # Wait for result
        QTest.qWait(500)

        assert result_received
        assert result_data.success
        assert result_data.word_count > 0
        assert len(result_data.sections) > 0

    def test_content_loader_error_handling(self, container):
        """Test content loader error handling."""
        file_manager = container.get(FileManagerProtocol)
        parser = container.get(ContentParserProtocol)
        analyzer = container.get(HtmlContentAnalyzerProtocol)
        metrics = container.get(ReadingMetricsProtocol)

        loader = ContentLoader(file_manager, parser, analyzer, metrics)

        error_received = False

        def on_content_loaded(result: ContentLoadResult):
            nonlocal error_received
            if not result.success:
                error_received = True

        loader.content_loaded.connect(on_content_loaded)

        # Try to load non-existent file
        loader.load_file("/path/to/nonexistent/file.md")
        QTest.qWait(500)

        assert error_received


class TestKeyboardCommandsIntegration:
    """Test keyboard commands integration."""

    def test_keyboard_command_registry(self, teleprompter_widget):
        """Test keyboard command registry with widget."""
        registry = teleprompter_widget.keyboard_commands

        # Test that default commands are registered
        shortcuts = registry.get_shortcuts_help()
        assert "Space" in shortcuts
        assert "R" in shortcuts
        assert "Esc" in shortcuts

    def test_custom_keyboard_command(self, teleprompter_widget):
        """Test adding custom keyboard command."""
        from teleprompter.ui.widgets.keyboard_commands import KeyboardCommand

        executed = False

        class CustomCommand(KeyboardCommand):
            def execute(self, widget):
                nonlocal executed
                executed = True
                return True

            def description(self):
                return "Custom test command"

        # Register custom command
        teleprompter_widget.keyboard_commands.register_command(
            Qt.Key.Key_X, CustomCommand()
        )

        # Trigger command
        teleprompter_widget.setFocus()
        QTest.keyClick(teleprompter_widget, Qt.Key.Key_X)

        assert executed


class TestJavaScriptManagerIntegration:
    """Test JavaScript manager integration."""

    def test_javascript_injection(self, teleprompter_widget):
        """Test JavaScript injection into web view."""
        js_manager = teleprompter_widget.js_manager

        # Load some content first
        teleprompter_widget.load_content("<h1>Test</h1><p>Content</p>")
        QTest.qWait(1000)

        # Test font size script
        font_script = js_manager.get_font_size_script(36, 50)
        assert "font-size: 36px" in font_script

        # Execute script
        result_received = False

        def on_result(result):
            nonlocal result_received
            result_received = True

        teleprompter_widget.web_view.page().runJavaScript(
            font_script + "; 'done'", on_result
        )

        QTest.qWait(500)
        assert result_received

    def test_scroll_behavior_script(self, teleprompter_widget):
        """Test scroll behavior JavaScript."""
        js_manager = teleprompter_widget.js_manager

        # Load content
        teleprompter_widget.load_content("<h1>Test</h1>" + "<p>Line</p>" * 100)
        QTest.qWait(1000)

        # Inject scroll behavior
        scroll_script = js_manager.get_scroll_behavior_script()

        teleprompter_widget.web_view.page().runJavaScript(scroll_script)
        QTest.qWait(500)

        # Test scroll info
        scroll_info = None

        def on_scroll_info(info):
            nonlocal scroll_info
            scroll_info = info

        teleprompter_widget.web_view.page().runJavaScript(
            "window.getScrollInfo()", on_scroll_info
        )

        QTest.qWait(500)
        assert scroll_info is not None
        assert "scrollTop" in scroll_info
        assert "scrollHeight" in scroll_info


class TestWidgetIntegration:
    """Test full widget integration."""

    def test_complete_workflow(self, teleprompter_widget):
        """Test complete workflow from loading to scrolling."""
        # Load content
        content = """# Integration Test Document

## Introduction
This is a test document for integration testing.

## Main Content
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Conclusion
This concludes our test document.
"""

        # Track signals
        signals_received = {
            "file_loaded": False,
            "speed_changed": False,
            "progress_changed": False,
            "reading_stats_changed": False,
        }

        def on_file_loaded(path):
            signals_received["file_loaded"] = True

        def on_speed_changed(speed):
            signals_received["speed_changed"] = True

        def on_progress_changed(progress):
            signals_received["progress_changed"] = True

        def on_stats_changed(stats):
            signals_received["reading_stats_changed"] = True

        # Connect signals
        teleprompter_widget.file_loaded.connect(on_file_loaded)
        teleprompter_widget.speed_changed.connect(on_speed_changed)
        teleprompter_widget.progress_changed.connect(on_progress_changed)
        teleprompter_widget.reading_stats_changed.connect(on_stats_changed)

        # Load content
        teleprompter_widget.load_content(content)
        QTest.qWait(1000)

        # Change speed
        teleprompter_widget.set_speed(2.0)

        # Start scrolling
        teleprompter_widget.play()
        QTest.qWait(2000)
        teleprompter_widget.pause()

        # Check signals were received
        assert signals_received["file_loaded"]
        assert signals_received["speed_changed"]
        assert signals_received["progress_changed"]
        assert signals_received["reading_stats_changed"]

    def test_responsive_behavior(self, teleprompter_widget):
        """Test responsive behavior of widget."""
        # Initial size
        teleprompter_widget.resize(1200, 800)
        QTest.qWait(100)

        # Check desktop layout
        assert (
            teleprompter_widget.responsive_manager.get_current_category() == "desktop"
        )

        # Resize to tablet
        teleprompter_widget.resize(768, 1024)
        QTest.qWait(100)

        # Check tablet layout
        category = teleprompter_widget.responsive_manager.get_current_category()
        assert category in ["tablet", "desktop"]  # May vary based on DPI

        # Resize to mobile
        teleprompter_widget.resize(375, 667)
        QTest.qWait(100)

        # Check mobile layout
        category = teleprompter_widget.responsive_manager.get_current_category()
        assert category in ["mobile", "tablet"]

    def test_voice_control_integration(self, teleprompter_widget):
        """Test voice control integration."""
        # Initially disabled
        assert not teleprompter_widget.voice_control_enabled

        # Enable voice control
        teleprompter_widget.enable_voice_control(True)
        assert teleprompter_widget.voice_control_enabled

        # Simulate voice activity (if detector is set)
        if teleprompter_widget.voice_detector:
            # This would trigger scrolling in real scenario
            pass

    def test_section_navigation_integration(self, teleprompter_widget):
        """Test section navigation with real content."""
        content = """# Document Title

## Section 1
First section content.

## Section 2
Second section content.

### Subsection 2.1
Subsection content.

## Section 3
Third section content.
"""

        # Load content
        teleprompter_widget.load_content(content)
        QTest.qWait(1000)

        # Get sections
        sections = teleprompter_widget.get_section_list()
        assert len(sections) >= 3

        # Navigate to next section
        teleprompter_widget.next_section()
        QTest.qWait(500)

        # Navigate to previous section
        teleprompter_widget.previous_section()
        QTest.qWait(500)

        # Jump to specific section
        teleprompter_widget.navigate_to_section(2)
        QTest.qWait(500)

    def test_concurrent_operations(self, teleprompter_widget):
        """Test concurrent operations don't cause issues."""
        # Load content
        teleprompter_widget.load_content("<h1>Test</h1>" + "<p>Paragraph</p>" * 50)
        QTest.qWait(500)

        # Start multiple operations
        teleprompter_widget.play()
        teleprompter_widget.set_speed(2.0)
        teleprompter_widget.set_font_size(36)
        teleprompter_widget.jump_by_percentage(10)

        QTest.qWait(1000)

        # Widget should still be functional
        teleprompter_widget.pause()
        assert not teleprompter_widget._is_scrolling


@pytest.mark.parametrize("font_size", [16, 24, 36, 48, 72])
def test_font_sizes(teleprompter_widget, font_size):
    """Test different font sizes."""
    teleprompter_widget.load_content("<h1>Test</h1><p>Content at different sizes</p>")
    QTest.qWait(500)

    teleprompter_widget.set_font_size(font_size)
    assert teleprompter_widget.current_font_size == font_size


def test_performance_under_load(teleprompter_widget):
    """Test performance with large document."""
    # Generate large document
    large_content = "<h1>Large Document</h1>\n"
    for i in range(100):
        large_content += f"<h2>Section {i}</h2>\n"
        large_content += "<p>" + " ".join(["word"] * 100) + "</p>\n" * 10

    # Measure loading time
    import time

    start_time = time.time()

    teleprompter_widget.load_content(large_content)
    QTest.qWait(2000)

    load_time = time.time() - start_time

    # Should load within reasonable time (5 seconds)
    assert load_time < 5.0

    # Test scrolling performance
    teleprompter_widget.play()
    QTest.qWait(3000)
    teleprompter_widget.pause()

    # Widget should still be responsive
    progress = teleprompter_widget.scroll_controller.get_progress()
    assert 0 <= progress <= 1
