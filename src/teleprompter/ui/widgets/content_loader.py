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
    """Encapsulates the result of a content loading operation.

    This class provides a structured way to return loading results
    with all relevant information about the processed content.

    Attributes:
        success (bool): Whether the loading operation succeeded.
        html_content (str): Processed HTML content ready for display.
        word_count (int): Total number of words in the content.
        sections (list): List of content sections/headings for navigation.
        error_message (str): Error description if loading failed.

    Example:
        result = ContentLoadResult(
            success=True,
            html_content="<h1>Title</h1><p>Content...</p>",
            word_count=150,
            sections=["Introduction", "Main Content"]
        )
    """

    def __init__(
        self,
        success: bool,
        html_content: str = "",
        word_count: int = 0,
        sections: list = None,
        error_message: str = "",
    ):
        self.success = success
        self.html_content = html_content
        self.word_count = word_count
        self.sections = sections or []
        self.error_message = error_message


class ContentLoader(QObject):
    """Handles asynchronous content loading and processing for the teleprompter.

    The ContentLoader orchestrates the complete content loading pipeline,
    from file reading through parsing to final HTML generation ready for
    display in the teleprompter widget.

    Processing Pipeline:
    1. File loading via FileManager
    2. Content parsing (Markdown, text, etc.) to HTML
    3. HTML analysis for sections and word counting
    4. Reading metrics calculation and setup
    5. Result packaging and signal emission

    The loader operates asynchronously to prevent UI blocking during
    file operations and provides progress signals for UI feedback.

    Signals:
        content_loaded (ContentLoadResult): Emitted when loading completes.
        loading_started: Emitted when loading operation begins.
        loading_finished: Emitted when loading operation ends.

    Attributes:
        _file_manager: Service for file I/O operations.
        _parser: Service for content parsing and conversion.
        _analyzer: Service for HTML analysis and section extraction.
        _metrics_service: Service for reading time calculations.
        _loading: Flag indicating if loading is in progress.
    """

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
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._file_manager = file_manager
        self._parser = parser
        self._analyzer = analyzer
        self._metrics_service = metrics_service
        self._loading = False

    def load_file(self, file_path: str) -> None:
        """Load and process content from a file asynchronously.

        Initiates the complete content loading pipeline for the specified
        file. The operation runs asynchronously to prevent UI blocking,
        with progress signals emitted at key stages.

        Args:
            file_path (str): Absolute or relative path to the file to load.
                Supports various formats including Markdown, HTML, and text files.

        Note:
            If a loading operation is already in progress, this call is ignored
            to prevent overlapping operations. The loading process includes
            file reading, content parsing, HTML analysis, and metrics calculation.

        Signals Emitted:
            - loading_started: When the operation begins
            - content_loaded: When processing completes (with results)
            - loading_finished: When the operation ends
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

            # For markdown files, count words from the original markdown content
            # This is more accurate than counting from HTML
            if file_path.lower().endswith(".md"):
                if hasattr(self._parser, "get_word_count"):
                    word_count = self._parser.get_word_count(content)
                else:
                    # Fallback to simple word counting
                    word_count = len(content.split())
            else:
                # For non-markdown files, analyze the HTML
                word_count = self._analyzer.count_words(html_content)

            sections = self._analyzer.find_sections(html_content)

            # Update metrics
            self._metrics_service.set_word_count(word_count)

            # Create result
            result = ContentLoadResult(
                success=True,
                html_content=html_content,
                word_count=word_count,
                sections=sections,
            )

        except Exception as e:
            result = ContentLoadResult(success=False, error_message=str(e))

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
                # For HTML loaded directly (like empty state), check if it's actual content
                # by looking for common empty state indicators
                if (
                    "Welcome to Teleprompter" in html_content
                    or "No sections found" in html_content
                ):
                    word_count = 0
                    sections = []
                else:
                    word_count = self._analyzer.count_words(html_content)
                    sections = self._analyzer.find_sections(html_content)
            else:
                html_content = self._parser.parse(text)
                # For markdown content, count words from the original markdown
                # This is more accurate than counting from HTML
                if hasattr(self._parser, "get_word_count"):
                    word_count = self._parser.get_word_count(text)
                else:
                    word_count = self._analyzer.count_words(html_content)
                sections = self._analyzer.find_sections(html_content)

            # Update metrics
            self._metrics_service.set_word_count(word_count)

            # Create result
            result = ContentLoadResult(
                success=True,
                html_content=html_content,
                word_count=word_count,
                sections=sections,
            )

        except Exception as e:
            result = ContentLoadResult(success=False, error_message=str(e))

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

        # Clear any cached content first
        self._web_view.page().profile().clearHttpCache()

        # Set HTML content with proper encoding
        # Use a unique base URL to prevent caching issues
        import time

        from PyQt6.QtCore import QUrl

        # Create a unique URL to bypass any potential caching
        base_url = QUrl(f"local://content/{int(time.time() * 1000)}")
        self._web_view.setHtml(html_content, base_url)

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

        # Set up scroll update callback if parent has the method
        if hasattr(self._web_view.parent(), "_on_scroll_update"):
            page.runJavaScript("""
                window.onScrollUpdate = function(scrollTop) {
                    // Trigger progress update in Python
                    if (window._qt_progress_update_pending) return;
                    window._qt_progress_update_pending = true;
                    setTimeout(() => {
                        window._qt_progress_update_pending = false;
                    }, 50);
                };
            """)

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
        self._web_view.page().runJavaScript("window.getScrollInfo()", callback)

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
