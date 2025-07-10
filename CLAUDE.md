# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Teleprompter - A professional-grade teleprompter application built with PyQt6 and Python 3.13+. The application provides smooth scrolling text display with voice activity detection, making it ideal for content creators, presenters, and video producers.

## Development Commands

### Environment Setup
```bash
poetry install              # Install all dependencies
poetry shell               # Activate virtual environment
```

### Running the Application
```bash
poetry run python -m teleprompter.main    # Run the main application
poetry poe run                           # Alternative using task runner
```

### Code Quality Commands
```bash
poetry poe lint             # Run ruff linter and fix issues
poetry poe format           # Format code using ruff
poetry poe check            # Run both linting and formatting
```

## Project Structure

### Core Components
- `src/teleprompter/main.py` - Application entry point
- `src/teleprompter/app.py` - Main application window (`TeleprompterApp`)
- `src/teleprompter/teleprompter.py` - Core teleprompter widget with scrolling logic
- `src/teleprompter/config.py` - Application-wide configuration constants

### Managers
- `src/teleprompter/file_manager.py` - File loading and validation
- `src/teleprompter/markdown_parser.py` - Markdown to HTML conversion
- `src/teleprompter/settings_manager.py` - User preferences persistence
- `src/teleprompter/toolbar_manager.py` - Toolbar creation and management
- `src/teleprompter/style_manager.py` - Centralized styling system
- `src/teleprompter/icon_manager.py` - Icon management

### UI Components
- `src/teleprompter/custom_widgets.py` - Custom PyQt6 widgets
- `src/teleprompter/voice_control_widget.py` - Voice control settings UI

### Voice Control
- `src/teleprompter/voice_detector.py` - Voice activity detection using WebRTC VAD

## Key Features

### Display & Rendering
- Web-based rendering using QWebEngineView for smooth text display
- 60 FPS scrolling animation
- Adjustable speed (0.05x to 5x)
- Dynamic font sizing (16px to 120px)
- Traditional white-on-black teleprompter styling
- Progress bar and reading time estimation

### Input Methods
- **Keyboard**: Space (play/pause), arrows (speed adjustment)
- **Mouse**: Wheel scrolling with auto-pause
- **Voice**: Activity detection for hands-free control
- **Toolbar**: Full control through GUI buttons

### Advanced Features
- Section navigation (previous/next based on markdown headers)
- Reading statistics (word count, time estimates)
- Responsive design for different screen sizes
- Auto-hide cursor during reading
- Markdown file support with custom styling

## Technical Stack

### Core Dependencies
- **PyQt6** - GUI framework
- **PyQt6-WebEngine** - HTML rendering engine
- **markdown** - Markdown to HTML conversion
- **webrtc-vad** - Voice activity detection
- **sounddevice** - Audio input processing
- **numpy** - Audio data handling

### Development Tools
- **Poetry** - Dependency management
- **Ruff** - Linting and code formatting
- **Poethepoet** - Task automation

## Architecture Notes

### Design Patterns
- **Signal/Slot Architecture**: PyQt signals for loose coupling between components
- **Manager Pattern**: Separate managers for different concerns
- **Configuration-driven**: Centralized config for easy customization

### Conventions
- All UI styling is centralized in `StyleManager`
- Icons use Unicode symbols (no external resources)
- Markdown is the primary content format
- User settings are persisted between sessions
- Voice detection runs in a separate thread

## Important Notes

- This is a Poetry-managed project, all dependencies should be added via `poetry add`
- Python 3.13+ is required
- The project is licensed under MIT
- When adding new Python modules, ensure `__init__.py` files exist in package directories
- Use `poetry poe` commands for development tasks
- The application uses QWebEngineView which requires a compatible graphics environment