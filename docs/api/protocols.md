# Protocol Reference

This document provides detailed documentation for all protocols (interfaces) in the teleprompter application.

## Core Protocols

### FileLoaderProtocol

Interface for file loading implementations.

```python
@runtime_checkable
class FileLoaderProtocol(Protocol):
    """Protocol for file loading implementations."""
    
    def load_file(self, file_path: str) -> str:
        """Load content from a file.
        
        Args:
            file_path: Absolute or relative path to the file
            
        Returns:
            The content of the file as a string
            
        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read due to permissions
            IOError: For other I/O related errors
            
        Example:
            >>> loader = FileManager()
            >>> content = loader.load_file("document.md")
            >>> print(content[:50])
            '# My Document\n\nThis is the content...'
        """
        ...
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file exists and has a supported extension,
            False otherwise
            
        Example:
            >>> loader = FileManager()
            >>> loader.validate_file("document.md")
            True
            >>> loader.validate_file("image.jpg")
            False
        """
        ...
    
    def get_supported_extensions(self) -> list[str]:
        """Return list of supported file extensions.
        
        Returns:
            List of file extensions that can be loaded,
            including the dot (e.g., ['.md', '.txt'])
            
        Example:
            >>> loader = FileManager()
            >>> loader.get_supported_extensions()
            ['.md', '.markdown', '.txt']
        """
        ...
```

### FileManagerProtocol

Extended protocol for file management operations.

```python
@runtime_checkable
class FileManagerProtocol(Protocol):
    """Protocol for file management operations."""
    
    def load_file(self, file_path: str) -> str:
        """Load content from a file.
        
        Inherits behavior from FileLoaderProtocol.
        """
        ...
    
    def save_file(self, file_path: str, content: str) -> bool:
        """Save content to a file.
        
        Args:
            file_path: Path where to save the file
            content: Content to write to the file
            
        Returns:
            True if save was successful, False otherwise
            
        Raises:
            PermissionError: If the file cannot be written
            IOError: For other I/O related errors
            
        Example:
            >>> manager = FileManager()
            >>> success = manager.save_file("output.md", "# Content")
            >>> print(success)
            True
        """
        ...
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded.
        
        Inherits behavior from FileLoaderProtocol.
        """
        ...
```

### ContentParserProtocol

Interface for content parsing implementations.

```python
@runtime_checkable
class ContentParserProtocol(Protocol):
    """Protocol for content parsing implementations."""
    
    def parse(self, content: str) -> str:
        """Parse content and return formatted output.
        
        Args:
            content: Raw content to parse (e.g., Markdown)
            
        Returns:
            Parsed content, typically as HTML
            
        Example:
            >>> parser = MarkdownParser()
            >>> html = parser.parse("# Hello\n\n**World**")
            >>> print(html)
            '<h1>Hello</h1>\n<p><strong>World</strong></p>'
        """
        ...
    
    def get_word_count(self, content: str) -> int:
        """Get word count from content.
        
        Args:
            content: Content to count words in
            
        Returns:
            Number of words in the content
            
        Note:
            Should count words in the raw content,
            ignoring markup or formatting
            
        Example:
            >>> parser = MarkdownParser()
            >>> count = parser.get_word_count("Hello world")
            >>> print(count)
            2
        """
        ...
```

### HtmlContentAnalyzerProtocol

Interface for HTML content analysis.

```python
@runtime_checkable
class HtmlContentAnalyzerProtocol(Protocol):
    """Protocol for HTML content analysis."""
    
    def count_words(self, html_content: str) -> int:
        """Count words in HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Number of words, excluding HTML tags
            
        Example:
            >>> analyzer = HtmlContentAnalyzer()
            >>> count = analyzer.count_words("<p>Hello <b>world</b></p>")
            >>> print(count)
            2
        """
        ...
    
    def find_sections(self, html_content: str) -> list[str]:
        """Find sections/headings in HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            List of section titles found in the content,
            in order of appearance
            
        Example:
            >>> analyzer = HtmlContentAnalyzer()
            >>> sections = analyzer.find_sections(
            ...     "<h1>Intro</h1><h2>Chapter 1</h2><h2>Chapter 2</h2>"
            ... )
            >>> print(sections)
            ['Intro', 'Chapter 1', 'Chapter 2']
        """
        ...
    
    def analyze_html(self, html_content: str) -> dict:
        """Analyze HTML content and return statistics.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Dictionary containing:
            - total_words: Total word count
            - sections: List of section titles
            - reading_time: Estimated reading time in minutes
            - has_code: Whether content contains code blocks
            - has_images: Whether content contains images
            
        Example:
            >>> analyzer = HtmlContentAnalyzer()
            >>> stats = analyzer.analyze_html(html_content)
            >>> print(stats)
            {
                'total_words': 500,
                'sections': ['Introduction', 'Main Content'],
                'reading_time': 2.5,
                'has_code': True,
                'has_images': False
            }
        """
        ...
```

### ScrollControllerProtocol

Interface for scroll control implementations.

```python
@runtime_checkable
class ScrollControllerProtocol(Protocol):
    """Protocol for scroll control implementations."""
    
    def start_scrolling(self) -> None:
        """Start automatic scrolling.
        
        Begins scrolling from the current position.
        If already scrolling, this has no effect.
        
        Example:
            >>> controller = ScrollController()
            >>> controller.start_scrolling()
        """
        ...
    
    def stop_scrolling(self) -> None:
        """Stop scrolling and reset position.
        
        Stops scrolling and resets the position to the beginning.
        
        Example:
            >>> controller = ScrollController()
            >>> controller.stop_scrolling()
            >>> controller.get_progress()
            0.0
        """
        ...
    
    def pause_scrolling(self) -> None:
        """Pause scrolling without resetting position.
        
        Temporarily stops scrolling but maintains current position.
        Can be resumed with start_scrolling().
        
        Example:
            >>> controller = ScrollController()
            >>> controller.pause_scrolling()
            >>> # Position is maintained
        """
        ...
    
    def set_speed(self, speed: float) -> None:
        """Set scrolling speed.
        
        Args:
            speed: Speed multiplier where:
                   - 1.0 = normal speed (200 WPM)
                   - 2.0 = double speed (400 WPM)
                   - 0.5 = half speed (100 WPM)
                   
        Note:
            Speed is clamped between MIN_SPEED and MAX_SPEED
            
        Example:
            >>> controller = ScrollController()
            >>> controller.set_speed(1.5)  # 1.5x speed
        """
        ...
    
    def get_progress(self) -> float:
        """Get current progress.
        
        Returns:
            Progress as a float between 0.0 (start) and 1.0 (end)
            
        Example:
            >>> controller = ScrollController()
            >>> progress = controller.get_progress()
            >>> print(f"{progress * 100:.1f}%")
            45.2%
        """
        ...
    
    def jump_to_position(self, position: float) -> None:
        """Jump to specific position.
        
        Args:
            position: Position as a float between 0.0 and 1.0
            
        Example:
            >>> controller = ScrollController()
            >>> controller.jump_to_position(0.5)  # Jump to middle
        """
        ...
```

### ReadingMetricsProtocol

Interface for reading metrics calculations.

```python
@runtime_checkable
class ReadingMetricsProtocol(Protocol):
    """Protocol for reading metrics calculations."""
    
    def calculate_reading_time(self, word_count: int, wpm: float) -> float:
        """Calculate estimated reading time in seconds.
        
        Args:
            word_count: Number of words in the document
            wpm: Words per minute reading speed
            
        Returns:
            Estimated reading time in seconds
            
        Example:
            >>> metrics = ReadingMetricsService()
            >>> time_seconds = metrics.calculate_reading_time(600, 200)
            >>> print(f"{time_seconds / 60:.1f} minutes")
            3.0 minutes
        """
        ...
    
    def calculate_words_per_minute(self, speed: float) -> float:
        """Calculate effective words per minute based on scroll speed.
        
        Args:
            speed: Scroll speed multiplier
            
        Returns:
            Effective words per minute
            
        Note:
            Base WPM is typically 200, adjusted by speed multiplier
            
        Example:
            >>> metrics = ReadingMetricsService()
            >>> wpm = metrics.calculate_words_per_minute(1.5)
            >>> print(wpm)
            300.0
        """
        ...
    
    def get_elapsed_time(self) -> float:
        """Get elapsed reading time in seconds.
        
        Returns:
            Time elapsed since reading started, in seconds
            
        Example:
            >>> metrics = ReadingMetricsService()
            >>> metrics.start_reading()
            >>> # ... some time passes ...
            >>> elapsed = metrics.get_elapsed_time()
            >>> print(f"{elapsed:.1f} seconds")
            45.2 seconds
        """
        ...
    
    def get_remaining_time(self) -> float:
        """Get remaining reading time in seconds.
        
        Returns:
            Estimated time remaining based on current progress
            and reading speed
            
        Example:
            >>> metrics = ReadingMetricsService()
            >>> remaining = metrics.get_remaining_time()
            >>> print(f"{remaining / 60:.1f} minutes remaining")
            2.3 minutes remaining
        """
        ...
```

## UI Protocols

### VoiceDetectorProtocol

Interface for voice detection implementations.

```python
@runtime_checkable
class VoiceDetectorProtocol(Protocol):
    """Protocol for voice detection implementations."""
    
    # Signals (PyQt)
    voice_detected: pyqtSignal
    voice_stopped: pyqtSignal
    error_occurred: pyqtSignal
    
    def start(self) -> None:
        """Start voice detection.
        
        Begins listening for voice activity.
        Emits voice_detected when voice is detected.
        
        Example:
            >>> detector = VoiceActivityDetector()
            >>> detector.voice_detected.connect(on_voice_detected)
            >>> detector.start()
        """
        ...
    
    def stop(self) -> None:
        """Stop voice detection.
        
        Stops listening and releases audio resources.
        
        Example:
            >>> detector.stop()
        """
        ...
    
    def is_running(self) -> bool:
        """Check if voice detection is running.
        
        Returns:
            True if currently detecting, False otherwise
            
        Example:
            >>> if detector.is_running():
            ...     print("Voice detection active")
        """
        ...
    
    def set_sensitivity(self, level: int) -> None:
        """Set detection sensitivity.
        
        Args:
            level: Sensitivity level (0-3) where:
                   - 0 = Most aggressive (fewer false positives)
                   - 3 = Least aggressive (fewer false negatives)
                   
        Example:
            >>> detector.set_sensitivity(2)  # Balanced
        """
        ...
    
    def get_audio_level(self) -> float:
        """Get current audio level.
        
        Returns:
            Audio level as float between 0.0 (silence) and 1.0 (max)
            
        Example:
            >>> level = detector.get_audio_level()
            >>> print(f"Audio level: {level * 100:.0f}%")
            Audio level: 45%
        """
        ...
```

### ResponsiveLayoutProtocol

Interface for responsive layout management.

```python
@runtime_checkable
class ResponsiveLayoutProtocol(Protocol):
    """Protocol for responsive layout management."""
    
    def get_device_category(self, width: int) -> str:
        """Determine device category based on width.
        
        Args:
            width: Screen width in pixels
            
        Returns:
            Device category: 'mobile', 'tablet', 'desktop', or 'large_desktop'
            
        Example:
            >>> manager = ResponsiveLayoutManager()
            >>> category = manager.get_device_category(768)
            >>> print(category)
            'tablet'
        """
        ...
    
    def update_layout(self, screen: Any) -> None:
        """Update layout based on screen.
        
        Args:
            screen: QScreen object containing screen information
            
        Example:
            >>> screen = widget.screen()
            >>> manager.update_layout(screen)
        """
        ...
    
    def get_responsive_settings(self, category: str | None = None) -> dict:
        """Get responsive settings for category.
        
        Args:
            category: Device category, or None for current
            
        Returns:
            Dictionary of responsive settings including:
            - font_size_multiplier: Font size adjustment
            - line_height: Optimal line height
            - padding: Content padding
            - control_size: Size for UI controls
            
        Example:
            >>> settings = manager.get_responsive_settings('mobile')
            >>> print(settings['font_size_multiplier'])
            0.9
        """
        ...
```

## Usage Patterns

### Implementing a Protocol

```python
from teleprompter.protocols import ContentParserProtocol

class CustomParser:
    """Custom content parser implementation."""
    
    def parse(self, content: str) -> str:
        # Custom parsing logic
        return f"<div class='custom'>{content}</div>"
    
    def get_word_count(self, content: str) -> int:
        # Simple word counting
        return len(content.split())

# Protocol is automatically satisfied
assert isinstance(CustomParser(), ContentParserProtocol)
```

### Type Hints with Protocols

```python
def process_content(
    parser: ContentParserProtocol,
    analyzer: HtmlContentAnalyzerProtocol
) -> dict:
    """Process content using parser and analyzer."""
    content = "# Hello World\n\nThis is content."
    html = parser.parse(content)
    return analyzer.analyze_html(html)
```

### Testing with Protocols

```python
from unittest.mock import Mock

def test_scroll_controller():
    # Create mock that satisfies protocol
    mock_controller = Mock(spec=ScrollControllerProtocol)
    mock_controller.get_progress.return_value = 0.5
    
    # Use in tests
    assert mock_controller.get_progress() == 0.5
```

## Best Practices

1. **Program to interfaces**: Use protocol types in function signatures
2. **Keep protocols focused**: Each protocol should have a single responsibility
3. **Use runtime_checkable**: Allows isinstance() checks when needed
4. **Document thoroughly**: Include examples in protocol method docstrings
5. **Version carefully**: Adding methods to protocols is a breaking change

## See Also

- [Architecture Overview](index.md#architecture-overview)
- [Services Documentation](services.md)
- [Testing Guide](../testing.md)