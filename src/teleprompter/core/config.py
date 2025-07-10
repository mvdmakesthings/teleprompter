"""Application configuration constants."""

# Application Identity
APPLICATION_NAME = "Teleprompter"
APPLICATION_VERSION = "1.0.0"
ORGANIZATION_NAME = "Teleprompter"

# Window Configuration
WINDOW_TITLE = "Teleprompter"
DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 700
MIN_WIDTH = 600
MIN_HEIGHT = 400

# Teleprompter Display
DEFAULT_FONT_SIZE = 24
DEFAULT_FONT_FAMILY = "Arial, sans-serif"
MIN_FONT_SIZE = 16
MAX_FONT_SIZE = 120

# Colors
BACKGROUND_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#4A90E2"

# Primary color variants
PRIMARY_COLORS = {
    "300": "#64b5f6",
    "400": "#42a5f5",
    "500": "#2196f3",
    "600": "#1e88e5",
    "700": "#1976d2",
    "800": "#1565c0"
}

# Scrolling
DEFAULT_SPEED = 1.0
MIN_SPEED = 0.05
MAX_SPEED = 5.0
SPEED_INCREMENT = 0.1

# Voice Detection
VAD_SAMPLE_RATE = 16000
VAD_FRAME_DURATION = 30  # milliseconds
VAD_SENSITIVITY = 1
VAD_START_DELAY = 0.3  # seconds
VAD_STOP_DELAY = 1.0   # seconds
VAD_ENABLED_DEFAULT = False  # Voice detection disabled by default

# File Handling
MAX_FILE_SIZE = 1048576  # 1MB in bytes
SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.txt']

# Animation
ANIMATION_DURATION = 200  # milliseconds
SCROLL_TIMER_INTERVAL = 16  # ~60 FPS
SCROLL_FPS = 60  # Frames per second for scrolling

# Network
NETWORK_TIMEOUT = 5000  # milliseconds

# Toolbar
TOOLBAR_HEIGHT = 40
TOOLBAR_ICON_SIZE = 20

# Settings Keys
SETTINGS_GEOMETRY = "geometry"
SETTINGS_SPEED = "speed"
SETTINGS_FONT_SIZE = "font_size"
SETTINGS_VOICE_ENABLED = "voice_enabled"
SETTINGS_VOICE_SENSITIVITY = "voice_sensitivity"

# Font families
FONT_FAMILIES = ["Arial", "Helvetica", "sans-serif"]

# Material design border radius
MATERIAL_BORDER_RADIUS = {
    "small": 4,
    "medium": 6,
    "large": 8
}
