"""Reading metrics service for tracking reading progress and statistics."""

import time

from teleprompter.core.protocols import ReadingMetricsProtocol
from teleprompter.utils.logging import LoggerMixin


class ReadingMetricsService(ReadingMetricsProtocol, LoggerMixin):
    """Service for calculating reading metrics and statistics.

    This service tracks reading progress, calculates reading time,
    and provides statistics about the reading session.
    """

    def __init__(self, base_wpm: float = 150.0):
        """Initialize the reading metrics service.

        Args:
            base_wpm: Base words per minute for calculations (default: 150)
        """
        self._start_time: float | None = None
        self._pause_time: float | None = None
        self._total_pause_duration: float = 0.0
        self._word_count: int = 0
        self._current_progress: float = 0.0
        self._base_wpm: float = base_wpm

    def set_word_count(self, count: int) -> None:
        """Set the total word count for the current content.

        Args:
            count: Total number of words in the content
        """
        self._word_count = max(0, count)
        self.log_debug(f"Word count set to {self._word_count}")

    def set_progress(self, progress: float) -> None:
        """Update current reading progress.

        Args:
            progress: Reading progress as a value between 0.0 and 1.0
        """
        self._current_progress = max(0.0, min(1.0, progress))

    def start_reading(self) -> None:
        """Mark the start of a reading session.

        Resets pause duration and starts timing.
        """
        self._start_time = time.time()
        self._pause_time = None
        self._total_pause_duration = 0.0
        self.log_info("Reading session started")

    def pause_reading(self) -> None:
        """Mark reading as paused.

        Records the pause time for duration calculation.
        """
        if self._start_time and not self._pause_time:
            self._pause_time = time.time()
            self.log_debug("Reading paused")

    def resume_reading(self) -> None:
        """Resume reading from pause.

        Calculates and adds the pause duration to total pause time.
        """
        if self._pause_time:
            pause_duration = time.time() - self._pause_time
            self._total_pause_duration += pause_duration
            self._pause_time = None
            self.log_debug(f"Reading resumed after {pause_duration:.1f}s pause")

    def stop_reading(self) -> None:
        """Stop the reading session.

        Clears all timing data.
        """
        self._start_time = None
        self._pause_time = None
        self.log_info("Reading session stopped")

    def calculate_reading_time(self, word_count: int, wpm: float) -> float:
        """Calculate estimated reading time in seconds.

        Args:
            word_count: Number of words to read
            wpm: Words per minute reading speed

        Returns:
            Estimated reading time in seconds
        """
        if word_count <= 0 or wpm <= 0:
            return 0.0
        return (word_count / wpm) * 60.0

    def calculate_words_per_minute(self, speed: float) -> float:
        """Calculate effective words per minute based on scroll speed.

        Args:
            speed: Scroll speed multiplier

        Returns:
            Effective words per minute
        """
        return self._base_wpm * speed

    def get_elapsed_time(self) -> float:
        """Get elapsed reading time in seconds (excluding pauses).

        Returns:
            Elapsed time in seconds, excluding pause durations
        """
        if not self._start_time:
            return 0.0

        current_time = self._pause_time if self._pause_time else time.time()
        total_time = current_time - self._start_time - self._total_pause_duration
        return max(0.0, total_time)

    def get_remaining_time(self) -> float:
        """Get estimated remaining reading time in seconds.

        Returns:
            Estimated remaining time based on current progress and reading speed
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
            Average WPM based on actual reading progress
        """
        elapsed = self.get_elapsed_time()
        if elapsed <= 0 or self._word_count <= 0:
            return 0.0

        words_read = int(self._word_count * self._current_progress)
        return (words_read / elapsed) * 60.0 if words_read > 0 else 0.0

    def format_time(self, seconds: float) -> str:
        """Format seconds into a human-readable time string.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string (e.g., "2m 30s", "1h 15m")
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

    def get_statistics(self) -> dict:
        """Get comprehensive reading statistics.

        Returns:
            Dictionary containing various reading metrics
        """
        elapsed = self.get_elapsed_time()
        words_read = int(self._word_count * self._current_progress)

        return {
            "total_words": self._word_count,
            "words_read": words_read,
            "words_remaining": self._word_count - words_read,
            "progress_percentage": self._current_progress * 100,
            "elapsed_time": elapsed,
            "elapsed_time_formatted": self.format_time(elapsed),
            "remaining_time": self.get_remaining_time(),
            "remaining_time_formatted": self.format_time(self.get_remaining_time()),
            "average_wpm": self.get_average_wpm(),
            "is_paused": self._pause_time is not None,
            "total_pause_duration": self._total_pause_duration,
        }
