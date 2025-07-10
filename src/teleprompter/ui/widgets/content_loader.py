"""Content loading and processing for the teleprompter widget."""

from collections.abc import Callable

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from ...core.protocols import (
    ContentParserProtocol,
    FileManagerProtocol,
    HtmlContentAnalyzerProtocol,
    ReadingMetricsProtocol,
)
from .javascript_manager import JavaScriptManager


class ContentLoadResult:
    """Result of content loading operation."""

    def __init__(
        self,
        success: bool,
        html_content: str = "",
        word_count: int = 0,
        sections: list = None,
        error_message: str = ""
    ):
        self.success = success
        self.html_content = html_content
        self.word_count = word_count
        self.sections = sections or []
        self.error_message = error_message


class ContentLoader(QObject):
    """Handles content loading and processing for the teleprompter."""

    # Signals
    content_loaded = pyqtSignal(ContentLoadResult)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()

    def __init__(
        self,
        file_manager: FileManagerProtocol,
        parser: ContentParserProtocol,
        analyzer: HtmlContentAnalyzerProtocol,
        metrics_service: ReadingMetricsProtocol,
        parent: QObject | None = None
    ):
        super().__init__(parent)
        self._file_manager = file_manager
        self._parser = parser
        self._analyzer = analyzer
        self._metrics_service = metrics_service
        self._loading = False

    def load_file(self, file_path: str) -> None:
        """Load content from a file.

        Args:
            file_path: Path to the file to load
        """
        if self._loading:
            return

        self._loading = True
        self.loading_started.emit()

        # Use timer to ensure UI updates
        QTimer.singleShot(10, lambda: self._perform_file_load(file_path))

    def _perform_file_load(self, file_path: str) -> None:
        """Perform the actual file loading."""
        try:
            # Load and parse content
            content = self._file_manager.load_file(file_path)
            html_content = self._parser.parse(content)

            # Analyze content
            word_count = self._analyzer.count_words(html_content)
            sections = self._analyzer.find_sections(html_content)

            # Update metrics
            self._metrics_service.set_word_count(word_count)

            # Create result
            result = ContentLoadResult(
                success=True,
                html_content=html_content,
                word_count=word_count,
                sections=sections
            )

        except Exception as e:
            result = ContentLoadResult(
                success=False,
                error_message=str(e)
            )

        self._loading = False
        self.loading_finished.emit()
        self.content_loaded.emit(result)

    def load_text(self, text: str, is_html: bool = False) -> None:
        """Load content from plain text or HTML.

        Args:
            text: The text content to load
            is_html: If True, text is already HTML and should not be parsed
        """
        if self._loading:
            return

        self._loading = True
        self.loading_started.emit()

        # Use timer to ensure UI updates
        QTimer.singleShot(10, lambda: self._perform_text_load(text, is_html))

    def _perform_text_load(self, text: str, is_html: bool = False) -> None:
        """Perform the actual text loading."""
        try:
            # Parse content if needed
            if is_html:
                html_content = text
            else:
                html_content = self._parser.parse(text)

            # Analyze content
            word_count = self._analyzer.count_words(html_content)
            sections = self._analyzer.find_sections(html_content)

            # Update metrics
            self._metrics_service.set_word_count(word_count)

            # Create result
            result = ContentLoadResult(
                success=True,
                html_content=html_content,
                word_count=word_count,
                sections=sections
            )

        except Exception as e:
            result = ContentLoadResult(
                success=False,
                error_message=str(e)
            )

        self._loading = False
        self.loading_finished.emit()
        self.content_loaded.emit(result)

    def is_loading(self) -> bool:
        """Check if content is currently loading."""
        return self._loading


class WebViewContentManager:
    """Manages content display in a web view."""

    def __init__(self, web_view):
        self._web_view = web_view
        self._js_manager = JavaScriptManager()
        self._current_font_size = 24
        self._sections = []

    def display_content(self, html_content: str, sections: list) -> None:
        """Display HTML content in the web view.

        Args:
            html_content: The HTML content to display
            sections: List of content sections
        """
        self._sections = sections

        # Set HTML content with proper encoding
        # Use setContent to ensure proper MIME type
        from PyQt6.QtCore import QUrl
        self._web_view.setHtml(html_content, QUrl())

        # Inject scripts after content loads
        self._web_view.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self) -> None:
        """Handle web view load finished."""
        # Disconnect to avoid multiple calls
        import contextlib
        with contextlib.suppress(Exception):
            self._web_view.loadFinished.disconnect(self._on_load_finished)

        # Inject all necessary scripts
        self._inject_scripts()

    def _inject_scripts(self) -> None:
        """Inject all necessary JavaScript."""
        page = self._web_view.page()

        # Inject scroll behavior
        page.runJavaScript(self._js_manager.get_scroll_behavior_script())

        # Inject section navigation
        page.runJavaScript(self._js_manager.get_section_navigation_script())

        # Apply font size
        self.set_font_size(self._current_font_size)

        # Setup section highlighting
        page.runJavaScript(self._js_manager.get_highlight_current_section_script())

    def set_font_size(self, size: int) -> None:
        """Set the font size.

        Args:
            size: Font size in pixels
        """
        self._current_font_size = size
        padding = 50  # Default padding

        script = self._js_manager.get_font_size_script(size, padding)
        self._web_view.page().runJavaScript(script)

    def set_cursor_visibility(self, visible: bool) -> None:
        """Set cursor visibility.

        Args:
            visible: Whether cursor should be visible
        """
        script = self._js_manager.get_cursor_visibility_script(visible)
        self._web_view.page().runJavaScript(script)

    def scroll_to_position(self, position: float) -> None:
        """Scroll to a specific position.

        Args:
            position: Position in pixels
        """
        script = self._js_manager.scroll_to_position(position)
        self._web_view.page().runJavaScript(script)

    def get_scroll_info(self, callback: Callable) -> None:
        """Get current scroll information.

        Args:
            callback: Function to call with scroll info
        """
        self._web_view.page().runJavaScript(
            "window.getScrollInfo()",
            callback
        )

    def navigate_to_section(self, index: int) -> None:
        """Navigate to a specific section.

        Args:
            index: Section index
        """
        script = f"window.navigateToSection({index})"
        self._web_view.page().runJavaScript(script)

    def highlight_current_section(self) -> None:
        """Highlight the current section being read."""
        self._web_view.page().runJavaScript("window.highlightCurrentSection()")

    def scroll_by_pixels(self, pixels: float) -> None:
        """Scroll by a number of pixels.

        Args:
            pixels: Number of pixels to scroll
        """
        script = f"window.scrollByPixels({pixels})"
        self._web_view.page().runJavaScript(script)
