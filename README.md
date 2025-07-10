# Teleprompter

A simple, elegant teleprompter application built with Python and PyQt6. Perfect for content creators, video producers, and anyone who needs to deliver scripted content smoothly.

## Features

- **📄 Markdown Support**: Load and display markdown files with full formatting support
- **🎬 Smooth Scrolling**: Automatic scrolling at 60 FPS for professional-quality teleprompting
- **⚡ Adjustable Speed**: Control scrolling speed from 0.05x to 5x with 0.05 increments
- **🎤 Voice Control**: Automatic start/stop based on voice activity detection
- **🔍 Manual Navigation**: Mouse wheel scrolling with auto-pause functionality
- **🔤 Dynamic Font Sizing**: Adjust text size from 16px to 120px on the fly
- **🖥️ Fullscreen Mode**: Distraction-free fullscreen display for recording
- **⌨️ Keyboard Shortcuts**: Quick controls for efficient operation
- **🎯 Traditional Styling**: Classic white-on-black teleprompter appearance

## Installation

### Prerequisites

- Python 3.13 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/teleprompter.git
cd teleprompter
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage

### Running the Application

```bash
poetry run python -m teleprompter.main
```

Or activate the Poetry shell first:
```bash
poetry shell
python -m teleprompter.main
```

### Basic Operation

1. **Load a Script**: Click "Open File" or press Ctrl+O (Cmd+O on Mac) to load a markdown file
2. **Enable Voice Control** (Optional): Click the 🎤 button to enable voice-activated scrolling
3. **Start Scrolling**: Click the ▶️ button, press Space, or begin speaking (if voice control is enabled)
4. **Adjust Speed**: Use Up/Down arrow keys or the speed spinner (e.g., "1.50x") in the toolbar
5. **Manual Navigation**: Use mouse wheel to scroll to any position (auto-pauses scrolling)
6. **Change Font Size**: Use the font size spinner (e.g., "24px") in the toolbar
7. **Go Fullscreen**: Press F11 or click the fullscreen button for recording mode

### Toolbar Controls

The compact toolbar includes:
- **Open File**: Load markdown scripts
- **▶️/⏸️**: Play/pause button with dynamic icons
- **⏮️**: Reset to beginning button
- **Speed Spinner**: Scrolling speed control (0.05x to 5.00x)
- **Font Size Spinner**: Text size control (16px to 120px)
- **🎤 Voice Control**: Complete voice detection interface
- **Fullscreen**: Distraction-free mode for recording

### Voice Control

The teleprompter includes advanced voice activity detection with a compact toolbar interface:

**🎤 Voice Detection Button**: Toggle voice control and shows activity status
- Gray: Voice detection disabled
- Orange: Voice detection active, listening for speech
- Green: Speech detected, scrolling active
- Red: Voice detection error occurred

**Sens: Slider**: Adjust voice detection sensitivity (0.0-3.0, higher = more sensitive)
**Microphone Dropdown**: Choose your preferred audio input device

**How Voice Control Works:**
- **Starts scrolling** when you begin speaking
- **Stops scrolling** when you pause or stop speaking
- **Resumes from current position** when you continue

**Tips for Best Results:**
- Speak clearly and at a consistent volume
- Adjust sensitivity based on your environment (lower for noisy environments)
- Watch the button color to ensure proper voice detection
- Voice control works alongside all other controls (keyboard, mouse, buttons)

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Space** | Play/Pause scrolling |
| **R** | Reset to beginning |
| **↑** | Increase speed |
| **↓** | Decrease speed |
| **F11** | Toggle fullscreen |
| **Esc** | Exit fullscreen |
| **Ctrl+O** / **Cmd+O** | Open file |

## Supported File Formats

The teleprompter supports standard markdown files with the following extensions:
- `.md`
- `.markdown`
- `.mdown`
- `.mkd`
- `.txt`

Maximum file size: 1MB

## Markdown Formatting

The application supports standard markdown formatting:

- **Headers** (H1-H6)
- **Bold** text
- *Italic* text
- Bulleted lists
- Numbered lists
- [Links](https://example.com)

All text is displayed center-aligned in traditional teleprompter style.

## Configuration

Default settings are optimized for teleprompting but can be adjusted during use:

- **Default Font Size**: 24px
- **Default Speed**: 1.0x
- **Font Family**: Helvetica Neue, Arial, sans-serif
- **Color Scheme**: White text on black background
- **Window Size**: 800x600 (resizable)

## Development

### Project Structure

```
teleprompter/
   src/
      teleprompter/
          __init__.py
          main.py          # Application entry point
          app.py           # Main window and UI
          teleprompter.py  # Core teleprompter widget
          markdown_parser.py # Markdown to HTML conversion
          config.py        # Configuration constants
          voice_detector.py # Voice activity detection
          voice_control_widget.py # Voice control UI
   docs/
      teleprompter-prd.md # Product requirements
   pyproject.toml           # Poetry configuration
   README.md               # This file
```

### Running Tests

```bash
poetry run pytest
```

### Linting

```bash
poetry run ruff check .
```

## Requirements

- Python 3.13+
- PyQt6 6.9.1+
- PyQt6-WebEngine 6.9.0+
- Markdown 3.8.2+
- WebRTC VAD 2.0.10+ (for voice control)
- SoundDevice 0.5.1+ (for voice control)
- NumPy 2.1.3+ (for voice control)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Built with:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Python-Markdown](https://python-markdown.github.io/) - Markdown processing
- [Poetry](https://python-poetry.org/) - Dependency management
- [WebRTC VAD](https://pypi.org/project/webrtcvad/) - Voice activity detection
- [SoundDevice](https://pypi.org/project/sounddevice/) - Audio processing
