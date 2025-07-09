"""Configuration constants for the teleprompter application."""

# Window settings
WINDOW_TITLE = "Teleprompter"
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

# Text display settings
DEFAULT_FONT_SIZE = 24
MIN_FONT_SIZE = 16
MAX_FONT_SIZE = 120
DEFAULT_FONT_FAMILY = "Helvetica Neue, Arial, sans-serif"

# Colors (traditional teleprompter style)
BACKGROUND_COLOR = "#000000"  # Black
TEXT_COLOR = "#FFFFFF"  # White

# Scrolling settings
DEFAULT_SPEED = 0.3  # 1x speed
MIN_SPEED = 0.05
MAX_SPEED = 5.0
SPEED_INCREMENT = 0.05
SCROLL_FPS = 60  # Target frames per second

# File settings
MARKDOWN_EXTENSIONS = ["*.md", "*.markdown", "*.mdown", "*.mkd"]
MAX_FILE_SIZE = 1024 * 1024  # 1MB

# Voice activity detection settings
VAD_ENABLED_DEFAULT = False
VAD_SENSITIVITY = 1  # WebRTC VAD aggressiveness (0-3, higher = more aggressive)
VAD_SAMPLE_RATE = 16000  # Sample rate for audio processing
VAD_FRAME_DURATION = 30  # Frame duration in milliseconds (10, 20, or 30)
VAD_START_DELAY = 0.5  # Seconds before considering speech as started
VAD_STOP_DELAY = 1.0  # Seconds to wait after silence before stopping
VAD_BUFFER_SIZE = 480  # Audio buffer size (sample_rate * frame_duration / 1000)
