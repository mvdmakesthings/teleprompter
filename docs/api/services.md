# Services Reference

This document provides detailed documentation for all service implementations in the teleprompter application.

## Core Services

### ScrollController

Controls scrolling behavior and animations.

```python
class ScrollController:
    """Controls scrolling behavior and animations.
    
    This service manages the scrolling logic, including speed control,
    position tracking, and smooth animation calculations.
    
    Attributes:
        _speed: Current scroll speed multiplier
        _is_scrolling: Whether scrolling is active
        _scroll_position: Current scroll position in pixels
        _content_height: Total content height in pixels
        _viewport_height: Visible area height in pixels
    """
    
    def __init__(self):
        """Initialize scroll controller with default settings.
        
        Sets up initial state with:
        - Speed: 1.0 (normal)
        - Position: 0 (top)
        - Not scrolling
        """
    
    def set_viewport_dimensions(self, viewport_height: int, content_height: int):
        """Set viewport and content dimensions.
        
        Args:
            viewport_height: Height of the visible scrolling area in pixels
            content_height: Total height of the content in pixels
            
        Example:
            >>> controller = ScrollController()
            >>> controller.set_viewport_dimensions(800, 2400)
            >>> # Can now scroll through 1600 pixels of content
        """
    
    def calculate_next_position(self, delta_time: float) -> float:
        """Calculate next scroll position based on time delta.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
            
        Returns:
            Next scroll position in pixels from top
            
        Note:
            Uses BASE_SCROLL_SPEED from config (default 100 pixels/second)
            adjusted by current speed multiplier
            
        Example:
            >>> controller = ScrollController()
            >>> controller.set_speed(2.0)  # 2x speed
            >>> next_pos = controller.calculate_next_position(0.016)  # ~60 FPS
            >>> # Returns current position + (100 * 2.0 * 0.016) pixels
        """
    
    def update_scroll_position(self, position: float):
        """Update the current scroll position.
        
        Args:
            position: New scroll position in pixels
            
        Note:
            Position is clamped between 0 and max scrollable distance
            
        Example:
            >>> controller.update_scroll_position(500.5)
        """
    
    def start_scrolling(self):
        """Start automatic scrolling.
        
        Sets the scrolling state to active. Does not actually
        perform scrolling - that's handled by calculate_next_position.
        
        Example:
            >>> controller.start_scrolling()
            >>> assert controller.is_scrolling()
        """
    
    def pause_scrolling(self):
        """Pause scrolling without resetting position.
        
        Maintains current position for resuming later.
        
        Example:
            >>> controller.pause_scrolling()
            >>> position_before = controller._scroll_position
            >>> # ... time passes ...
            >>> controller.start_scrolling()
            >>> assert controller._scroll_position == position_before
        """
    
    def stop_scrolling(self):
        """Stop scrolling and reset to beginning.
        
        Sets scrolling state to inactive and resets position to 0.
        
        Example:
            >>> controller.stop_scrolling()
            >>> assert controller._scroll_position == 0
            >>> assert not controller.is_scrolling()
        """
    
    def set_speed(self, speed: float):
        """Set scrolling speed multiplier.
        
        Args:
            speed: Speed multiplier (0.05 to 5.0)
                   1.0 = normal (200 WPM)
                   2.0 = double speed (400 WPM)
                   0.5 = half speed (100 WPM)
                   
        Note:
            Speed is clamped to MIN_SPEED and MAX_SPEED from config
            
        Example:
            >>> controller.set_speed(1.5)
            >>> assert controller.get_speed() == 1.5
        """
    
    def get_speed(self) -> float:
        """Get current speed multiplier.
        
        Returns:
            Current speed setting
            
        Example:
            >>> speed = controller.get_speed()
            >>> print(f"Currently at {speed}x speed")
        """
    
    def adjust_speed(self, delta: float):
        """Adjust speed by a delta amount.
        
        Args:
            delta: Amount to adjust speed by (positive or negative)
            
        Example:
            >>> controller.set_speed(1.0)
            >>> controller.adjust_speed(0.5)  # Increase by 0.5
            >>> assert controller.get_speed() == 1.5
        """
    
    def get_progress(self) -> float:
        """Get current reading progress.
        
        Returns:
            Progress as float between 0.0 (start) and 1.0 (end)
            
        Example:
            >>> progress = controller.get_progress()
            >>> percentage = progress * 100
            >>> print(f"Reading progress: {percentage:.1f}%")
        """
    
    def set_progress(self, progress: float):
        """Set reading progress.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            
        Note:
            Internally converts progress to scroll position
            
        Example:
            >>> controller.set_progress(0.5)  # Jump to middle
        """
    
    def has_reached_end(self) -> bool:
        """Check if scrolling has reached the end.
        
        Returns:
            True if at or past the end of content
            
        Example:
            >>> if controller.has_reached_end():
            ...     controller.stop_scrolling()
        """
```

### ReadingMetricsService

Tracks reading progress and calculates statistics.

```python
class ReadingMetricsService:
    """Service for calculating reading metrics and statistics.
    
    Tracks reading time, calculates words per minute, and provides
    progress-based time estimates.
    
    Attributes:
        _word_count: Total words in document
        _start_time: When reading started
        _elapsed_time: Total time spent reading
        _is_reading: Whether currently reading
        _progress: Current reading progress (0.0 to 1.0)
    """
    
    def __init__(self):
        """Initialize reading metrics service."""
    
    def set_word_count(self, count: int):
        """Set the total word count for the document.
        
        Args:
            count: Total number of words
            
        Example:
            >>> metrics = ReadingMetricsService()
            >>> metrics.set_word_count(1000)
        """
    
    def start_reading(self):
        """Start tracking reading time.
        
        Records the start time and sets reading state to active.
        
        Example:
            >>> metrics.start_reading()
            >>> # Reading timer is now running
        """
    
    def pause_reading(self):
        """Pause reading time tracking.
        
        Accumulates elapsed time and pauses the timer.
        Can be resumed with start_reading().
        
        Example:
            >>> metrics.pause_reading()
            >>> # Timer paused, elapsed time preserved
        """
    
    def stop_reading(self):
        """Stop reading and reset metrics.
        
        Resets all tracking state to initial values.
        
        Example:
            >>> metrics.stop_reading()
            >>> assert metrics.get_elapsed_time() == 0
        """
    
    def set_progress(self, progress: float):
        """Update current reading progress.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            
        Example:
            >>> metrics.set_progress(0.25)  # 25% complete
        """
    
    def get_progress(self) -> float:
        """Get current reading progress.
        
        Returns:
            Progress as float between 0.0 and 1.0
            
        Example:
            >>> progress = metrics.get_progress()
            >>> print(f"{progress * 100:.0f}% complete")
        """
    
    def calculate_reading_time(self, word_count: int, wpm: float) -> float:
        """Calculate estimated reading time.
        
        Args:
            word_count: Number of words to read
            wpm: Reading speed in words per minute
            
        Returns:
            Estimated time in seconds
            
        Example:
            >>> time_sec = metrics.calculate_reading_time(600, 200)
            >>> print(f"{time_sec / 60:.1f} minutes")
            3.0 minutes
        """
    
    def calculate_words_per_minute(self, speed: float) -> float:
        """Calculate effective WPM based on scroll speed.
        
        Args:
            speed: Scroll speed multiplier
            
        Returns:
            Effective words per minute
            
        Note:
            Base WPM is 200, multiplied by speed factor
            
        Example:
            >>> wpm = metrics.calculate_words_per_minute(1.5)
            >>> print(f"Reading at {wpm} words per minute")
            Reading at 300 words per minute
        """
    
    def get_elapsed_time(self) -> float:
        """Get time spent reading.
        
        Returns:
            Elapsed time in seconds
            
        Example:
            >>> elapsed = metrics.get_elapsed_time()
            >>> minutes = elapsed / 60
            >>> print(f"You've been reading for {minutes:.1f} minutes")
        """
    
    def get_remaining_time(self) -> float:
        """Get estimated time remaining.
        
        Returns:
            Remaining time in seconds based on current progress
            and average reading speed
            
        Example:
            >>> remaining = metrics.get_remaining_time()
            >>> if remaining < 60:
            ...     print(f"{remaining:.0f} seconds left")
            ... else:
            ...     print(f"{remaining / 60:.1f} minutes left")
        """
    
    def get_average_wpm(self) -> float:
        """Calculate average reading speed.
        
        Returns:
            Average words per minute based on actual progress
            
        Example:
            >>> avg_wpm = metrics.get_average_wpm()
            >>> print(f"Average speed: {avg_wpm:.0f} WPM")
        """
```

### ContentManager

Manages content loading, parsing, and caching.

```python
class ContentManager:
    """Manages content loading, parsing, and caching.
    
    Provides a high-level interface for content operations,
    handling markdown parsing and format conversions.
    
    Attributes:
        _parser: Content parser implementation
        _markdown_content: Raw markdown content
        _html_content: Parsed HTML content
        _plain_text: Plain text version
    """
    
    def __init__(self, parser: ContentParserProtocol):
        """Initialize content manager.
        
        Args:
            parser: Parser implementation for content conversion
            
        Example:
            >>> parser = MarkdownParser()
            >>> manager = ContentManager(parser)
        """
    
    def load_markdown(self, content: str):
        """Load markdown content.
        
        Args:
            content: Raw markdown content
            
        Note:
            Automatically parses to HTML and extracts plain text
            
        Example:
            >>> manager.load_markdown("# Hello\\n\\nWorld")
            >>> html = manager.get_html()
            >>> assert "<h1>Hello</h1>" in html
        """
    
    def load_file(self, file_path: str):
        """Load content from file.
        
        Args:
            file_path: Path to markdown file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
            
        Example:
            >>> manager.load_file("document.md")
        """
    
    def get_html(self) -> str:
        """Get content as HTML.
        
        Returns:
            HTML representation of the content
            
        Example:
            >>> html = manager.get_html()
            >>> # Use for web view display
        """
    
    def get_plain_text(self) -> str:
        """Get content as plain text.
        
        Returns:
            Plain text without any formatting or markup
            
        Example:
            >>> text = manager.get_plain_text()
            >>> word_count = len(text.split())
        """
    
    def get_markdown(self) -> str:
        """Get original markdown content.
        
        Returns:
            Original markdown content before parsing
            
        Example:
            >>> markdown = manager.get_markdown()
            >>> # Use for editing or saving
        """
    
    def has_content(self) -> bool:
        """Check if content is loaded.
        
        Returns:
            True if content has been loaded
            
        Example:
            >>> if manager.has_content():
            ...     display_content(manager.get_html())
        """
    
    def clear(self):
        """Clear all loaded content.
        
        Resets the manager to initial empty state.
        
        Example:
            >>> manager.clear()
            >>> assert not manager.has_content()
        """
    
    def get_word_count(self) -> int:
        """Get word count of current content.
        
        Returns:
            Number of words in the content
            
        Example:
            >>> count = manager.get_word_count()
            >>> print(f"Document contains {count} words")
        """
```

### HtmlContentAnalyzer

Analyzes HTML content for metadata extraction.

```python
class HtmlContentAnalyzer:
    """Service for analyzing HTML content.
    
    Extracts metadata and statistics from HTML documents,
    including word counts, sections, and content features.
    """
    
    def count_words(self, html_content: str) -> int:
        """Count words in HTML content.
        
        Args:
            html_content: HTML to analyze
            
        Returns:
            Word count excluding HTML tags and scripts
            
        Example:
            >>> analyzer = HtmlContentAnalyzer()
            >>> count = analyzer.count_words(
            ...     "<p>Hello <b>world</b>!</p>"
            ... )
            >>> assert count == 2
        """
    
    def find_sections(self, html_content: str) -> list[str]:
        """Find all sections/headings.
        
        Args:
            html_content: HTML to analyze
            
        Returns:
            List of section titles from h1-h6 tags
            
        Example:
            >>> sections = analyzer.find_sections(html)
            >>> for i, section in enumerate(sections):
            ...     print(f"{i+1}. {section}")
            1. Introduction
            2. Chapter 1
            3. Chapter 2
        """
    
    def analyze_html(self, html_content: str) -> dict:
        """Perform complete content analysis.
        
        Args:
            html_content: HTML to analyze
            
        Returns:
            Dictionary containing:
            - total_words: Word count
            - sections: List of section titles
            - reading_time: Estimated minutes to read
            - has_code: Whether content has code blocks
            - has_images: Whether content has images
            - has_links: Whether content has hyperlinks
            - paragraph_count: Number of paragraphs
            - average_paragraph_length: Words per paragraph
            
        Example:
            >>> stats = analyzer.analyze_html(html_content)
            >>> print(f"Reading time: {stats['reading_time']:.1f} min")
            >>> if stats['has_code']:
            ...     print("Document contains code examples")
        """
    
    def extract_table_of_contents(self, html_content: str) -> list[dict]:
        """Extract hierarchical table of contents.
        
        Args:
            html_content: HTML to analyze
            
        Returns:
            List of TOC entries with:
            - title: Section title
            - level: Heading level (1-6)
            - id: Element ID for navigation
            
        Example:
            >>> toc = analyzer.extract_table_of_contents(html)
            >>> for entry in toc:
            ...     indent = "  " * (entry['level'] - 1)
            ...     print(f"{indent}- {entry['title']}")
        """
    
    def find_section_in_html(
        self, 
        html_content: str, 
        section_title: str
    ) -> str:
        """Generate JavaScript to find and scroll to section.
        
        Args:
            html_content: HTML content
            section_title: Title of section to find
            
        Returns:
            JavaScript code to scroll to the section
            
        Example:
            >>> js = analyzer.find_section_in_html(html, "Chapter 2")
            >>> # Execute JS in web view to navigate
        """
```

## Manager Services

### FileManager

Manages file operations with signals for UI integration.

```python
class FileManager(QObject):
    """Manages file operations with loading states and error handling.
    
    Provides file loading with progress tracking and error reporting
    through Qt signals.
    
    Signals:
        loading_started: Emitted when file loading begins
        loading_finished: Emitted when file loading completes
        file_loaded: Emitted with (html_content, file_path, markdown_content)
        error_occurred: Emitted with (error_message, error_type)
    """
    
    def open_file_dialog(self) -> str | None:
        """Open file dialog for selecting a file.
        
        Returns:
            Selected file path or None if cancelled
            
        Example:
            >>> manager = FileManager()
            >>> file_path = manager.open_file_dialog()
            >>> if file_path:
            ...     print(f"Selected: {file_path}")
        """
    
    def load_file(self, file_path: str):
        """Load a file with progress tracking.
        
        Args:
            file_path: Path to the file to load
            
        Emits:
            loading_started: When loading begins
            file_loaded: When successful with content
            error_occurred: When loading fails
            loading_finished: Always when done
            
        Example:
            >>> manager = FileManager()
            >>> manager.file_loaded.connect(on_file_loaded)
            >>> manager.error_occurred.connect(on_error)
            >>> manager.load_file("document.md")
        """
    
    def validate_file(self, file_path: str) -> bool:
        """Check if file is valid for loading.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if file exists and has supported extension
            
        Example:
            >>> if manager.validate_file(path):
            ...     manager.load_file(path)
        """
    
    def get_recent_files(self) -> list[str]:
        """Get list of recently opened files.
        
        Returns:
            List of file paths, most recent first
            
        Example:
            >>> recent = manager.get_recent_files()
            >>> for path in recent[:5]:  # Show last 5
            ...     print(path)
        """
```

### SettingsManager

Manages application settings persistence.

```python
class SettingsManager:
    """Manages persistent application settings.
    
    Uses QSettings for cross-platform settings storage.
    Settings are automatically saved and loaded.
    """
    
    def get_speed(self) -> float:
        """Get saved scroll speed.
        
        Returns:
            Scroll speed multiplier (default: 1.0)
        """
    
    def set_speed(self, speed: float):
        """Save scroll speed setting.
        
        Args:
            speed: Speed multiplier to save
        """
    
    def get_font_size(self) -> int:
        """Get saved font size.
        
        Returns:
            Font size in pixels (default: 24)
        """
    
    def set_font_size(self, size: int):
        """Save font size setting.
        
        Args:
            size: Font size in pixels
        """
    
    def get_voice_enabled(self) -> bool:
        """Get voice control enabled state.
        
        Returns:
            True if voice control is enabled
        """
    
    def set_voice_enabled(self, enabled: bool):
        """Save voice control state.
        
        Args:
            enabled: Whether voice control is enabled
        """
    
    def get_window_geometry(self) -> bytes | None:
        """Get saved window geometry.
        
        Returns:
            Window geometry bytes or None
            
        Example:
            >>> geometry = settings.get_window_geometry()
            >>> if geometry:
            ...     window.restoreGeometry(geometry)
        """
    
    def save_window_geometry(self, geometry: bytes):
        """Save window geometry.
        
        Args:
            geometry: Window geometry as bytes
            
        Example:
            >>> settings.save_window_geometry(
            ...     window.saveGeometry()
            ... )
        """
    
    def reset_to_defaults(self):
        """Reset all settings to defaults.
        
        Example:
            >>> settings.reset_to_defaults()
            >>> assert settings.get_speed() == 1.0
            >>> assert settings.get_font_size() == 24
        """
```

## Usage Examples

### Complete Reading Session

```python
# Initialize services
container = configure_container()
content_manager = ContentManager(container.get(ContentParserProtocol))
scroll_controller = container.get(ScrollControllerProtocol)
metrics = container.get(ReadingMetricsProtocol)

# Load content
content_manager.load_file("book.md")
word_count = content_manager.get_word_count()

# Set up metrics
metrics.set_word_count(word_count)
metrics.start_reading()

# Configure scrolling
scroll_controller.set_viewport_dimensions(800, 5000)
scroll_controller.set_speed(1.5)  # 1.5x speed
scroll_controller.start_scrolling()

# Simulate reading
for _ in range(100):
    position = scroll_controller.calculate_next_position(0.016)
    scroll_controller.update_scroll_position(position)
    
    progress = scroll_controller.get_progress()
    metrics.set_progress(progress)
    
    if scroll_controller.has_reached_end():
        break

# Get statistics
elapsed = metrics.get_elapsed_time()
avg_wpm = metrics.get_average_wpm()
print(f"Read {word_count} words in {elapsed/60:.1f} minutes")
print(f"Average speed: {avg_wpm:.0f} WPM")
```

### Service Composition

```python
class ReadingSession:
    """Combines multiple services for a reading session."""
    
    def __init__(
        self,
        content_manager: ContentManager,
        scroll_controller: ScrollController,
        metrics: ReadingMetricsService
    ):
        self.content = content_manager
        self.scroll = scroll_controller
        self.metrics = metrics
    
    def start(self, file_path: str, speed: float = 1.0):
        """Start a new reading session."""
        # Load content
        self.content.load_file(file_path)
        
        # Initialize metrics
        word_count = self.content.get_word_count()
        self.metrics.set_word_count(word_count)
        self.metrics.start_reading()
        
        # Start scrolling
        self.scroll.set_speed(speed)
        self.scroll.start_scrolling()
    
    def get_status(self) -> dict:
        """Get current session status."""
        return {
            'is_reading': self.scroll.is_scrolling(),
            'progress': self.scroll.get_progress(),
            'elapsed_time': self.metrics.get_elapsed_time(),
            'remaining_time': self.metrics.get_remaining_time(),
            'current_wpm': self.metrics.get_average_wpm()
        }
```

## Testing Services

```python
import pytest
from unittest.mock import Mock

def test_scroll_controller():
    """Test scroll controller behavior."""
    controller = ScrollController()
    
    # Set up viewport
    controller.set_viewport_dimensions(600, 1200)
    
    # Test speed control
    controller.set_speed(2.0)
    assert controller.get_speed() == 2.0
    
    # Test scrolling
    controller.start_scrolling()
    assert controller.is_scrolling()
    
    # Test position calculation
    next_pos = controller.calculate_next_position(0.1)
    assert next_pos > 0
    
    # Test progress
    controller.update_scroll_position(600)
    assert controller.get_progress() == pytest.approx(0.5)

def test_reading_metrics():
    """Test reading metrics calculations."""
    metrics = ReadingMetricsService()
    
    # Set up document
    metrics.set_word_count(1000)
    
    # Test WPM calculation
    assert metrics.calculate_words_per_minute(1.0) == 200
    assert metrics.calculate_words_per_minute(2.0) == 400
    
    # Test reading time
    time_sec = metrics.calculate_reading_time(1000, 200)
    assert time_sec == 300  # 5 minutes
```

## Performance Considerations

1. **ScrollController**: Optimized for 60 FPS with minimal calculations
2. **ContentManager**: Caches parsed content to avoid re-parsing
3. **HtmlContentAnalyzer**: Uses efficient regex for large documents
4. **FileManager**: Loads files asynchronously to prevent UI blocking

## See Also

- [Protocol Reference](protocols.md)
- [Widget Reference](widgets.md)
- [Architecture Overview](index.md)