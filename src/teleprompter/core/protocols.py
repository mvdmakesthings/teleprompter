"""Protocol definitions for the teleprompter application.

This module defines interfaces (protocols) that establish contracts for various
components in the application, promoting loose coupling and testability.
"""

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class FileLoaderProtocol(Protocol):
    """Protocol for file loading implementations.

    This protocol defines the interface for classes that can load and validate
    files. Implementations should handle file reading, validation, and provide
    information about supported file types.
    """

    def load_file(self, file_path: str) -> str:
        """Load content from a file.

        Args:
            file_path: Path to the file to load.

        Returns:
            The content of the file as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If the file cannot be read.
            ValueError: If the file content is invalid.
        """
        ...

    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded.

        Args:
            file_path: Path to the file to validate.

        Returns:
            True if the file can be loaded, False otherwise.
        """
        ...

    def get_supported_extensions(self) -> list[str]:
        """Return list of supported file extensions.

        Returns:
            List of file extensions (including the dot) that this loader
            supports, e.g., ['.md', '.markdown', '.txt'].
        """
        ...


@runtime_checkable
class FileManagerProtocol(Protocol):
    """Protocol for file management operations.

    This protocol defines the interface for classes that handle file
    operations including loading, saving, and validation. Implementations
    should provide comprehensive file management capabilities for the
    teleprompter application.
    """

    def load_file(self, file_path: str) -> str:
        """Load content from a file.

        Args:
            file_path: Path to the file to load.

        Returns:
            The content of the file as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If the file cannot be read.
            ValueError: If the file content is invalid.
        """
        ...

    def save_file(self, file_path: str, content: str) -> bool:
        """Save content to a file.

        Args:
            file_path: Path where the file should be saved.
            content: Content to write to the file.

        Returns:
            True if the file was saved successfully, False otherwise.

        Raises:
            IOError: If the file cannot be written.
            PermissionError: If there are insufficient permissions.
        """
        ...

    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded.

        Args:
            file_path: Path to the file to validate.

        Returns:
            True if the file exists and can be loaded, False otherwise.
        """
        ...


@runtime_checkable
class HtmlContentAnalyzerProtocol(Protocol):
    """Protocol for HTML content analysis.

    This protocol defines methods for analyzing HTML content to extract
    statistics, word counts, and structural information such as sections
    and headings. Implementations should handle various HTML structures
    and provide meaningful metrics for teleprompter usage.
    """

    def count_words(self, html_content: str) -> int:
        """Count words in HTML content.

        Args:
            html_content: HTML content to analyze.

        Returns:
            Number of words found in the content, excluding HTML tags.

        Note:
            Words are typically counted by extracting text content from
            HTML and splitting on whitespace. HTML entities should be
            properly decoded before counting.
        """
        ...

    def find_sections(self, html_content: str) -> list[str]:
        """Find sections/headings in HTML content.

        Args:
            html_content: HTML content to analyze.

        Returns:
            List of section titles found in heading tags (h1-h6).
            Titles are returned in order of appearance.

        Note:
            Only text content from heading tags is extracted, not the
            HTML markup itself.
        """
        ...

    def analyze_html(self, html_content: str) -> dict:
        """Analyze HTML content and return comprehensive statistics.

        Args:
            html_content: HTML content to analyze.

        Returns:
            Dictionary containing analysis results with keys such as:
            - 'word_count': Total number of words
            - 'sections': List of section titles
            - 'estimated_reading_time': Estimated time in minutes
            - 'total_elements': Number of HTML elements
            Additional keys may be included based on implementation.

        Raises:
            ValueError: If the HTML content is malformed or cannot be parsed.
        """
        ...


@runtime_checkable
class ContentParserProtocol(Protocol):
    """Protocol for content parsing implementations.

    This protocol defines the interface for classes that can parse various
    content formats (such as Markdown) and convert them to display-ready
    formats (such as HTML). Implementations should handle parsing errors
    gracefully and provide word count functionality.
    """

    def parse(self, content: str) -> str:
        """Parse content and return formatted output.

        Args:
            content: Raw content to parse (e.g., Markdown text).

        Returns:
            Parsed and formatted content ready for display (e.g., HTML).

        Raises:
            ValueError: If the content cannot be parsed or is malformed.
            RuntimeError: If the parser encounters an internal error.
        """
        ...

    def get_word_count(self, content: str) -> int:
        """Get word count from content.

        Args:
            content: Content to count words in (raw or parsed format).

        Returns:
            Number of words in the content.

        Note:
            Word counting should handle both raw input format and any
            markup or formatting characters appropriately.
        """
        ...


# UI-related StyleProviderProtocol removed - not needed for backend-only operation


@runtime_checkable
class SettingsStorageProtocol(Protocol):
    """Protocol for settings storage implementations.

    This protocol defines the interface for classes that handle persistent
    storage of application settings. Implementations should provide reliable
    storage and retrieval of configuration data with appropriate error handling.
    """

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting value.

        Args:
            key: The setting key to retrieve.
            default: Default value to return if the key is not found.

        Returns:
            The stored value for the key, or the default value if not found.

        Note:
            Values are returned in their original type as stored. Implementations
            should handle type preservation appropriately.
        """
        ...

    def set(self, key: str, value: Any) -> None:
        """Store a setting value.

        Args:
            key: The setting key to store.
            value: The value to store. Should be serializable.

        Raises:
            TypeError: If the value cannot be serialized.
            IOError: If the setting cannot be written to storage.
        """
        ...

    def remove(self, key: str) -> None:
        """Remove a setting.

        Args:
            key: The setting key to remove.

        Note:
            This method should not raise an error if the key does not exist.
        """
        ...

    def clear(self) -> None:
        """Clear all settings.

        Removes all stored settings from the storage backend.

        Raises:
            IOError: If the storage cannot be cleared.
        """
        ...


@runtime_checkable
class VoiceDetectorProtocol(Protocol):
    """Protocol for voice detection implementations.

    This protocol defines the interface for voice activity detection systems.
    Implementations should provide real-time voice detection with configurable
    sensitivity and use callbacks for detected events.

    Callbacks:
        voice_detected_callback: Called when voice activity is detected.
        voice_stopped_callback: Called when voice activity stops.
        error_callback: Called when an error occurs during detection.
    """

    # Event callbacks
    voice_detected_callback: Callable[[], None] | None
    voice_stopped_callback: Callable[[], None] | None
    error_callback: Callable[[str], None] | None

    def start(self) -> None:
        """Start voice detection.

        Begins monitoring audio input for voice activity. The detector
        will call the configured callbacks when voice is detected or stopped.

        Raises:
            RuntimeError: If detection is already running.
            OSError: If audio input cannot be initialized.
            PermissionError: If microphone access is denied.
        """
        ...

    def stop(self) -> None:
        """Stop voice detection.

        Stops monitoring audio input and releases audio resources.
        Safe to call even if detection is not running.
        """
        ...

    def is_running(self) -> bool:
        """Check if voice detection is running.

        Returns:
            True if voice detection is currently active, False otherwise.
        """
        ...

    def set_sensitivity(self, level: int) -> None:
        """Set detection sensitivity.

        Args:
            level: Sensitivity level from 0 (least sensitive) to 3 (most sensitive).
                   Higher values will detect quieter speech but may increase
                   false positives from background noise.

        Raises:
            ValueError: If level is not in the range 0-3.
        """
        ...

    def get_audio_level(self) -> float:
        """Get current audio level.

        Returns:
            Current audio input level as a float from 0.0 (silence) to 1.0
            (maximum level). Useful for displaying audio level indicators.

        Note:
            This value represents the instantaneous audio level and may
            fluctuate rapidly. Consider smoothing for display purposes.
        """
        ...

    def set_voice_detected_callback(self, callback: Callable[[], None] | None) -> None:
        """Set callback for voice detection events.

        Args:
            callback: Function to call when voice is detected, or None to remove.
        """
        ...

    def set_voice_stopped_callback(self, callback: Callable[[], None] | None) -> None:
        """Set callback for voice stopped events.

        Args:
            callback: Function to call when voice stops, or None to remove.
        """
        ...

    def set_error_callback(self, callback: Callable[[str], None] | None) -> None:
        """Set callback for error events.

        Args:
            callback: Function to call when an error occurs, or None to remove.
                     Should accept error message as string parameter.
        """
        ...


@runtime_checkable
class ScrollControllerProtocol(Protocol):
    """Protocol for scroll control implementations.

    This protocol defines the interface for classes that manage scrolling
    behavior in the teleprompter. Implementations should handle smooth
    scrolling, speed control, position tracking, and navigation.
    """

    def start_scrolling(self) -> None:
        """Start scrolling from the current position.

        Begins automatic scrolling at the current speed setting.
        If scrolling is already active, this method has no effect.

        Raises:
            RuntimeError: If the scroll controller is not properly initialized.
        """
        ...

    def stop_scrolling(self) -> None:
        """Stop scrolling completely.

        Stops all scrolling activity and maintains the current position.
        Safe to call even if scrolling is not active.
        """
        ...

    def pause_scrolling(self) -> None:
        """Pause scrolling temporarily.

        Pauses scrolling while maintaining the current state. Scrolling
        can be resumed with start_scrolling() without losing position.
        """
        ...

    def set_speed(self, speed: float) -> None:
        """Set scrolling speed.

        Args:
            speed: Scrolling speed multiplier where 1.0 is normal speed.
                   Values should typically range from 0.05 to 5.0.

        Raises:
            ValueError: If speed is negative or exceeds reasonable limits.

        Note:
            Speed changes take effect immediately, even during active scrolling.
        """
        ...

    def get_progress(self) -> float:
        """Get current scroll progress.

        Returns:
            Progress as a float from 0.0 (beginning) to 1.0 (end).

        Note:
            Progress is calculated based on the current scroll position
            relative to the total scrollable content height.
        """
        ...

    def jump_to_position(self, position: float) -> None:
        """Jump to a specific position in the content.

        Args:
            position: Target position as a float from 0.0 (beginning) to 1.0 (end).

        Raises:
            ValueError: If position is not in the range 0.0-1.0.

        Note:
            This method immediately moves to the specified position,
            interrupting any active scrolling.
        """
        ...


@runtime_checkable
class ReadingMetricsProtocol(Protocol):
    """Protocol for reading metrics calculations.

    This protocol defines methods for calculating various reading-related
    metrics such as reading time, words per minute, and progress tracking.
    Implementations should provide accurate calculations based on content
    analysis and reading behavior.
    """

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
            Actual reading time may vary based on content complexity and
            pauses.
        """
        ...

    def calculate_words_per_minute(self, speed: float) -> float:
        """Calculate effective words per minute based on scroll speed.

        Args:
            speed: Scroll speed multiplier (1.0 = normal speed).

        Returns:
            Effective words per minute at the given scroll speed.

        Note:
            This method converts scroll speed to reading speed, taking into
            account the relationship between scrolling rate and reading rate.
        """
        ...

    def get_elapsed_time(self) -> float:
        """Get elapsed reading time in seconds.

        Returns:
            Time spent reading since the session started, excluding pauses.

        Note:
            This time represents actual reading time and excludes periods
            when reading was paused or stopped.
        """
        ...

    def get_remaining_time(self) -> float:
        """Get remaining reading time in seconds.

        Returns:
            Estimated time remaining to complete the current content,
            based on current reading speed and progress.

        Note:
            This estimate assumes reading continues at the current speed
            without interruption.
        """
        ...


@runtime_checkable
# UI-related ToolbarFactoryProtocol removed - not needed for backend-only operation


# UI-related IconProviderProtocol removed - not needed for backend-only operation


class ManagerProtocol(Protocol):
    """Base protocol for all manager classes.

    This protocol defines the common interface that all manager classes
    should implement. Managers are responsible for coordinating specific
    aspects of the application lifecycle and resource management.
    """

    def initialize(self) -> None:
        """Initialize the manager.

        Performs any necessary setup tasks for the manager to become
        operational. This should include resource allocation, initial
        configuration, and dependency setup.

        Raises:
            RuntimeError: If initialization fails.
            OSError: If required resources cannot be allocated.
        """
        ...

    def cleanup(self) -> None:
        """Clean up resources.

        Releases any resources held by the manager and performs cleanup
        tasks. This method should be called before the manager is destroyed
        and should be safe to call multiple times.

        Note:
            This method should not raise exceptions during cleanup to
            ensure proper resource release even in error conditions.
        """
        ...


# UI-related AnimatedWidgetProtocol removed - not needed for backend-only operation


@runtime_checkable
class FileWatcherProtocol(Protocol):
    """Protocol for file watching implementations.

    This protocol defines the interface for classes that monitor files
    for changes and use callbacks when modifications occur. Implementations
    should support debouncing to prevent rapid reloads and handle file
    system edge cases gracefully.

    Callbacks:
        file_changed_callback: Called when watched file is modified.
        file_removed_callback: Called when watched file is deleted.
        watch_error_callback: Called when watching fails.
    """

    # Event callbacks
    file_changed_callback: Callable[[str], None] | None
    file_removed_callback: Callable[[str], None] | None
    watch_error_callback: Callable[[str, str], None] | None

    def watch_file(self, file_path: str) -> bool:
        """Start watching a file for changes.

        Args:
            file_path: Path to the file to watch.

        Returns:
            True if watching was successful, False otherwise.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be accessed.
        """
        ...

    def stop_watching(self) -> None:
        """Stop watching the current file.

        Releases any resources associated with file watching.
        Safe to call even if not currently watching a file.
        """
        ...

    def get_watched_file(self) -> str | None:
        """Get the currently watched file path.

        Returns:
            Path to the watched file or None if not watching.
        """
        ...

    def is_watching(self) -> bool:
        """Check if currently watching a file.

        Returns:
            True if watching a file, False otherwise.
        """
        ...

    def set_debounce_delay(self, delay_ms: int) -> None:
        """Set the debounce delay for file change notifications.

        Args:
            delay_ms: Delay in milliseconds. Must be non-negative.

        Raises:
            ValueError: If delay_ms is negative.

        Note:
            Debouncing prevents multiple rapid notifications when a file
            is saved multiple times in quick succession.
        """
        ...

    def set_file_changed_callback(self, callback: Callable[[str], None] | None) -> None:
        """Set callback for file changed events.

        Args:
            callback: Function to call when file changes, receives file path as parameter.
        """
        ...

    def set_file_removed_callback(self, callback: Callable[[str], None] | None) -> None:
        """Set callback for file removed events.

        Args:
            callback: Function to call when file is removed, receives file path as parameter.
        """
        ...

    def set_watch_error_callback(self, callback: Callable[[str, str], None] | None) -> None:
        """Set callback for watch error events.

        Args:
            callback: Function to call when watch error occurs.
                     Receives file path and error message as parameters.
        """
        ...


# UI-related ResponsiveLayoutProtocol removed - not needed for backend-only operation
