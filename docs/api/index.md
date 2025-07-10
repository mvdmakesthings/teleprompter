# Teleprompter API Documentation

## Overview

The Teleprompter application is built with a modular architecture following Domain-Driven Design (DDD) principles. This documentation covers the public APIs, protocols, and key components.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Protocols](#core-protocols)
3. [Services](#services)
4. [UI Components](#ui-components)
5. [Dependency Injection](#dependency-injection)
6. [Configuration](#configuration)

## Architecture Overview

The application is structured into several layers:

```
src/teleprompter/
├── core/           # Business logic and protocols
├── domain/         # Domain models (future)
├── ui/             # User interface components
│   ├── widgets/    # Custom widgets
│   ├── managers/   # UI managers
│   └── builders/   # UI builders
├── config.py       # Configuration
└── container.py    # Dependency injection
```

## Core Protocols

### FileManagerProtocol

Handles file operations with loading states and error handling.

```python
class FileManagerProtocol(Protocol):
    """Protocol for file management operations."""
    
    def load_file(self, file_path: str) -> str:
        """Load content from a file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
    
    def save_file(self, file_path: str, content: str) -> bool:
        """Save content to a file.
        
        Args:
            file_path: Path where to save the file
            content: Content to save
            
        Returns:
            True if successful, False otherwise
        """
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if file is valid and can be loaded
        """
```

### ContentParserProtocol

Handles content parsing and transformation.

```python
class ContentParserProtocol(Protocol):
    """Protocol for content parsing implementations."""
    
    def parse(self, content: str) -> str:
        """Parse content and return formatted output.
        
        Args:
            content: Raw content to parse
            
        Returns:
            Parsed content (typically HTML)
        """
    
    def get_word_count(self, content: str) -> int:
        """Get word count from content.
        
        Args:
            content: Content to count words in
            
        Returns:
            Number of words
        """
```

### ScrollControllerProtocol

Manages scrolling behavior and position tracking.

```python
class ScrollControllerProtocol(Protocol):
    """Protocol for scroll control implementations."""
    
    def start_scrolling(self) -> None:
        """Start automatic scrolling."""
    
    def stop_scrolling(self) -> None:
        """Stop scrolling and reset position."""
    
    def pause_scrolling(self) -> None:
        """Pause scrolling without resetting position."""
    
    def set_speed(self, speed: float) -> None:
        """Set scrolling speed.
        
        Args:
            speed: Speed multiplier (1.0 = normal, 2.0 = 2x speed)
        """
    
    def get_progress(self) -> float:
        """Get current progress.
        
        Returns:
            Progress as float between 0.0 and 1.0
        """
```

### ReadingMetricsProtocol

Calculates reading statistics and time estimates.

```python
class ReadingMetricsProtocol(Protocol):
    """Protocol for reading metrics calculations."""
    
    def calculate_reading_time(self, word_count: int, wpm: float) -> float:
        """Calculate estimated reading time in seconds.
        
        Args:
            word_count: Number of words
            wpm: Words per minute
            
        Returns:
            Reading time in seconds
        """
    
    def calculate_words_per_minute(self, speed: float) -> float:
        """Calculate effective words per minute based on scroll speed.
        
        Args:
            speed: Scroll speed multiplier
            
        Returns:
            Effective words per minute
        """
```

## Services

### ScrollController

Manages scrolling animation and position tracking.

```python
class ScrollController:
    """Controls scrolling behavior and animations."""
    
    def __init__(self):
        """Initialize scroll controller with default settings."""
    
    def set_viewport_dimensions(self, viewport_height: int, content_height: int):
        """Set viewport and content dimensions.
        
        Args:
            viewport_height: Height of visible area
            content_height: Total height of content
        """
    
    def calculate_next_position(self, delta_time: float) -> float:
        """Calculate next scroll position based on time delta.
        
        Args:
            delta_time: Time elapsed since last frame
            
        Returns:
            Next scroll position in pixels
        """
```

### ReadingMetricsService

Tracks reading progress and calculates statistics.

```python
class ReadingMetricsService:
    """Service for calculating reading metrics and statistics."""
    
    def set_word_count(self, count: int):
        """Set total word count for the document.
        
        Args:
            count: Total number of words
        """
    
    def start_reading(self):
        """Start tracking reading time."""
    
    def pause_reading(self):
        """Pause reading time tracking."""
    
    def get_average_wpm(self) -> float:
        """Get average reading speed.
        
        Returns:
            Average words per minute
        """
```

### ContentManager

Manages content loading and transformation.

```python
class ContentManager:
    """Manages content loading, parsing, and caching."""
    
    def load_markdown(self, content: str):
        """Load markdown content.
        
        Args:
            content: Markdown content to load
        """
    
    def get_html(self) -> str:
        """Get content as HTML.
        
        Returns:
            HTML representation of content
        """
    
    def get_plain_text(self) -> str:
        """Get content as plain text.
        
        Returns:
            Plain text without formatting
        """
```

## UI Components

### TeleprompterWidget

Main widget for displaying and scrolling content.

```python
class TeleprompterWidget(QWidget):
    """Main teleprompter display widget."""
    
    # Signals
    speed_changed = pyqtSignal(float)
    voice_activity_changed = pyqtSignal(bool)
    progress_changed = pyqtSignal(float)
    reading_stats_changed = pyqtSignal(dict)
    file_loaded = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def load_content(self, html_content: str):
        """Load HTML content for display.
        
        Args:
            html_content: HTML content to display
        """
    
    def load_file(self, file_path: str):
        """Load content from file.
        
        Args:
            file_path: Path to file to load
        """
    
    def play(self):
        """Start scrolling."""
    
    def pause(self):
        """Pause scrolling."""
    
    def set_speed(self, speed: float):
        """Set scroll speed.
        
        Args:
            speed: Speed multiplier (0.05 to 5.0)
        """
    
    def set_font_size(self, size: int):
        """Set display font size.
        
        Args:
            size: Font size in pixels (16 to 120)
        """
```

### KeyboardCommandRegistry

Manages keyboard shortcuts and commands.

```python
class KeyboardCommandRegistry:
    """Registry for keyboard commands with key mapping."""
    
    def register_command(self, key: Qt.Key, command: KeyboardCommand):
        """Register a custom keyboard command.
        
        Args:
            key: Qt key to bind to
            command: Command to execute
        """
    
    def handle_key_press(self, event: QKeyEvent, widget) -> bool:
        """Handle a key press event.
        
        Args:
            event: Key press event
            widget: Widget that received the event
            
        Returns:
            True if event was handled
        """
```

### ContentLoader

Handles asynchronous content loading.

```python
class ContentLoader(QObject):
    """Handles content loading and processing."""
    
    # Signals
    content_loaded = pyqtSignal(ContentLoadResult)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()
    
    def load_file(self, file_path: str):
        """Load content from file asynchronously.
        
        Args:
            file_path: Path to file to load
        """
    
    def load_text(self, text: str):
        """Load content from plain text.
        
        Args:
            text: Text content to load
        """
```

## Dependency Injection

The application uses a simple dependency injection container.

### Registering Services

```python
from teleprompter.container import get_container

container = get_container()
container.register(ProtocolType, ImplementationType)
container.register_instance(ProtocolType, instance)
container.register_factory(ProtocolType, factory_function)
```

### Retrieving Services

```python
service = container.get(ProtocolType)
```

### Using the @inject Decorator

```python
from teleprompter.container import inject

@inject
def my_function(file_manager: FileManagerProtocol):
    # file_manager is automatically injected
    content = file_manager.load_file("example.md")
```

## Configuration

Application configuration is centralized in `config.py`.

### Key Configuration Values

```python
# Display settings
DEFAULT_FONT_SIZE = 24
MIN_FONT_SIZE = 16
MAX_FONT_SIZE = 120

# Scrolling settings
DEFAULT_SPEED = 1.0
MIN_SPEED = 0.05
MAX_SPEED = 5.0
SPEED_INCREMENT = 0.1
BASE_SCROLL_SPEED = 100  # pixels per second
SCROLL_FPS = 60

# File settings
MARKDOWN_EXTENSIONS = ["*.md", "*.markdown", "*.mdown", "*.mkd", "*.mdwn"]

# Voice control
VOICE_SAMPLE_RATE = 16000
VOICE_CHUNK_DURATION_MS = 30
```

### Environment Variables

The application supports the following environment variables:

- `TELEPROMPTER_CONFIG_DIR`: Directory for configuration files
- `TELEPROMPTER_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `TELEPROMPTER_THEME`: UI theme (light, dark)

## Usage Examples

### Basic Usage

```python
from teleprompter.ui.app import TeleprompterApp
from teleprompter.container import configure_container

# Configure services
configure_container()

# Create and run application
app = TeleprompterApp()
app.show()

# Load a file
app.file_manager.load_file("document.md")

# Start scrolling
app.teleprompter_widget.play()
```

### Custom Keyboard Command

```python
from teleprompter.ui.widgets.keyboard_commands import KeyboardCommand

class CustomCommand(KeyboardCommand):
    def execute(self, widget):
        widget.set_speed(2.0)
        return True
    
    def description(self):
        return "Set speed to 2x"

# Register command
widget.keyboard_commands.register_command(Qt.Key.Key_2, CustomCommand())
```

### Custom Content Parser

```python
from teleprompter.protocols import ContentParserProtocol

class CustomParser:
    def parse(self, content: str) -> str:
        # Custom parsing logic
        return f"<div>{content}</div>"
    
    def get_word_count(self, content: str) -> int:
        return len(content.split())

# Register custom parser
container.register(ContentParserProtocol, CustomParser)
```

## Error Handling

The application uses signals for error reporting:

```python
def handle_error(message: str, error_type: str):
    print(f"Error ({error_type}): {message}")

app.file_manager.error_occurred.connect(handle_error)
```

## Performance Considerations

1. **Scrolling**: Uses requestAnimationFrame for smooth 60 FPS scrolling
2. **Content Loading**: Asynchronous loading prevents UI blocking
3. **Memory**: Content caching with LRU eviction
4. **JavaScript**: Batched operations to minimize IPC overhead

## Testing

The application includes comprehensive test suites:

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Performance tests: `tests/performance/`

Run tests with:
```bash
poetry run pytest
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## License

This project is licensed under the MIT License.