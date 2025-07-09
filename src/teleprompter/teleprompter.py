"""Teleprompter widget for displaying and scrolling text."""

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from . import config


class TeleprompterWidget(QWidget):
    """Custom widget for teleprompter display and control."""

    speed_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        """Initialize the teleprompter widget."""
        super().__init__(parent)
        self.current_speed = config.DEFAULT_SPEED
        self.current_font_size = config.DEFAULT_FONT_SIZE
        self.is_playing = False
        self.content_height = 0
        self.current_position = 0
        self.current_content = ""

        self._setup_ui()
        self._setup_animation()

    def _setup_ui(self):
        """Set up the user interface."""
        self.setStyleSheet(f"background-color: {config.BACKGROUND_COLOR};")

        # Make widget focusable
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Web view for displaying HTML content
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet(f"background-color: {config.BACKGROUND_COLOR};")
        layout.addWidget(self.web_view)

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
        """Handle when content is loaded."""
        if ok:
            # Get content height
            self.web_view.page().runJavaScript(
                "document.body.scrollHeight",
                lambda height: setattr(self, 'content_height', height)
            )
            # Disable manual scrolling
            self.web_view.page().runJavaScript("""
                document.body.style.overflow = 'hidden';
                document.documentElement.style.overflow = 'hidden';
                // Prevent all scroll events
                window.addEventListener('wheel', function(e) { e.preventDefault(); }, { passive: false });
                window.addEventListener('touchmove', function(e) { e.preventDefault(); }, { passive: false });
                window.addEventListener('keydown', function(e) {
                    // Prevent arrow keys, page up/down, home/end from scrolling
                    if([32, 33, 34, 35, 36, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
                        e.preventDefault();
                    }
                }, false);
            """)
            # Apply current font size
            if self.current_font_size != config.DEFAULT_FONT_SIZE:
                self.set_font_size(self.current_font_size)

    def _scroll_step(self):
        """Perform one scroll step."""
        if not self.is_playing:
            return

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

    def play(self):
        """Start scrolling."""
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

    def set_speed(self, speed: float):
        """Set the scrolling speed."""
        self.current_speed = max(config.MIN_SPEED, min(speed, config.MAX_SPEED))
        self.speed_changed.emit(self.current_speed)

    def adjust_speed(self, delta: float):
        """Adjust speed by delta amount."""
        self.set_speed(self.current_speed + delta)


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
        else:
            super().keyPressEvent(event)

    def set_font_size(self, size: int):
        """Set the font size for the teleprompter text."""
        self.current_font_size = size
        # Update the font size via JavaScript with !important to override CSS
        js_code = f"""
        // Create or update a style element for font size overrides
        var styleId = 'teleprompter-font-size-override';
        var styleEl = document.getElementById(styleId);
        if (!styleEl) {{
            styleEl = document.createElement('style');
            styleEl.id = styleId;
            document.head.appendChild(styleEl);
        }}

        // Calculate relative sizes for headers
        var baseFontSize = {size};
        styleEl.textContent = `
            body {{ font-size: ${{baseFontSize}}px !important; }}
            p {{ font-size: ${{baseFontSize}}px !important; }}
            li {{ font-size: ${{baseFontSize}}px !important; }}
            a {{ font-size: ${{baseFontSize}}px !important; }}
            h1 {{ font-size: ${{baseFontSize * 2.5}}px !important; }}
            h2 {{ font-size: ${{baseFontSize * 2.0}}px !important; }}
            h3 {{ font-size: ${{baseFontSize * 1.7}}px !important; }}
            h4 {{ font-size: ${{baseFontSize * 1.5}}px !important; }}
            h5 {{ font-size: ${{baseFontSize * 1.3}}px !important; }}
            h6 {{ font-size: ${{baseFontSize * 1.1}}px !important; }}
        `;
        """
        self.web_view.page().runJavaScript(js_code)
