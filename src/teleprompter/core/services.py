"""Business logic services for the teleprompter application.

This module contains services that encapsulate business logic,
separated from UI concerns.
"""

import time

from . import config
from .protocols import (
    ContentParserProtocol,
    ReadingMetricsProtocol,
    ScrollControllerProtocol,
)


class ReadingMetricsService(ReadingMetricsProtocol):
    """Service for calculating reading metrics and statistics."""

    def __init__(self):
        self._start_time: float | None = None
        self._pause_time: float | None = None
        self._total_pause_duration: float = 0.0
        self._word_count: int = 0
        self._current_progress: float = 0.0
        self._base_wpm: float = config.DEFAULT_WPM

    def set_word_count(self, count: int) -> None:
        """Set the total word count."""
        self._word_count = count

    def set_progress(self, progress: float) -> None:
        """Update current reading progress (0.0-1.0)."""
        self._current_progress = max(0.0, min(1.0, progress))

    def start_reading(self) -> None:
        """Mark the start of reading session."""
        self._start_time = time.time()
        self._pause_time = None
        self._total_pause_duration = 0.0

    def pause_reading(self) -> None:
        """Mark reading as paused."""
        if self._start_time and not self._pause_time:
            self._pause_time = time.time()

    def resume_reading(self) -> None:
        """Resume reading from pause."""
        if self._pause_time:
            self._total_pause_duration += time.time() - self._pause_time
            self._pause_time = None

    def stop_reading(self) -> None:
        """Stop the reading session."""
        self._start_time = None
        self._pause_time = None

    def calculate_reading_time(self, word_count: int, wpm: float) -> float:
        """Calculate estimated reading time in seconds."""
        if word_count <= 0 or wpm <= 0:
            return 0.0
        return (word_count / wpm) * 60.0

    def calculate_words_per_minute(self, speed: float) -> float:
        """Calculate effective words per minute based on scroll speed."""
        return self._base_wpm * speed

    def get_elapsed_time(self) -> float:
        """Get elapsed reading time in seconds (excluding pauses)."""
        if not self._start_time:
            return 0.0

        current_time = self._pause_time if self._pause_time else time.time()
        total_time = current_time - self._start_time - self._total_pause_duration
        return max(0.0, total_time)

    def get_remaining_time(self) -> float:
        """Get remaining reading time in seconds."""
        if self._word_count <= 0 or self._current_progress >= 1.0:
            return 0.0

        words_read = int(self._word_count * self._current_progress)
        words_remaining = self._word_count - words_read

        # Calculate average reading speed based on elapsed time
        elapsed = self.get_elapsed_time()
        if elapsed > 0 and words_read > 0:
            actual_wpm = (words_read / elapsed) * 60.0
            return self.calculate_reading_time(words_remaining, actual_wpm)
        else:
            # Use default WPM if no reading history
            return self.calculate_reading_time(words_remaining, self._base_wpm)

    def get_average_wpm(self) -> float:
        """Get the average words per minute for the current session."""
        elapsed = self.get_elapsed_time()
        if elapsed <= 0 or self._word_count <= 0:
            return 0.0

        words_read = int(self._word_count * self._current_progress)
        return (words_read / elapsed) * 60.0 if words_read > 0 else 0.0

    def format_time(self, seconds: float) -> str:
        """Format seconds into a readable time string."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"


class ScrollController(ScrollControllerProtocol):
    """Controller for managing scroll behavior and state."""

    def __init__(self):
        self._is_scrolling: bool = False
        self._is_paused: bool = False
        self._speed: float = 1.0
        self._progress: float = 0.0
        self._viewport_height: int = 0
        self._content_height: int = 0
        self._scroll_position: int = 0

    def set_viewport_dimensions(
        self, viewport_height: int, content_height: int
    ) -> None:
        """Update viewport dimensions."""
        self._viewport_height = viewport_height
        self._content_height = content_height

    def start_scrolling(self) -> None:
        """Start scrolling."""
        self._is_scrolling = True
        self._is_paused = False

    def stop_scrolling(self) -> None:
        """Stop scrolling completely."""
        self._is_scrolling = False
        self._is_paused = False
        self._scroll_position = 0
        self._progress = 0.0

    def pause_scrolling(self) -> None:
        """Pause scrolling (can be resumed)."""
        self._is_paused = True

    def resume_scrolling(self) -> None:
        """Resume scrolling from pause."""
        if self._is_scrolling:
            self._is_paused = False

    def toggle_scrolling(self) -> None:
        """Toggle between play and pause."""
        if not self._is_scrolling:
            self.start_scrolling()
        elif self._is_paused:
            self.resume_scrolling()
        else:
            self.pause_scrolling()

    def set_speed(self, speed: float) -> None:
        """Set scrolling speed (0.05 to 5.0)."""
        self._speed = max(config.MIN_SPEED, min(config.MAX_SPEED, speed))

    def adjust_speed(self, delta: float) -> None:
        """Adjust speed by delta amount."""
        self.set_speed(self._speed + delta)

    def get_speed(self) -> float:
        """Get current scrolling speed."""
        return self._speed

    def is_scrolling(self) -> bool:
        """Check if currently scrolling (not paused)."""
        return self._is_scrolling and not self._is_paused

    def is_active(self) -> bool:
        """Check if scrolling is active (may be paused)."""
        return self._is_scrolling

    def get_progress(self) -> float:
        """Get current progress (0.0-1.0)."""
        return self._progress

    def jump_to_position(self, position: float) -> None:
        """Jump to specific position (0.0-1.0)."""
        self._progress = max(0.0, min(1.0, position))
        if self._content_height > self._viewport_height:
            max_scroll = self._content_height - self._viewport_height
            self._scroll_position = int(self._progress * max_scroll)

    def update_scroll_position(self, position: int) -> None:
        """Update scroll position and calculate progress."""
        self._scroll_position = position
        if self._content_height > self._viewport_height:
            max_scroll = self._content_height - self._viewport_height
            self._progress = position / max_scroll if max_scroll > 0 else 0.0
        else:
            self._progress = 1.0

    def calculate_next_position(self, delta_time: float) -> int:
        """Calculate next scroll position based on speed and time delta."""
        if not self.is_scrolling():
            return self._scroll_position

        # Base scroll rate (pixels per second at speed 1.0)
        base_rate = config.BASE_SCROLL_RATE
        pixels_per_second = base_rate * self._speed

        # Calculate position change
        position_delta = pixels_per_second * delta_time
        new_position = self._scroll_position + position_delta

        # Clamp to valid range
        max_scroll = max(0, self._content_height - self._viewport_height)
        new_position = max(0, min(max_scroll, new_position))

        return int(new_position)

    def has_reached_end(self) -> bool:
        """Check if scrolling has reached the end."""
        return (
            self._progress >= 0.99
        )  # Use 0.99 to account for floating point precision


class ContentManager:
    """Manager for handling text and markdown content operations."""

    def __init__(self, parser: ContentParserProtocol):
        self._parser = parser
        self._current_content: str = ""
        self._parsed_content: str = ""
        self._word_count: int = 0
        self._sections: list[tuple[int, str]] = []  # (line_number, header_text)

    def load_content(self, content: str) -> None:
        """Load and process new content."""
        self._current_content = content
        self._parsed_content = self._parser.parse(content)
        self._word_count = self._parser.get_word_count(content)
        self._extract_sections()

    def get_parsed_content(self) -> str:
        """Get the parsed HTML content."""
        return self._parsed_content

    def get_word_count(self) -> int:
        """Get total word count."""
        return self._word_count

    def get_sections(self) -> list[tuple[int, str]]:
        """Get list of sections (line number, header text)."""
        return self._sections.copy()

    def _extract_sections(self) -> None:
        """Extract section headers from content."""
        self._sections.clear()
        lines = self._current_content.split("\n")

        for i, line in enumerate(lines):
            # Check for markdown headers
            if line.strip().startswith("#"):
                # Extract header text
                header_text = line.strip().lstrip("#").strip()
                if header_text:
                    self._sections.append((i, header_text))

    def find_section_at_progress(self, progress: float) -> int | None:
        """Find section index at given progress (0.0-1.0)."""
        if not self._sections:
            return None

        total_lines = len(self._current_content.split("\n"))
        current_line = int(progress * total_lines)

        # Find the last section before current line
        for i in range(len(self._sections) - 1, -1, -1):
            if self._sections[i][0] <= current_line:
                return i

        return 0

    def get_section_progress(self, section_index: int) -> float:
        """Get progress value for a specific section."""
        if (
            not self._sections
            or section_index < 0
            or section_index >= len(self._sections)
        ):
            return 0.0

        total_lines = len(self._current_content.split("\n"))
        section_line = self._sections[section_index][0]

        return section_line / total_lines if total_lines > 0 else 0.0


class HtmlContentAnalyzer:
    """Analyzer for extracting information from HTML content."""

    def analyze_html(self, html_content: str) -> dict:
        """Analyze HTML content for word count and sections."""
        import re

        # Extract text content from HTML
        text_content = re.sub(r"<[^>]+>", " ", html_content)
        text_content = re.sub(r"\s+", " ", text_content).strip()

        # Count words
        word_count = len(text_content.split()) if text_content else 0

        # Find sections (headers)
        sections = re.findall(
            r"<h[1-6][^>]*>(.*?)</h[1-6]>", html_content, re.IGNORECASE
        )
        section_titles = [
            re.sub(r"<[^>]+>", "", section).strip() for section in sections
        ]

        return {
            "total_words": word_count,
            "sections": section_titles,
            "text_content": text_content,
        }

    def find_section_in_html(self, html_content: str, section_title: str) -> str:
        """Generate JavaScript to find and scroll to a section."""
        return f"""(function() {{
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
                return targetPosition;
            }} else {{
                return -1; // Section not found
            }}
        }})();"""
