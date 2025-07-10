"""Teleprompter widget for displaying and scrolling text."""

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from . import config
from .style_manager import StyleManager


class ProgressBar(QWidget):
    """Custom progress bar for teleprompter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0  # 0.0 to 1.0
        self.setFixedHeight(4)
        self.setStyleSheet(StyleManager.get_progress_bar_stylesheet())

    def set_progress(self, progress: float):
        """Set progress value (0.0 to 1.0)."""
        self.progress = max(0.0, min(1.0, progress))
        self.update()

    def paintEvent(self, event):
        """Paint the progress bar."""
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


class ReadingTimeEstimator:
    """Estimates reading time and provides navigation information."""

    def __init__(self):
        self.words_per_minute = 150  # Average reading speed
        self.total_words = 0
        self.content_sections = []

    def analyze_content(self, html_content: str) -> dict:
        """Analyze content for reading time and sections."""
        import re

        # Extract text content (simple approach)
        text_content = re.sub(r"<[^>]+>", " ", html_content)
        text_content = re.sub(r"\s+", " ", text_content).strip()

        # Count words
        self.total_words = len(text_content.split()) if text_content else 0

        # Estimate reading time
        reading_time_minutes = self.total_words / self.words_per_minute

        # Find sections (headers)
        sections = re.findall(
            r"<h[1-6][^>]*>(.*?)</h[1-6]>", html_content, re.IGNORECASE
        )
        self.content_sections = [
            re.sub(r"<[^>]+>", "", section).strip() for section in sections
        ]

        return {
            "total_words": self.total_words,
            "estimated_minutes": reading_time_minutes,
            "sections": self.content_sections,
        }

    def get_reading_progress(
        self, current_position: float, content_height: float
    ) -> dict:
        """Get current reading progress information."""
        if content_height <= 0:
            return {"progress": 0.0, "time_remaining": 0.0}

        progress = min(1.0, current_position / content_height)
        words_read = int(self.total_words * progress)
        words_remaining = self.total_words - words_read
        time_remaining = words_remaining / self.words_per_minute

        return {
            "progress": progress,
            "words_read": words_read,
            "words_remaining": words_remaining,
            "time_remaining": time_remaining,
        }


class TeleprompterWidget(QWidget):
    """Custom widget for teleprompter display and control."""

    speed_changed = pyqtSignal(float)
    voice_activity_changed = pyqtSignal(bool)
    progress_changed = pyqtSignal(float)  # New signal for progress updates
    reading_stats_changed = pyqtSignal(dict)  # New signal for reading statistics

    def __init__(self, parent=None):
        """Initialize the teleprompter widget."""
        super().__init__(parent)
        self.current_speed = config.DEFAULT_SPEED
        self.current_font_size = config.DEFAULT_FONT_SIZE
        self.is_playing = False
        self.content_height = 0
        self.current_position = 0
        self.current_content = ""

        # Voice control settings
        self.voice_control_enabled = False
        self.voice_detector = None

        # Phase 3: Progress tracking and focus management
        self.reading_estimator = ReadingTimeEstimator()
        self.show_progress = True
        self.auto_hide_cursor = True

        # Phase 4.3: Responsive design
        self.device_category = "desktop"  # Will be set by responsive setup

        # Cursor auto-hide timer
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self._hide_cursor)
        self.cursor_timer.setSingleShot(True)

        self._setup_ui()
        self._setup_animation()
        self._setup_focus_management()
        self._setup_responsive_layout()
        self._setup_responsive_layout()

    def _setup_ui(self):
        """Set up the user interface with progress tracking."""
        self.setStyleSheet(StyleManager.get_main_window_stylesheet())

        # Make widget focusable
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Progress bar at top
        self.progress_bar = ProgressBar()
        layout.addWidget(self.progress_bar)

        # Web view for displaying HTML content
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet(StyleManager.get_web_view_stylesheet())
        layout.addWidget(self.web_view)

        # Reading info overlay (bottom)
        self.info_overlay = QWidget()
        self.info_overlay.setStyleSheet(
            StyleManager.get_teleprompter_info_overlay_stylesheet()
        )
        self.info_overlay.setFixedHeight(40)

        info_layout = QHBoxLayout(self.info_overlay)
        info_layout.setContentsMargins(12, 8, 12, 8)

        self.reading_info_label = QLabel("Ready to read")
        self.reading_info_label.setStyleSheet(
            StyleManager.get_teleprompter_info_label_stylesheet()
        )
        info_layout.addWidget(self.reading_info_label)

        info_layout.addStretch()

        self.progress_label = QLabel("0%")
        self.progress_label.setStyleSheet(
            StyleManager.get_teleprompter_info_label_stylesheet()
        )
        info_layout.addWidget(self.progress_label)

        layout.addWidget(self.info_overlay)

        # Connect to page load finished signal
        self.web_view.loadFinished.connect(self._on_content_loaded)

    def _setup_animation(self):
        """Set up the scrolling animation timer."""
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self._scroll_step)
        self.scroll_timer.setInterval(int(1000 / config.SCROLL_FPS))  # 60 FPS

    def load_content(self, html_content: str):
        """Load HTML content into the web view."""
        self.current_content = html_content
        self.web_view.setHtml(html_content)
        self.current_position = 0

    def _on_content_loaded(self, ok: bool):
        """Handle when content is loaded and analyze for progress tracking."""
        if ok:
            # Get content height
            self.web_view.page().runJavaScript(
                "document.body.scrollHeight",
                lambda height: setattr(self, "content_height", height),
            )

            # Analyze content for reading statistics
            if self.current_content:
                stats = self.reading_estimator.analyze_content(self.current_content)
                self.reading_stats_changed.emit(stats)
                self._update_reading_info(stats)

            # Configure scrolling behavior and progress tracking
            self.web_view.page().runJavaScript("""
                // Allow manual scrolling via mouse wheel, but hide scrollbar
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';

                // Hide scrollbars while keeping scroll functionality
                var style = document.createElement('style');
                style.textContent = `
                    /* Hide scrollbar for webkit browsers (Chrome, Safari, Edge) */
                    ::-webkit-scrollbar {
                        width: 0px;
                        background: transparent;
                    }

                    /* Hide scrollbar for Firefox */
                    html {
                        scrollbar-width: none;
                    }

                    /* Ensure body and html can still scroll */
                    body, html {
                        overflow: auto;
                        -ms-overflow-style: none; /* IE and Edge */
                    }
                `;
                document.head.appendChild(style);

                // Detect mouse wheel scrolling and pause auto-scroll
                window.addEventListener('wheel', function(e) {
                    // Signal to Qt that user is manually scrolling
                    window.userIsScrolling = true;

                    // Clear any existing timeout
                    if (window.scrollTimeout) {
                        clearTimeout(window.scrollTimeout);
                    }

                    // Set flag back to false after a brief delay
                    window.scrollTimeout = setTimeout(function() {
                        window.userIsScrolling = false;
                    }, 100);
                }, { passive: true });

                // Prevent touch scrolling (for mobile devices)
                window.addEventListener('touchmove', function(e) { e.preventDefault(); }, { passive: false });

                // Prevent keyboard scrolling but allow Qt to handle up/down arrows for speed control
                window.addEventListener('keydown', function(e) {
                    // Prevent space, page up/down, home/end, all arrow keys from scrolling the page
                    // This ensures up/down arrows reach Qt for speed control, not page scrolling
                    if([32, 33, 34, 35, 36, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
                        e.preventDefault();
                    }
                }, false);

                // Track manual scroll position for auto-scroll resume
                window.addEventListener('scroll', function(e) {
                    // This will be used to sync manual scroll position with auto-scroll
                    window.manualScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
                }, false);
            """)
            # Apply current font size
            if self.current_font_size != config.DEFAULT_FONT_SIZE:
                self.set_font_size(self.current_font_size)

            # Add responsive bottom padding for better reading experience
            self._add_bottom_padding()

    def _scroll_step(self):
        """Perform one scroll step."""
        if not self.is_playing:
            return

        # Check if user is manually scrolling with mouse wheel
        self.web_view.page().runJavaScript(
            "window.userIsScrolling", self._handle_user_scrolling
        )

        # Check if user has manually scrolled and update our position
        self.web_view.page().runJavaScript(
            "window.manualScrollPosition || window.pageYOffset || document.documentElement.scrollTop",
            self._update_position_from_manual_scroll,
        )

        # Calculate scroll amount based on speed
        # Base speed: 100 pixels per second at 1x speed
        pixels_per_frame = (100 * self.current_speed) / config.SCROLL_FPS

        self.current_position += pixels_per_frame

        # Check if we've reached the end
        if self.current_position >= self.content_height - self.height():
            self.pause()
            self.current_position = self.content_height - self.height()

        # Scroll to position
        self.web_view.page().runJavaScript(
            f"window.scrollTo(0, {int(self.current_position)})"
        )

        # Update progress display during scrolling
        self._update_progress_display()

    def _handle_user_scrolling(self, is_user_scrolling):
        """Handle user wheel scrolling by pausing auto-scroll."""
        if is_user_scrolling and self.is_playing:
            self.pause()
            # Update UI button text if parent app has the method
            parent = self.parent()
            while parent:
                if hasattr(parent, "play_button"):
                    parent.play_button.setText("Play")
                    break
                parent = parent.parent()

    def _update_position_from_manual_scroll(self, manual_position):
        """Update auto-scroll position based on manual scroll."""
        if (
            manual_position is not None
            and abs(manual_position - self.current_position) > 10
        ):
            # User has manually scrolled, update our position to match
            self.current_position = manual_position

    def play(self):
        """Start scrolling."""
        # Sync our position with current manual scroll position before starting
        self.web_view.page().runJavaScript(
            "window.pageYOffset || document.documentElement.scrollTop",
            lambda pos: setattr(self, "current_position", pos or 0),
        )
        self.is_playing = True
        self.scroll_timer.start()

    def pause(self):
        """Pause scrolling."""
        self.is_playing = False
        self.scroll_timer.stop()

    def toggle_playback(self):
        """Toggle between play and pause."""
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def reset(self):
        """Reset scroll position to the beginning."""
        self.current_position = 0
        self.web_view.page().runJavaScript("window.scrollTo(0, 0)")
        self._update_progress_display()

    def set_speed(self, speed: float):
        """Set the scrolling speed."""
        self.current_speed = max(config.MIN_SPEED, min(speed, config.MAX_SPEED))
        self.speed_changed.emit(self.current_speed)

    def adjust_speed(self, delta: float):
        """Adjust speed by delta amount."""
        self.set_speed(self.current_speed + delta)

    def set_voice_detector(self, voice_detector):
        """Set the voice detector instance and connect signals."""
        self.voice_detector = voice_detector
        if voice_detector:
            voice_detector.voice_started.connect(self._on_voice_started)
            voice_detector.voice_stopped.connect(self._on_voice_stopped)

    def enable_voice_control(self, enabled: bool):
        """Enable or disable voice-controlled scrolling."""
        self.voice_control_enabled = enabled

    def _on_voice_started(self):
        """Handle voice activity start."""
        if self.voice_control_enabled and not self.is_playing:
            self.play()
            self.voice_activity_changed.emit(True)

    def _on_voice_stopped(self):
        """Handle voice activity stop."""
        if self.voice_control_enabled and self.is_playing:
            self.pause()
            self.voice_activity_changed.emit(False)

    def ensure_focus(self):
        """Ensure the widget has focus for keyboard events."""
        self.setFocus()
        self.activateWindow()

    def mousePressEvent(self, event):
        """Handle mouse press to regain focus and sync scroll position."""
        self.setFocus()
        # Sync our position with the current scroll position when user clicks
        self.web_view.page().runJavaScript(
            "window.pageYOffset || document.documentElement.scrollTop",
            lambda pos: setattr(self, "current_position", pos or 0),
        )
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key.Key_Space:
            self.toggle_playback()
            event.accept()
        elif event.key() == Qt.Key.Key_R:
            self.reset()
            event.accept()
        elif event.key() == Qt.Key.Key_Up:
            self.adjust_speed(config.SPEED_INCREMENT)
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            self.adjust_speed(-config.SPEED_INCREMENT)
            event.accept()
        elif event.key() == Qt.Key.Key_Left:
            # Previous section
            self.navigate_to_previous_section()
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            # Next section
            self.navigate_to_next_section()
            event.accept()
        elif (
            event.key() == Qt.Key.Key_H
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            # Ctrl+H: Toggle progress display
            self.set_progress_visibility(not self.show_progress)
            event.accept()
        elif (
            event.key() == Qt.Key.Key_C
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            # Ctrl+C: Toggle cursor auto-hide
            self.auto_hide_cursor = not self.auto_hide_cursor
            if not self.auto_hide_cursor:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.cursor_timer.stop()
            event.accept()
        elif event.key() == Qt.Key.Key_Home:
            # Jump to beginning
            self.jump_to_progress(0.0)
            event.accept()
        elif event.key() == Qt.Key.Key_End:
            # Jump to end
            self.jump_to_progress(1.0)
            event.accept()
        else:
            super().keyPressEvent(event)

    def set_font_size(self, size: int):
        """Set the font size for the teleprompter text with enhanced typography."""
        self.current_font_size = size

        # Determine optimal line height and letter spacing based on size
        line_height = self._calculate_optimal_line_height(size)
        letter_spacing = self._calculate_optimal_letter_spacing(size)

        # Update the font size via JavaScript with enhanced typography
        js_code = f"""
        // Create or update a style element for font size overrides
        var styleId = 'teleprompter-font-size-override';
        var styleEl = document.getElementById(styleId);
        if (!styleEl) {{
            styleEl = document.createElement('style');
            styleEl.id = styleId;
            document.head.appendChild(styleEl);
        }}

        // Calculate relative sizes and optimal typography settings
        var baseFontSize = {size};
        var lineHeight = {line_height};
        var letterSpacing = '{letter_spacing}';

        styleEl.textContent = `
            body {{
                font-size: ${{baseFontSize}}px !important;
                line-height: ${{lineHeight}} !important;
                letter-spacing: ${{letterSpacing}} !important;
            }}
            p {{
                font-size: ${{baseFontSize}}px !important;
                line-height: ${{lineHeight}} !important;
            }}
            li {{
                font-size: ${{baseFontSize}}px !important;
                line-height: ${{lineHeight}} !important;
            }}
            a {{
                font-size: ${{baseFontSize}}px !important;
            }}
            h1 {{
                font-size: ${{baseFontSize * 2.5}}px !important;
                line-height: 1.2 !important;
                letter-spacing: -0.02em !important;
            }}
            h2 {{
                font-size: ${{baseFontSize * 2.0}}px !important;
                line-height: 1.2 !important;
                letter-spacing: -0.015em !important;
            }}
            h3 {{
                font-size: ${{baseFontSize * 1.7}}px !important;
                line-height: 1.3 !important;
                letter-spacing: -0.01em !important;
            }}
            h4 {{
                font-size: ${{baseFontSize * 1.5}}px !important;
                line-height: 1.3 !important;
            }}
            h5 {{
                font-size: ${{baseFontSize * 1.3}}px !important;
                line-height: 1.4 !important;
            }}
            h6 {{
                font-size: ${{baseFontSize * 1.1}}px !important;
                line-height: 1.4 !important;
            }}
        `;
        """
        self.web_view.page().runJavaScript(js_code)

    def _calculate_optimal_line_height(self, font_size: int) -> float:
        """Calculate optimal line height based on font size."""
        # Smaller fonts need more line height, larger fonts need less
        if font_size <= 20:
            return 1.7
        elif font_size <= 30:
            return 1.6
        elif font_size <= 40:
            return 1.5
        else:
            return 1.4

    def _calculate_optimal_letter_spacing(self, font_size: int) -> str:
        """Calculate optimal letter spacing based on font size."""
        # Larger fonts benefit from tighter letter spacing
        if font_size <= 20:
            return "0.02em"
        elif font_size <= 30:
            return "0.01em"
        elif font_size <= 40:
            return "0.005em"
        else:
            return "-0.01em"

    def _setup_focus_management(self):
        """Set up focus management and cursor auto-hide functionality."""
        # Mouse tracking for cursor auto-hide
        self.setMouseTracking(True)
        self.web_view.setMouseTracking(True)

        # Install event filter to track mouse movement
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle events for cursor auto-hide and focus management."""
        if event.type() == event.Type.MouseMove and self.auto_hide_cursor:
            # Show cursor and restart timer
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.cursor_timer.start(3000)  # Hide after 3 seconds of inactivity

        return super().eventFilter(obj, event)

    def _hide_cursor(self):
        """Hide the cursor during reading."""
        if self.auto_hide_cursor:
            self.setCursor(Qt.CursorShape.BlankCursor)

    def set_progress_visibility(self, visible: bool):
        """Set whether progress indicators are visible."""
        self.show_progress = visible
        self.progress_bar.setVisible(visible)
        self.info_overlay.setVisible(visible)

    def jump_to_progress(self, progress: float):
        """Jump to a specific progress point (0.0 to 1.0)."""
        if self.content_height > 0:
            target_position = progress * self.content_height
            self.current_position = max(
                0, min(target_position, self.content_height - self.height())
            )
            self.web_view.page().runJavaScript(
                f"window.scrollTo(0, {int(self.current_position)})"
            )
            self._update_progress_display()

    def navigate_to_section(self, section_index: int):
        """Navigate to a specific section/chapter."""
        if not self.reading_estimator.content_sections or section_index < 0:
            return

        if section_index >= len(self.reading_estimator.content_sections):
            return

        section_title = self.reading_estimator.content_sections[section_index]

        # Find the section in the HTML content and scroll to it
        js_code = f"""
        var elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        var targetElement = null;

        for (var i = 0; i < elements.length; i++) {{
            var textContent = elements[i].textContent || elements[i].innerText;
            if (textContent.trim() === "{section_title}") {{
                targetElement = elements[i];
                break;
            }}
        }}

        if (targetElement) {{
            var rect = targetElement.getBoundingClientRect();
            var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            var targetPosition = rect.top + scrollTop - 50; // 50px offset from top
            window.scrollTo(0, Math.max(0, targetPosition));
            targetPosition; // Return the position
        }} else {{
            -1; // Section not found
        }}
        """

        self.web_view.page().runJavaScript(
            js_code, self._on_section_navigation_complete
        )

    def _on_section_navigation_complete(self, position):
        """Handle completion of section navigation."""
        if position >= 0:
            self.current_position = position
            self._update_progress_display()

    def navigate_to_next_section(self):
        """Navigate to the next section."""
        if not self.reading_estimator.content_sections:
            return

        # Find current section based on scroll position
        current_section = self._get_current_section_index()
        if current_section < len(self.reading_estimator.content_sections) - 1:
            self.navigate_to_section(current_section + 1)

    def navigate_to_previous_section(self):
        """Navigate to the previous section."""
        if not self.reading_estimator.content_sections:
            return

        # Find current section based on scroll position
        current_section = self._get_current_section_index()
        if current_section > 0:
            self.navigate_to_section(current_section - 1)

    def _get_current_section_index(self) -> int:
        """Get the index of the current section based on scroll position."""
        # This is a simplified approach - in a real implementation,
        # you might want to track section positions more precisely
        progress = (
            self.current_position / self.content_height
            if self.content_height > 0
            else 0
        )
        section_count = len(self.reading_estimator.content_sections)

        if section_count == 0:
            return 0

        # Estimate section index based on progress
        estimated_index = int(progress * section_count)
        return min(estimated_index, section_count - 1)

    def get_section_list(self) -> list:
        """Get the list of sections/chapters for navigation."""
        return self.reading_estimator.content_sections.copy()

    def get_current_section_info(self) -> dict:
        """Get information about the current section."""
        sections = self.reading_estimator.content_sections
        if not sections:
            return {"index": -1, "title": "", "total": 0}

        current_index = self._get_current_section_index()
        return {
            "index": current_index,
            "title": sections[current_index] if current_index < len(sections) else "",
            "total": len(sections),
        }

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

    def _update_progress_display(self):
        """Update progress bar and information."""
        if self.content_height > 0:
            progress_info = self.reading_estimator.get_reading_progress(
                self.current_position, self.content_height
            )

            # Update progress bar
            self.progress_bar.set_progress(progress_info["progress"])

            # Update progress label
            progress_percent = int(progress_info["progress"] * 100)
            self.progress_label.setText(f"{progress_percent}%")

            # Emit progress signal
            self.progress_changed.emit(progress_info["progress"])

            # Update reading stats signal
            self.reading_stats_changed.emit(progress_info)

    def _setup_responsive_layout(self):
        """Set up responsive layout management for different screen sizes."""
        # Get initial screen size to determine layout
        screen = self.window().screen()
        screen_size = screen.size()

        # Determine device category based on screen width
        self.device_category = self._get_device_category(screen_size.width())

        # Apply responsive styles based on device category
        self._apply_responsive_styles()

        # Connect to screen change signals for dynamic updates
        screen.geometryChanged.connect(self._on_screen_changed)

    def _get_device_category(self, width: int) -> str:
        """Determine device category based on screen width."""
        if width <= config.BREAKPOINTS["mobile"]:
            return "mobile"
        elif width <= config.BREAKPOINTS["tablet"]:
            return "tablet"
        elif width <= config.BREAKPOINTS["desktop"]:
            return "desktop"
        else:
            return "large_desktop"

    def _apply_responsive_styles(self):
        """Apply device-specific styles and layouts."""
        if self.device_category == "mobile":
            self._apply_mobile_layout()
        elif self.device_category == "tablet":
            self._apply_tablet_layout()
        else:
            self._apply_desktop_layout()

    def _apply_mobile_layout(self):
        """Apply mobile-optimized layout."""
        # Increase touch target sizes
        self.progress_bar.setFixedHeight(8)
        self.info_overlay.setFixedHeight(60)

        # Update font sizes for mobile
        mobile_css = StyleManager.get_mobile_info_overlay_stylesheet()
        self.info_overlay.setStyleSheet(self.info_overlay.styleSheet() + mobile_css)

    def _apply_tablet_layout(self):
        """Apply tablet-optimized layout."""
        # Moderate touch targets
        self.progress_bar.setFixedHeight(6)
        self.info_overlay.setFixedHeight(50)

        # Tablet-specific styling
        tablet_css = StyleManager.get_tablet_info_overlay_stylesheet()
        self.info_overlay.setStyleSheet(self.info_overlay.styleSheet() + tablet_css)

    def _apply_desktop_layout(self):
        """Apply desktop-optimized layout."""
        # Standard sizes for desktop
        self.progress_bar.setFixedHeight(4)
        self.info_overlay.setFixedHeight(40)

        # Desktop styling (already applied by default)
        pass

    def _on_screen_changed(self):
        """Handle screen size changes for responsive updates."""
        screen = self.window().screen()
        new_width = screen.size().width()
        new_device_category = self._get_device_category(new_width)

        if new_device_category != self.device_category:
            self.device_category = new_device_category
            self._apply_responsive_styles()

    def _add_bottom_padding(self):
        """Add padding to bottom of content so text ends halfway in middle of screen."""
        # Calculate viewport height for responsive padding
        viewport_height = self.height()
        padding_height = viewport_height // 2  # Half screen height

        # Apply padding via JavaScript to the web content
        js_code = f"""
        // Add responsive bottom padding
        var style = document.createElement('style');
        style.textContent = `
            body {{
                padding-bottom: {padding_height}px !important;
            }}
        `;
        document.head.appendChild(style);
        """

        self.web_view.page().runJavaScript(js_code)
