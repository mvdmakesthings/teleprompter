"""Modular teleprompter widget using refactored components."""

from PyQt6.QtCore import (
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QKeyEvent, QWheelEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...core import config
from ...core.container import get_container
from ...core.protocols import (
    ContentParserProtocol,
    FileManagerProtocol,
    HtmlContentAnalyzerProtocol,
    ReadingMetricsProtocol,
    ScrollControllerProtocol,
)
from ..managers.responsive_manager import ResponsiveLayoutManager
from ..managers.style_manager import StyleManager
from .content_loader import ContentLoader, ContentLoadResult, WebViewContentManager
from .javascript_manager import JavaScriptManager
from .keyboard_commands import KeyboardCommandRegistry


class ProgressBar(QWidget):
    """Custom progress bar for teleprompter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0  # 0.0 to 1.0
        self.setFixedHeight(4)
        self.setStyleSheet(StyleManager().get_progress_bar_stylesheet())

    def set_progress(self, progress: float):
        """Set progress value (0.0 to 1.0)."""
        self.progress = max(0.0, min(1.0, progress))
        self.update()

    def paintEvent(self, event):
        """Paint the progress bar."""
        from PyQt6.QtGui import QColor, QPainter, QPen

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawRect(0, 1, self.width(), 2)

        # Progress fill
        if self.progress > 0:
            progress_width = int(self.width() * self.progress)
            painter.setPen(QPen(QColor(0, 120, 212, 180), 2))
            painter.drawRect(0, 1, progress_width, 2)


class TeleprompterWidget(QWidget):
    """Modular teleprompter widget with improved architecture.

    This is the main teleprompter display widget that provides a comprehensive
    teleprompting experience including content display, auto-scrolling, voice
    control, progress tracking, and responsive design capabilities.

    The widget integrates multiple components:
    - Web view for HTML content display with custom CSS styling
    - Scroll controller for smooth, customizable auto-scrolling
    - Reading metrics for time estimation and progress tracking
    - Voice activity detection for hands-free operation
    - Responsive layout management for different screen sizes
    - JavaScript integration for advanced content manipulation

    Key Features:
    - Smooth auto-scrolling with adjustable speed (0.05x - 5.0x)
    - Voice-activated scrolling with customizable sensitivity
    - Manual navigation with mouse wheel and keyboard shortcuts
    - Section/chapter navigation for long documents
    - Reading progress tracking and time estimation
    - Responsive design for mobile, tablet, and desktop
    - Font size adjustment with optimal typography scaling
    - Full-screen support for distraction-free reading

    Signals:
        speed_changed (float): Emitted when scroll speed changes.
        voice_activity_changed (bool): Emitted when voice activity state changes.
        progress_changed (float): Emitted when reading progress changes.
        reading_stats_changed (dict): Emitted when reading statistics update.
        file_loaded (str): Emitted when a new file is loaded.
        error_occurred (str): Emitted when an error occurs.

    Attributes:
        web_view: QWebEngineView for displaying HTML content.
        content_loader: Manages content loading and processing.
        js_manager: Handles JavaScript execution and DOM manipulation.
        responsive_manager: Manages responsive layout adaptations.
        keyboard_registry: Handles keyboard shortcuts and commands.
        scroll_controller: Manages auto-scrolling behavior.
        reading_metrics: Tracks reading progress and time estimation.
    """

    # Signals
    speed_changed = pyqtSignal(float)
    voice_activity_changed = pyqtSignal(bool)
    progress_changed = pyqtSignal(float)
    reading_stats_changed = pyqtSignal(dict)
    file_loaded = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize the teleprompter widget.

        Args:
            parent: Parent widget, typically the main application window.

        Note:
            The widget automatically sets up all required services, UI components,
            managers, and signal connections. It initializes with default settings
            from the configuration and prepares for content loading.
        """
        super().__init__(parent)

        # Initialize components
        self._setup_services()
        self._setup_ui_components()
        self._setup_managers()
        self._setup_timers()
        self._setup_ui()
        self._connect_signals()

        # Initial state
        self.current_font_size = config.DEFAULT_FONT_SIZE
        self._is_scrolling = False
        self._manual_scroll_active = False
        self._current_sections = []
        self._current_section_index = 0
        self._voice_control_enabled = False
        self._voice_detector = None
        self._auto_hide_cursor = True
        self._show_progress = True

        # Legacy attributes for backward compatibility
        self.current_content = ""
        self.content_sections = []

    def _setup_services(self):
        """Initialize services from dependency container.

        Retrieves and initializes all required services from the dependency
        injection container, including file management, content parsing,
        HTML analysis, scroll control, and reading metrics.

        Note:
            This method establishes the service layer dependencies required
            for the teleprompter widget to function properly.
        """
        container = get_container()

        # Core services
        self.file_manager = container.get(FileManagerProtocol)
        self.parser = container.get(ContentParserProtocol)
        self.content_analyzer = container.get(HtmlContentAnalyzerProtocol)
        self.scroll_controller = container.get(ScrollControllerProtocol)
        self.reading_metrics = container.get(ReadingMetricsProtocol)

    def _setup_ui_components(self):
        """Initialize UI components.

        Creates and configures the core UI elements including:
        - QWebEngineView for HTML content display with disabled context menu
        - Progress bar for visual reading progress indication
        - Info overlay for displaying reading statistics and section information
        - Reading info label for word count and time estimates

        All components are styled according to the application theme and
        configured for optimal teleprompter display.
        """
        # Web view for content display
        self.web_view = QWebEngineView()
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.web_view.setStyleSheet(StyleManager().get_web_view_stylesheet())

        # Progress bar
        self.progress_bar = ProgressBar()

        # Info overlay
        self.info_overlay = QWidget()
        self.info_overlay.setStyleSheet(
            StyleManager().get_teleprompter_info_overlay_stylesheet()
        )
        self.info_overlay.setFixedHeight(40)

        # Labels
        self.reading_info_label = QLabel("Ready to read")
        self.reading_info_label.setStyleSheet(
            StyleManager().get_teleprompter_info_labels_stylesheet()
        )

        self.progress_label = QLabel("0%")
        self.progress_label.setStyleSheet(
            StyleManager().get_teleprompter_info_labels_stylesheet()
        )

    def _setup_managers(self):
        """Initialize manager objects and create component instances.

        Creates and configures all necessary manager components for the
        teleprompter widget including:
        - Content loaders for file and text processing
        - Web view content manager for HTML manipulation
        - Keyboard command registry for shortcuts
        - Responsive layout manager for adaptive UI
        - Style manager for consistent theming
        - JavaScript manager for advanced DOM operations

        These managers work together to provide the complete teleprompter
        functionality and user experience.
        """
        # Content management
        self.content_loader = ContentLoader(
            self.file_manager,
            self.parser,
            self.content_analyzer,
            self.reading_metrics,
            self,
        )
        self.web_content_manager = WebViewContentManager(self.web_view)

        # UI management
        self.keyboard_commands = KeyboardCommandRegistry()
        self.responsive_manager = ResponsiveLayoutManager(self)
        self.style_manager = StyleManager()

        # JavaScript manager
        self.js_manager = JavaScriptManager()

    def _setup_timers(self):
        """Initialize timer components for widget functionality.

        Creates and configures multiple QTimer instances for different
        aspects of the teleprompter operation:

        - scroll_timer: Controls the smooth auto-scrolling at the configured FPS
        - cursor_timer: Handles automatic cursor hiding during inactive periods
        - progress_timer: Updates the reading progress display in real-time

        Each timer is configured with appropriate intervals and behaviors
        to ensure smooth user experience and optimal performance.
        """
        # Scroll timer
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self._perform_scroll_step)
        self.scroll_timer.setInterval(int(1000 / config.SCROLL_FPS))

        # Auto-hide cursor timer
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self._hide_cursor)
        self.cursor_timer.setSingleShot(True)

        # Progress update timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress_display)
        self.progress_timer.setInterval(
            50
        )  # 20 updates per second for smoother progress

    def _setup_ui(self):
        """Set up the complete user interface layout and styling.

        Configures the main widget styling, focus policies, and mouse tracking.
        Creates and arranges the layout hierarchy consisting of:

        1. Progress bar at the top for visual reading progress
        2. Central web view for content display
        3. Info overlay at the bottom with reading statistics

        The layout uses zero margins and spacing for a clean, full-screen
        appearance suitable for teleprompting. All components are styled
        consistently using the StyleManager.
        """
        self.setStyleSheet(StyleManager().get_main_window_stylesheet())
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.web_view.setMouseTracking(True)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Progress bar at top
        layout.addWidget(self.progress_bar)

        # Web view
        layout.addWidget(self.web_view)

        # Info overlay at bottom
        info_layout = QHBoxLayout(self.info_overlay)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_layout.addWidget(self.reading_info_label)
        info_layout.addStretch()
        info_layout.addWidget(self.progress_label)
        layout.addWidget(self.info_overlay)

    def _connect_signals(self):
        """Connect internal component signals to their respective handlers.

        Establishes the signal-slot connections between different components
        to ensure proper communication and data flow. Connected signals include:

        - Content loader signals for tracking loading states and content updates
        - Web view signals for detecting when content is fully rendered
        - Internal timer and UI update signals for responsive user experience

        This method centralizes all signal connections for maintainability
        and clear understanding of component interactions.
        """
        # Content loader signals
        self.content_loader.content_loaded.connect(self._on_content_loaded)
        self.content_loader.loading_started.connect(self._on_loading_started)
        self.content_loader.loading_finished.connect(self._on_loading_finished)

        # Web view signals
        self.web_view.loadFinished.connect(self._on_web_view_loaded)

    # Properties for backward compatibility
    @property
    def current_speed(self):
        """Get the current scrolling speed multiplier.

        Returns:
            float: Current scroll speed as a multiplier (0.05 to 5.0),
                where 1.0 represents normal speed.
        """
        return self.scroll_controller.get_speed()

    @current_speed.setter
    def current_speed(self, value):
        """Set the scrolling speed multiplier.

        Args:
            value (float): Speed multiplier to set (0.05 to 5.0).
                Values below 0.05 will be clamped to minimum,
                values above 5.0 will be clamped to maximum.
        """
        self.scroll_controller.set_speed(value)

    @property
    def is_playing(self):
        """Check if auto-scrolling is currently active.

        Returns:
            bool: True if the teleprompter is actively scrolling content,
                False if paused or stopped.
        """
        return self.scroll_controller.is_scrolling()

    @is_playing.setter
    def is_playing(self, value):
        """Set the auto-scrolling state.

        Args:
            value (bool): True to start scrolling, False to stop/pause.
                Starting scrolling will also begin reading metrics tracking.
        """
        if value:
            self.scroll_controller.start_scrolling()
        else:
            self.scroll_controller.pause_scrolling()

    @property
    def current_position(self):
        """Get current scroll position."""
        return self.scroll_controller._scroll_position

    @current_position.setter
    def current_position(self, value):
        """Set scroll position."""
        self.scroll_controller._scroll_position = value

    @property
    def content_height(self):
        """Get content height."""
        return self.scroll_controller._content_height

    @content_height.setter
    def content_height(self, value):
        """Set content height."""
        self.scroll_controller._content_height = value

    @property
    def show_progress(self):
        """Get progress visibility."""
        return self._show_progress

    @show_progress.setter
    def show_progress(self, value):
        """Set progress visibility."""
        self.set_progress_visibility(value)

    @property
    def voice_control_enabled(self):
        """Get voice control state."""
        return self._voice_control_enabled

    @voice_control_enabled.setter
    def voice_control_enabled(self, value):
        """Set voice control state."""
        self.enable_voice_control(value)

    @property
    def voice_detector(self):
        """Get voice detector."""
        return self._voice_detector

    @voice_detector.setter
    def voice_detector(self, value):
        """Set voice detector."""
        self.set_voice_detector(value)

    @property
    def auto_hide_cursor(self):
        """Get cursor auto-hide state."""
        return self._auto_hide_cursor

    @auto_hide_cursor.setter
    def auto_hide_cursor(self, value):
        """Set cursor auto-hide state."""
        self._auto_hide_cursor = value
        if not value:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.cursor_timer.stop()

    # Public API methods
    def load_content(self, html_content: str):
        """Load HTML content directly into the teleprompter web view.

        Args:
            html_content (str): Raw HTML content to display. Should be
                well-formed HTML with proper structure and styling.

        Note:
            This method bypasses file loading and directly processes
            the provided HTML content. The content will be analyzed
            for reading metrics and section navigation.
        """
        self.current_content = html_content
        self.content_loader.load_text(html_content, is_html=True)

    def load_file(self, file_path: str):
        """Load and display content from a file.

        Args:
            file_path (str): Path to the file to load. Supports various
                formats including text, markdown, HTML, and other
                document types based on the configured file manager.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            PermissionError: If the file cannot be read due to permissions.
            UnicodeDecodeError: If the file encoding is not supported.

        Note:
            The file content will be processed through the content parser
            and analyzer to extract sections, estimate reading time, and
            prepare for optimal teleprompter display.
        """
        self.content_loader.load_file(file_path)

    def play(self):
        """Start scrolling."""
        self.start_scrolling()

    def pause(self):
        """Pause scrolling."""
        self.stop_scrolling()

    def toggle_playback(self):
        """Toggle between play and pause."""
        self.toggle_play_pause()

    def reset(self):
        """Reset scroll position to the beginning."""
        self.reset_position()

    def set_speed(self, speed: float):
        """Set the scrolling speed."""
        self.set_scroll_speed(speed)

    def adjust_speed(self, delta: float):
        """Adjust speed by delta amount."""
        current = self.get_scroll_speed()
        self.set_scroll_speed(current + delta)

    def set_font_size(self, size: int):
        """Set the font size for all teleprompter text content.

        Args:
            size (int): Font size in points. Should be between 8 and 72
                for optimal readability and performance.

        Note:
            The font size change is applied immediately to the web view
            content using CSS styling. The change affects all text
            elements while maintaining proper scaling and proportions.
            This setting persists until changed again or the widget is reset.
        """
        self.current_font_size = size
        self.web_content_manager.set_font_size(size)

    def ensure_focus(self):
        """Ensure the widget has focus for keyboard events."""
        self.setFocus()
        self.activateWindow()

    def navigate_to_section(self, section_index: int):
        """Navigate directly to a specific section or chapter.

        Args:
            section_index (int): Zero-based index of the target section.
                Must be within the range of available sections.

        Note:
            This method allows quick navigation to different parts of
            long documents. The section index is validated against the
            available sections list before navigation. If successful,
            the current section index is updated and the web view
            scrolls to the section's beginning.

        Example:
            # Navigate to the third section (index 2)
            widget.navigate_to_section(2)
        """
        if 0 <= section_index < len(self._current_sections):
            self._current_section_index = section_index
            self.web_content_manager.navigate_to_section(section_index)

    def navigate_to_next_section(self):
        """Navigate to the next section."""
        self.next_section()

    def navigate_to_previous_section(self):
        """Navigate to the previous section."""
        self.previous_section()

    def get_section_list(self) -> list:
        """Get the list of sections/chapters for navigation."""
        return self.content_sections.copy()

    def get_current_section_info(self) -> dict:
        """Get detailed information about the currently active section.

        Returns:
            dict: Section information containing:
                - index (int): Current section index (-1 if no sections)
                - title (str): Section title or heading text
                - total (int): Total number of available sections

        Note:
            This information is useful for displaying navigation state,
            progress indicators, and section-based controls in the UI.
            Returns default values if no sections are available.

        Example:
            info = widget.get_current_section_info()
            print(f"Section {info['index'] + 1} of {info['total']}: {info['title']}")
        """
        if not self._current_sections:
            return {"index": -1, "title": "", "total": 0}

        return {
            "index": self._current_section_index,
            "title": self._current_sections[self._current_section_index]
            if self._current_section_index < len(self._current_sections)
            else "",
            "total": len(self._current_sections),
        }

    def jump_to_progress(self, progress: float):
        """Jump to a specific progress point (0.0 to 1.0)."""
        self._jump_to_progress(progress)

    # Core functionality methods
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self._is_scrolling:
            self.stop_scrolling()
        else:
            self.start_scrolling()

    def start_scrolling(self):
        """Start automatic scrolling of the teleprompter content.

        Initiates the auto-scroll functionality by:
        1. Syncing the current scroll position with the web view
        2. Starting the scroll controller and reading metrics
        3. Beginning the scroll timer for smooth animation
        4. Updating the status to indicate active reading

        The scrolling will continue at the configured speed until
        manually paused or stopped. Voice control (if enabled)
        can also influence the scrolling behavior.

        Note:
            If scrolling is already active, this method has no effect.
            The scroll position is synchronized before starting to ensure
            accurate progress tracking.
        """
        if not self._is_scrolling:
            # Sync position first
            self.web_view.page().runJavaScript(
                "window.pageYOffset || (document.documentElement ? document.documentElement.scrollTop : 0)",
                lambda pos: self.scroll_controller.update_scroll_position(pos or 0),
            )

            self._is_scrolling = True
            self.scroll_controller.start_scrolling()
            self.reading_metrics.start_reading()
            self.scroll_timer.start()
            # Progress timer is always running now
            self._update_status("Reading...")

    def stop_scrolling(self):
        """Stop automatic scrolling and pause reading.

        Halts the auto-scroll functionality by:
        1. Stopping the scroll controller and reading metrics tracking
        2. Pausing the scroll timer while maintaining position
        3. Updating the status to indicate paused state

        The current scroll position is preserved, allowing the user
        to resume from the same location. Progress tracking continues
        to monitor any manual scrolling that occurs while paused.

        Note:
            If scrolling is not currently active, this method has no effect.
            Manual scrolling via mouse wheel or keyboard remains functional.
        """
        if self._is_scrolling:
            self._is_scrolling = False
            self.scroll_controller.pause_scrolling()
            self.reading_metrics.pause_reading()
            self.scroll_timer.stop()
            # Progress timer keeps running to track manual scrolling
            self._update_status("Paused")

    def reset_position(self):
        """Reset the teleprompter to the beginning of the content.

        Performs a complete reset by:
        1. Stopping all scrolling and reading metrics
        2. Resetting scroll position to the top (0)
        3. Clearing reading progress and time estimates
        4. Updating the display to show ready state

        This is useful for restarting a presentation or when switching
        to new content. All timers except progress tracking are stopped,
        and the user can begin reading from the start.

        Note:
            Any unsaved progress or reading statistics will be lost.
            The content remains loaded and ready for immediate playback.
        """
        self.scroll_controller.stop_scrolling()
        self.reading_metrics.stop_reading()
        self._is_scrolling = False
        self.scroll_timer.stop()
        # Progress timer keeps running

        self.web_content_manager.scroll_to_position(0)
        self.scroll_controller.set_position(0)
        self.reading_metrics.set_progress(0)
        self._update_progress_display()
        self._update_status("Ready")

    def get_scroll_speed(self) -> float:
        """Get current scroll speed."""
        return self.scroll_controller.get_speed()

    def set_scroll_speed(self, speed: float):
        """Set scroll speed."""
        speed = max(config.MIN_SPEED, min(config.MAX_SPEED, speed))
        self.scroll_controller.set_speed(speed)
        self.speed_changed.emit(speed)

    def jump_by_percentage(self, percentage: float):
        """Jump forward or backward by a percentage."""
        current_progress = self.reading_metrics.get_progress()
        new_progress = max(0, min(1, current_progress + (percentage / 100)))
        self._jump_to_progress(new_progress)

    def next_section(self):
        """Navigate to the next section."""
        if self._current_section_index < len(self._current_sections) - 1:
            self._current_section_index += 1
            self.web_content_manager.navigate_to_section(self._current_section_index)

    def previous_section(self):
        """Navigate to the previous section."""
        if self._current_section_index > 0:
            self._current_section_index -= 1
            self.web_content_manager.navigate_to_section(self._current_section_index)

    def toggle_voice_control(self):
        """Toggle voice control on/off."""
        self._voice_control_enabled = not self._voice_control_enabled
        self.voice_activity_changed.emit(self._voice_control_enabled)

    def toggle_cursor_visibility(self):
        """Toggle cursor visibility."""
        current_visible = self.cursor().shape() != Qt.CursorShape.BlankCursor
        self.web_content_manager.set_cursor_visibility(not current_visible)

        if current_visible:
            self.setCursor(Qt.CursorShape.BlankCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_progress_visibility(self, visible: bool):
        """Set whether progress indicators are visible."""
        self._show_progress = visible
        self.progress_bar.setVisible(visible)
        self.info_overlay.setVisible(visible)

    def enable_voice_control(self, enabled: bool):
        """Enable or disable voice-controlled scrolling."""
        self._voice_control_enabled = enabled

    def set_voice_detector(self, voice_detector):
        """Set the voice detector instance and connect signals."""
        self._voice_detector = voice_detector
        if voice_detector:
            voice_detector.voice_started.connect(self._on_voice_started)
            voice_detector.voice_stopped.connect(self._on_voice_stopped)

    # Event handlers
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard events."""
        if self.keyboard_commands.handle_key_press(event, self):
            event.accept()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events."""
        # Forward the wheel event to web view first
        if self.web_view:
            # Let the web view handle the scroll
            self.web_view.wheelEvent(event)

            # If auto-scrolling, pause it
            if self._is_scrolling:
                self._manual_scroll_active = True
                self.stop_scrolling()

                # Update UI button text if parent app has the method
                parent = self.parent()
                while parent:
                    if hasattr(parent, "play_button"):
                        parent.play_button.setText("Play")
                        break
                    parent = parent.parent()

            # Update scroll position and progress after a short delay
            QTimer.singleShot(50, self._sync_scroll_position)

            # Don't resume auto-scroll immediately - wait for user to stop scrolling
            if hasattr(self, "_resume_timer"):
                self._resume_timer.stop()
            self._resume_timer = QTimer()
            self._resume_timer.setSingleShot(True)
            self._resume_timer.timeout.connect(self._check_resume_auto_scroll)
            self._resume_timer.start(3000)  # Wait 3 seconds after last scroll

            event.accept()
        else:
            super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse movement for cursor auto-hide."""
        if self._auto_hide_cursor:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.cursor_timer.start(3000)  # Hide after 3 seconds
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press to regain focus."""
        self.setFocus()
        # Sync our position with the current scroll position when user clicks
        self.web_view.page().runJavaScript(
            "window.pageYOffset || (document.documentElement ? document.documentElement.scrollTop : 0)",
            lambda pos: setattr(self, "current_position", pos or 0),
        )
        super().mousePressEvent(event)

    # Private methods
    def _on_content_loaded(self, result: ContentLoadResult):
        """Handle content loaded event."""
        if result.success:
            self._current_sections = result.sections
            self._current_section_index = 0
            self.content_sections = result.sections  # Backward compatibility

            # Display content
            self.web_content_manager.display_content(
                result.html_content, result.sections
            )

            # Update reading metrics
            stats = {
                "total_words": result.word_count,
                "estimated_minutes": self.reading_metrics.calculate_reading_time(
                    result.word_count,
                    self.reading_metrics.calculate_words_per_minute(1.0),
                )
                / 60.0,
                "sections": result.sections,
            }
            self.reading_stats_changed.emit(stats)
            self._update_reading_info(stats)

            # Update status
            self._update_status(f"Loaded - {result.word_count} words")
            self.file_loaded.emit("")
        else:
            self._update_status(f"Error: {result.error_message}")
            self.error_occurred.emit(result.error_message)

    def _on_loading_started(self):
        """Handle loading started event."""
        self._update_status("Loading...")

    def _on_loading_finished(self):
        """Handle loading finished event."""
        pass

    def _on_web_view_loaded(self, ok: bool):
        """Handle web view content loaded."""
        if ok:
            # Get content height
            self.web_view.page().runJavaScript(
                "document.body.scrollHeight",
                lambda height: setattr(self, "content_height", height),
            )

            # Add responsive bottom padding
            self._add_bottom_padding()

            # Start progress timer to track all scrolling (manual and auto)
            self.progress_timer.start()

    def _perform_scroll_step(self):
        """Perform a single scroll step."""
        if not self._is_scrolling or self._manual_scroll_active:
            return

        # Check if user is manually scrolling
        self.web_view.page().runJavaScript(
            "window.userIsScrolling", self._handle_user_scrolling
        )

        # Check if user has manually scrolled and update our position
        self.web_view.page().runJavaScript(
            "window.manualScrollPosition || window.pageYOffset || (document.documentElement ? document.documentElement.scrollTop : 0)",
            self._update_position_from_manual_scroll,
        )

        # Update viewport dimensions
        self.scroll_controller.set_viewport_dimensions(
            self.height(), self.content_height
        )

        # Calculate next position
        delta_time = 1.0 / config.SCROLL_FPS
        next_position = self.scroll_controller.calculate_next_position(delta_time)

        # Update scroll position
        self.scroll_controller.update_scroll_position(next_position)

        # Check if we've reached the end
        if self.scroll_controller.has_reached_end():
            self.pause()

        # Scroll to position
        self.web_view.page().runJavaScript(f"window.scrollTo(0, {int(next_position)})")

        # Highlight current section
        self.web_content_manager.highlight_current_section()

    def _handle_user_scrolling(self, is_user_scrolling):
        """Handle user wheel scrolling by pausing auto-scroll."""
        if is_user_scrolling and self._is_scrolling:
            self._manual_scroll_active = True

    def _update_position_from_manual_scroll(self, manual_position):
        """Update auto-scroll position based on manual scroll."""
        if (
            manual_position is not None
            and abs(manual_position - self.scroll_controller._scroll_position) > 10
        ):
            # User has manually scrolled, update our position to match
            self.scroll_controller.update_scroll_position(manual_position)

    def _update_progress_display(self):
        """Update progress indicators."""
        # Always get the actual scroll position from the web view
        self.web_view.page().runJavaScript(
            """
            (function() {
                // Check if document is ready
                if (!document.documentElement) {
                    return null;
                }
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
                const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight || 0;
                const clientHeight = window.innerHeight || document.documentElement.clientHeight || 0;
                const maxScroll = Math.max(0, scrollHeight - clientHeight);
                const progress = maxScroll > 0 ? scrollTop / maxScroll : 0;
                return {
                    scrollTop: scrollTop,
                    maxScroll: maxScroll,
                    progress: Math.min(1.0, Math.max(0.0, progress))
                };
            })();
            """,
            self._handle_progress_update,
        )

    def _handle_progress_update(self, scroll_info):
        """Handle progress update from JavaScript."""
        if scroll_info and self.content_height > 0:
            progress = scroll_info.get("progress", 0)
            scroll_position = scroll_info.get("scrollTop", 0)

            # Update internal state
            self.scroll_controller.update_scroll_position(scroll_position)
            self.reading_metrics.set_progress(progress)

            # Update progress bar
            self.progress_bar.set_progress(progress)

            # Update progress label
            progress_percent = int(progress * 100)
            self.progress_label.setText(f"{progress_percent}%")

            # Emit progress signal
            self.progress_changed.emit(progress)

            # Update reading stats signal
            stats = {
                "progress": progress,
                "elapsed_time": self.reading_metrics.get_elapsed_time(),
                "remaining_time": self.reading_metrics.get_remaining_time(),
                "average_wpm": self.reading_metrics.get_average_wpm(),
            }
            self.reading_stats_changed.emit(stats)

    def _update_status(self, message: str):
        """Update status label."""
        # This could be implemented to update a status label if needed
        pass

    def _update_reading_info(self, stats: dict):
        """Update the reading information display."""
        minutes = stats.get("estimated_minutes", 0)
        if minutes < 1:
            time_str = f"{int(minutes * 60)}s"
        else:
            time_str = f"{int(minutes)}m {int((minutes % 1) * 60)}s"

        sections_count = len(stats.get("sections", []))
        section_text = f" • {sections_count} sections" if sections_count > 0 else ""

        self.reading_info_label.setText(
            f"{stats.get('total_words', 0)} words • ~{time_str}{section_text}"
        )

    def _jump_to_progress(self, progress: float):
        """Jump to a specific progress position."""
        if self.content_height > 0:
            target_position = progress * self.content_height
            self.current_position = max(
                0, min(target_position, self.content_height - self.height())
            )
            self.web_view.page().runJavaScript(
                f"window.scrollTo(0, {int(self.current_position)})"
            )
            self._update_progress_display()

    def _resume_auto_scroll(self):
        """Resume automatic scrolling after manual intervention."""
        if not self._is_scrolling and self._manual_scroll_active:
            self._manual_scroll_active = False
            self.start_scrolling()

    def _sync_scroll_position(self):
        """Sync scroll position from web view and update progress."""
        # Just trigger the unified progress update
        self._update_progress_display()

    def _check_resume_auto_scroll(self):
        """Check if we should resume auto-scrolling."""
        if (
            not self._is_scrolling
            and self._manual_scroll_active
            and not self.scroll_controller.has_reached_end()
        ):
            self._manual_scroll_active = False
            # Optionally auto-resume (you can make this configurable)
            # self.start_scrolling()

    def _hide_cursor(self):
        """Hide the cursor."""
        if self._auto_hide_cursor:
            self.setCursor(Qt.CursorShape.BlankCursor)

    def _on_voice_started(self):
        """Handle voice activity start."""
        if self._voice_control_enabled and not self._is_scrolling:
            self.start_scrolling()
            self.voice_activity_changed.emit(True)

    def _on_voice_stopped(self):
        """Handle voice activity stop."""
        if self._voice_control_enabled and self._is_scrolling:
            self.stop_scrolling()
            self.voice_activity_changed.emit(False)

    def _add_bottom_padding(self):
        """Add padding to bottom of content."""
        viewport_height = self.height()
        padding_height = viewport_height // 2  # Half screen height

        js_code = f"""
        var style = document.createElement('style');
        style.textContent = `
            body {{
                padding-bottom: {padding_height}px !important;
            }}
        `;
        document.head.appendChild(style);
        """
        self.web_view.page().runJavaScript(js_code)

    def capture_reading_state(self) -> dict:
        """Capture the current reading state for restoration.

        Returns:
            Dictionary containing reading state including:
            - progress: Current progress (0.0 to 1.0)
            - scroll_position: Absolute scroll position
            - is_playing: Whether currently scrolling
            - speed: Current scroll speed
            - section_index: Current section index
        """
        # Get current progress from scroll controller
        current_progress = 0.0
        if hasattr(self.scroll_controller, "get_progress"):
            current_progress = self.scroll_controller.get_progress()
        elif self.content_height > 0:
            # Calculate progress manually if method not available
            current_progress = (
                self.scroll_controller._scroll_position / self.content_height
            )

        return {
            "progress": current_progress,
            "scroll_position": self.scroll_controller._scroll_position,
            "is_playing": self._is_scrolling,
            "speed": self.scroll_controller.get_speed(),
            "section_index": self._current_section_index,
            "elapsed_time": self.reading_metrics.get_elapsed_time(),
        }

    def restore_reading_state(self, state: dict) -> None:
        """Restore reading state after content reload.

        Args:
            state: Dictionary containing reading state from capture_reading_state
        """
        # Restore scroll speed
        if "speed" in state:
            self.set_scroll_speed(state["speed"])

        # Restore section index
        if "section_index" in state:
            self._current_section_index = state["section_index"]

        # Restore scroll position - wait for content to load first
        def restore_position():
            if "progress" in state and self.content_height > 0:
                # Use progress-based restoration for better accuracy
                self._jump_to_progress(state["progress"])
            elif "scroll_position" in state:
                # Fallback to absolute position
                self.web_view.page().runJavaScript(
                    f"window.scrollTo(0, {int(state['scroll_position'])})"
                )

            # Update internal state
            self._update_progress_display()

            # Resume scrolling if it was playing
            if state.get("is_playing", False):
                QTimer.singleShot(100, self.start_scrolling)

        # Wait for content to be fully loaded before restoring position
        QTimer.singleShot(200, restore_position)

    def reload_content_with_state(self, html_content: str) -> None:
        """Reload content while preserving reading state.

        Args:
            html_content: New HTML content to display
        """
        # Capture current state before reload
        state = self.capture_reading_state()

        # Stop scrolling during reload
        was_scrolling = self._is_scrolling
        if was_scrolling:
            self.stop_scrolling()

        # Clear web view cache to ensure fresh content
        self.web_view.page().profile().clearHttpCache()

        # Force reload by using a different base URL each time
        import time

        from PyQt6.QtCore import QUrl

        # Use timestamp to ensure unique URL and bypass any caching
        base_url = QUrl(f"local://reload/{int(time.time() * 1000)}")
        self.web_view.setHtml(html_content, base_url)

        # Update current content
        self.current_content = html_content

        # Restore state after content loads
        def on_load_finished(ok):
            if ok:
                # Re-parse content to update sections
                self.content_loader.load_text(html_content, is_html=True)
                # Restore reading state
                self.restore_reading_state(state)
                # Show notification that content was updated
                self._show_reload_notification()

        # Connect one-time to load finished signal
        self.web_view.loadFinished.connect(
            on_load_finished, Qt.ConnectionType.SingleShotConnection
        )

    def _show_reload_notification(self) -> None:
        """Show a subtle notification that content was reloaded."""
        # Create notification overlay
        from PyQt6.QtCore import QPropertyAnimation, QRect
        from PyQt6.QtWidgets import QLabel

        notification = QLabel("Content updated", self)
        notification.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 120, 212, 200);
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        notification.adjustSize()

        # Position at top-right corner
        x = self.width() - notification.width() - 20
        notification.move(x, -notification.height())
        notification.show()

        # Animate slide in
        slide_in = QPropertyAnimation(notification, b"geometry")
        slide_in.setDuration(300)
        slide_in.setStartValue(
            QRect(
                x, -notification.height(), notification.width(), notification.height()
            )
        )
        slide_in.setEndValue(QRect(x, 20, notification.width(), notification.height()))

        # Auto-hide after 2 seconds
        def hide_notification():
            slide_out = QPropertyAnimation(notification, b"geometry")
            slide_out.setDuration(300)
            slide_out.setStartValue(notification.geometry())
            slide_out.setEndValue(
                QRect(
                    x,
                    -notification.height(),
                    notification.width(),
                    notification.height(),
                )
            )
            slide_out.finished.connect(notification.deleteLater)
            slide_out.start()

        QTimer.singleShot(2000, hide_notification)
        slide_in.start()
