"""Basic unit tests for the application that don't require full Qt setup."""

from unittest.mock import Mock, patch

from src.teleprompter.core.container import ServiceContainer, configure_container
from src.teleprompter.core.protocols import (
    ContentParserProtocol,
)


class TestApplicationBasics:
    """Test basic application functionality without full Qt setup."""

    def test_container_configuration(self):
        """Test that the container can be configured properly."""
        configure_container()
        container = ServiceContainer()

        # Container should be configured but empty (it's a new instance)
        assert container is not None

    def test_service_registration(self):
        """Test that services can be registered."""
        container = ServiceContainer()

        # Register a mock service
        mock_parser = Mock(spec=ContentParserProtocol)
        container.register(ContentParserProtocol, lambda: mock_parser)

        # Should be able to retrieve it
        parser = container.get(ContentParserProtocol)
        assert parser is mock_parser

    def test_app_initialization_mocked(self):
        """Test app initialization basics without full Qt setup."""
        # Simple test that container can be configured
        configure_container()
        container = ServiceContainer()

        # Test that we can register and retrieve services
        mock_parser = Mock(spec=ContentParserProtocol)
        container.register(ContentParserProtocol, lambda: mock_parser)

        retrieved = container.get(ContentParserProtocol)
        assert retrieved is mock_parser

    def test_content_manager_unit(self):
        """Test ContentManager in isolation."""
        from src.teleprompter.domain.content.manager import ContentManager
        from src.teleprompter.domain.content.parser import MarkdownParser

        parser = MarkdownParser()
        manager = ContentManager(parser)

        # Test basic functionality - check word count is 0 when no content
        assert manager.get_word_count() == 0

        # Load some content
        manager.load_content("# Test\n\nHello world")
        assert manager.get_word_count() > 0
        assert manager.get_parsed_content() != ""

    def test_scroll_controller_unit(self):
        """Test ScrollController in isolation."""
        from src.teleprompter.domain.reading.controller import ScrollController

        controller = ScrollController()

        # Test initial state
        assert controller.is_scrolling() is False
        assert controller.get_speed() == 1.0
        assert controller.get_progress() == 0.0

        # Test basic operations
        controller.set_speed(2.0)
        assert controller.get_speed() == 2.0

        controller.start_scrolling()
        assert controller.is_scrolling() is True

        controller.pause_scrolling()
        assert controller.is_scrolling() is False

    def test_markdown_parser_unit(self):
        """Test MarkdownParser in isolation."""
        from src.teleprompter.domain.content.parser import MarkdownParser

        parser = MarkdownParser()

        # Test basic parsing
        markdown = "# Title\n\nParagraph with **bold** text."
        html = parser.parse(markdown)

        assert "<h1" in html
        assert "Title" in html
        assert "<p>" in html
        assert "<strong>" in html or "<b>" in html
        assert "bold" in html

    def test_settings_manager_unit(self):
        """Test SettingsManager in isolation."""
        from src.teleprompter.infrastructure.settings_manager import SettingsManager

        with patch("src.teleprompter.infrastructure.settings_manager.QSettings"):
            manager = SettingsManager()

            # Test get with default
            value = manager.get("test_key", "default_value")
            assert value is not None

    def test_style_manager_unit(self):
        """Test StyleManager in isolation."""
        from src.teleprompter.ui.managers.style_manager import StyleManager

        manager = StyleManager()

        # Test basic functionality
        stylesheet = manager.get_stylesheet("application")
        assert stylesheet is not None
        assert len(stylesheet) > 0
        assert "QMainWindow" in stylesheet  # Changed from QWidget

        # Test that we can get progress bar stylesheet too
        progress_style = manager.get_stylesheet("progress_bar")
        assert progress_style is not None
        assert len(progress_style) > 0

        # Test web view stylesheet
        web_style = manager.get_stylesheet("web_view_background")
        assert web_style is not None

    def test_reading_metrics_unit(self):
        """Test ReadingMetricsService in isolation."""
        from src.teleprompter.domain.reading.metrics import ReadingMetricsService

        service = ReadingMetricsService()

        # Test initial state
        assert service.get_elapsed_time() == 0.0

        # Test word count setting
        service.set_word_count(100)

        # Test WPM calculation
        wpm = service.calculate_words_per_minute(2.0)
        assert wpm == 300.0  # 150 * 2.0 (base_wpm is 150)

    def test_content_analyzer_unit(self):
        """Test HtmlContentAnalyzer in isolation."""
        from src.teleprompter.domain.content.analyzer import HtmlContentAnalyzer

        analyzer = HtmlContentAnalyzer()

        # Test analysis
        html = "<h1>Title</h1><p>Content</p><h2>Subtitle</h2><p>More content</p>"
        analysis = analyzer.analyze_html(html)

        assert "total_words" in analysis
        assert "sections" in analysis
        assert analysis["total_words"] > 0
        assert len(analysis["sections"]) > 0

    def test_error_handling(self):
        """Test error handling classes."""
        from src.teleprompter.core.exceptions import TeleprompterError

        # Test base error with keyword args
        error = TeleprompterError("Test error", error_code="TEST_ERROR")
        assert "Test error" in str(error)
        assert error.error_code == "TEST_ERROR"

        # Test error with context
        error_with_context = TeleprompterError(
            "Error with context", context={"key": "value"}
        )
        assert error_with_context.context == {"key": "value"}
