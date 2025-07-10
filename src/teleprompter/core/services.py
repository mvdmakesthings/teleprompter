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
    """Service for calculating reading metrics and statistics.

    This service provides comprehensive reading analytics including time tracking,
    progress monitoring, and words-per-minute calculations. It maintains session
    state to provide accurate metrics for teleprompter usage.

    Attributes:
        _start_time: When the current reading session started.
        _pause_time: When reading was paused (None if not paused).
        _total_pause_duration: Total time spent paused in current session.
        _word_count: Total number of words in the current content.
        _current_progress: Current reading progress (0.0-1.0).
        _base_wpm: Base words per minute for calculations.
    """

    def __init__(self):
        """Initialize the reading metrics service with default values."""
        self._start_time: float | None = None
        self._pause_time: float | None = None
        self._total_pause_duration: float = 0.0
        self._word_count: int = 0
        self._current_progress: float = 0.0
        self._base_wpm: float = config.DEFAULT_WPM

    def set_word_count(self, count: int) -> None:
        """Set the total word count for the current content.

        Args:
            count: Total number of words in the content.

        Raises:
            ValueError: If count is negative.
        """
        if count < 0:
            raise ValueError("Word count cannot be negative")
        self._word_count = count

    def set_progress(self, progress: float) -> None:
        """Update current reading progress.

        Args:
            progress: Reading progress from 0.0 (start) to 1.0 (end).

        Raises:
            ValueError: If progress is not in the range 0.0-1.0.
        """
        if not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        self._current_progress = progress

    def start_reading(self) -> None:
        """Mark the start of a reading session.

        Initializes timing for the current session and resets pause tracking.
        If a session is already active, this resets the timing.
        """
        self._start_time = time.time()
        self._pause_time = None
        self._total_pause_duration = 0.0

    def pause_reading(self) -> None:
        """Mark reading as paused.

        Records the pause time for accurate session duration tracking.
        Safe to call multiple times or when reading is not active.
        """
        if self._start_time and not self._pause_time:
            self._pause_time = time.time()

    def resume_reading(self) -> None:
        """Resume reading from pause.

        Adds the pause duration to the total and clears the pause state.
        Safe to call when reading is not paused.
        """
        if self._pause_time:
            self._total_pause_duration += time.time() - self._pause_time
            self._pause_time = None

    def stop_reading(self) -> None:
        """Stop the reading session.

        Clears all session timing data. The service can be reused for
        a new session by calling start_reading() again.
        """
        self._start_time = None
        self._pause_time = None

    def calculate_reading_time(self, word_count: int, wpm: float) -> float:
        """Calculate estimated reading time in seconds.

        Args:
            word_count: Total number of words in the content.
            wpm: Reading speed in words per minute.

        Returns:
            Estimated reading time in seconds.

        Raises:
            ValueError: If word_count is negative or wpm is not positive.

        Note:
            This calculation assumes steady reading at the specified rate.
            Actual reading time may vary based on content complexity.
        """
        if word_count < 0:
            raise ValueError("Word count cannot be negative")
        if wpm <= 0:
            raise ValueError("Words per minute must be positive")
        if word_count == 0:
            return 0.0
        return (word_count / wpm) * 60.0

    def calculate_words_per_minute(self, speed: float) -> float:
        """Calculate effective words per minute based on scroll speed.

        Args:
            speed: Scroll speed multiplier (1.0 = normal speed).

        Returns:
            Effective words per minute at the given scroll speed.

        Note:
            This method converts scroll speed to reading speed by applying
            the multiplier to the base words per minute rate.
        """
        return self._base_wpm * speed

    def get_elapsed_time(self) -> float:
        """Get elapsed reading time in seconds, excluding pauses.

        Returns:
            Time spent actively reading since the session started.
            Returns 0.0 if no session is active.

        Note:
            This time excludes periods when reading was paused, providing
            an accurate measure of actual reading time.
        """
        if not self._start_time:
            return 0.0

        current_time = self._pause_time if self._pause_time else time.time()
        total_time = current_time - self._start_time - self._total_pause_duration
        return max(0.0, total_time)

    def get_remaining_time(self) -> float:
        """Get remaining reading time in seconds.

        Returns:
            Estimated time remaining to complete the current content,
            based on actual reading speed or default rate.

        Note:
            If reading history is available, this uses the actual measured
            reading speed. Otherwise, it falls back to the base WPM rate.
        """
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
        """Get the average words per minute for the current session.

        Returns:
            Average words per minute based on actual reading progress
            and elapsed time. Returns 0.0 if no meaningful data is available.

        Note:
            This calculation is based on the actual words read and time
            elapsed, providing a real-time measure of reading speed.
        """
        elapsed = self.get_elapsed_time()
        if elapsed <= 0 or self._word_count <= 0:
            return 0.0

        words_read = int(self._word_count * self._current_progress)
        return (words_read / elapsed) * 60.0 if words_read > 0 else 0.0

    def format_time(self, seconds: float) -> str:
        """Format seconds into a human-readable time string.

        Args:
            seconds: Time duration in seconds.

        Returns:
            Formatted time string (e.g., "1m 30s", "2h 15m", "45s").

        Note:
            Times less than 60 seconds show only seconds.
            Times less than 1 hour show minutes and seconds.
            Times 1 hour or more show hours and minutes.
        """
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
    """Controller for managing scroll behavior and state.

    This controller handles scrolling logic including speed control,
    position tracking, and scroll state management. It provides smooth
    scrolling functionality for the teleprompter with precise position
    and progress tracking.

    Attributes:
        _is_scrolling: Whether scrolling is active.
        _is_paused: Whether scrolling is paused.
        _speed: Current scroll speed multiplier.
        _progress: Current scroll progress (0.0-1.0).
        _viewport_height: Height of the visible area.
        _content_height: Total height of the content.
        _scroll_position: Current scroll position in pixels.
    """

    def __init__(self):
        """Initialize the scroll controller with default values."""
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
        """Update viewport dimensions for scroll calculations.

        Args:
            viewport_height: Height of the visible viewport in pixels.
            content_height: Total height of the content in pixels.

        Note:
            These dimensions are used to calculate scroll progress and
            determine maximum scroll positions.
        """
        self._viewport_height = max(0, viewport_height)
        self._content_height = max(0, content_height)

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
        """Set scrolling speed within allowed range.

        Args:
            speed: Scroll speed multiplier (clamped to config.MIN_SPEED - config.MAX_SPEED).

        Note:
            Speed is automatically clamped to the valid range defined by
            configuration constants to ensure stable operation.
        """
        self._speed = max(config.MIN_SPEED, min(config.MAX_SPEED, speed))

    def adjust_speed(self, delta: float) -> None:
        """Adjust speed by delta amount.

        Args:
            delta: Amount to adjust speed by (positive increases, negative decreases).

        Note:
            The resulting speed is automatically clamped to the valid range.
        """
        self.set_speed(self._speed + delta)

    def get_speed(self) -> float:
        """Get current scrolling speed.

        Returns:
            Current scroll speed multiplier.
        """
        return self._speed

    def is_scrolling(self) -> bool:
        """Check if currently scrolling (not paused).

        Returns:
            True if actively scrolling, False if stopped or paused.
        """
        return self._is_scrolling and not self._is_paused

    def is_active(self) -> bool:
        """Check if scrolling is active (may be paused).

        Returns:
            True if scrolling session is active (even if paused), False if stopped.
        """
        return self._is_scrolling

    def get_progress(self) -> float:
        """Get current progress through the content.

        Returns:
            Progress value from 0.0 (start) to 1.0 (end).
        """
        return self._progress

    def jump_to_position(self, position: float) -> None:
        """Jump to specific position in the content.

        Args:
            position: Target position from 0.0 (start) to 1.0 (end).

        Note:
            Position is automatically clamped to the valid range [0.0, 1.0].
            The corresponding scroll position is calculated based on content dimensions.
        """
        self._progress = max(0.0, min(1.0, position))
        if self._content_height > self._viewport_height:
            max_scroll = self._content_height - self._viewport_height
            self._scroll_position = int(self._progress * max_scroll)

    def update_scroll_position(self, position: int) -> None:
        """Update scroll position and calculate progress.

        Args:
            position: Current scroll position in pixels.

        Note:
            This method automatically calculates the progress percentage
            based on the scroll position and content dimensions.
        """
        self._scroll_position = position
        if self._content_height > self._viewport_height:
            max_scroll = self._content_height - self._viewport_height
            self._progress = position / max_scroll if max_scroll > 0 else 0.0
        else:
            self._progress = 1.0

    def calculate_next_position(self, delta_time: float) -> int:
        """Calculate next scroll position based on speed and time delta.

        Args:
            delta_time: Time elapsed since last calculation in seconds.

        Returns:
            Next scroll position in pixels, clamped to valid range.

        Note:
            If not actively scrolling, returns the current position unchanged.
            The calculation uses the base scroll rate from configuration.
        """
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
        """Check if scrolling has reached the end.

        Returns:
            True if scroll progress is at or near the end (>= 0.99).

        Note:
            Uses 0.99 threshold instead of 1.0 to account for floating
            point precision issues in progress calculations.
        """
        return (
            self._progress >= 0.99
        )  # Use 0.99 to account for floating point precision


class ContentManager:
    """Manager for handling text and markdown content operations.

    This class provides content management functionality including loading,
    parsing, and analyzing text content. It maintains parsed content state,
    word counts, and section information for teleprompter display.

    Attributes:
        _parser: Content parser implementation for format conversion.
        _current_content: Raw content text as loaded.
        _parsed_content: Processed content ready for display.
        _word_count: Total number of words in the content.
        _sections: List of content sections with line numbers and titles.
    """

    def __init__(self, parser: ContentParserProtocol):
        """Initialize the content manager.

        Args:
            parser: Content parser implementation for processing text.
        """
        self._parser = parser
        self._current_content: str = ""
        self._parsed_content: str = ""
        self._word_count: int = 0
        self._sections: list[tuple[int, str]] = []  # (line_number, header_text)

    def load_content(self, content: str) -> None:
        """Load and process new content.

        Args:
            content: Raw content text to load and parse.

        Note:
            This method processes the content through the parser,
            calculates word count, and extracts section information.
        """
        self._current_content = content
        self._parsed_content = self._parser.parse(content)
        self._word_count = self._parser.get_word_count(content)
        self._extract_sections()

    def get_parsed_content(self) -> str:
        """Get the parsed HTML content.

        Returns:
            Processed content ready for display in the teleprompter.
        """
        return self._parsed_content

    def get_word_count(self) -> int:
        """Get total word count.

        Returns:
            Number of words in the loaded content.
        """
        return self._word_count

    def get_sections(self) -> list[tuple[int, str]]:
        """Get list of sections with their line numbers and titles.

        Returns:
            List of tuples containing (line_number, header_text) for
            each section found in the content.
        """
        return self._sections.copy()

    def _extract_sections(self) -> None:
        """Extract section headers from markdown content.

        Parses the raw content to find markdown headers (lines starting
        with #) and stores their line numbers and titles for navigation.
        """
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
        """Find section index at given progress through the content.

        Args:
            progress: Progress through content from 0.0 to 1.0.

        Returns:
            Index of the current section, or None if no sections exist.

        Note:
            Returns the index of the last section that starts before
            the current position in the content.
        """
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
        """Get progress value for a specific section.

        Args:
            section_index: Index of the section to get progress for.

        Returns:
            Progress value (0.0-1.0) where the specified section begins.
            Returns 0.0 if the section index is invalid.
        """
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
    """Analyzer for extracting information from HTML content.

    This class provides functionality to analyze HTML content and extract
    useful information such as text content, word counts, and section headers.
    It's particularly useful for processing parsed markdown content in the
    teleprompter application.
    """

    def analyze_html(self, html_content: str) -> dict:
        """Analyze HTML content for word count and sections.

        Args:
            html_content: HTML content to analyze.

        Returns:
            Dictionary containing analysis results:
            - 'total_words': Number of words in the text content
            - 'sections': List of section titles from headers
            - 'text_content': Plain text extracted from HTML

        Note:
            This method strips HTML tags to extract pure text content
            for accurate word counting and section detection.
        """
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
        """Generate JavaScript to find and scroll to a section.

        Args:
            html_content: HTML content to search in (unused in current implementation).
            section_title: Title of the section to find and scroll to.

        Returns:
            JavaScript code that when executed will find the section with
            the specified title and scroll to it with a 50px offset from top.

        Note:
            The returned JavaScript returns the scroll position if successful,
            or -1 if the section is not found.
        """
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
                var scrollTop = window.pageYOffset || (document.documentElement ? document.documentElement.scrollTop : 0);
                var targetPosition = rect.top + scrollTop - 50; // 50px offset from top
                window.scrollTo(0, Math.max(0, targetPosition));
                return targetPosition;
            }} else {{
                return -1; // Section not found
            }}
        }})();"""
