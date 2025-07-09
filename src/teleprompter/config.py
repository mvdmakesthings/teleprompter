"""Configuration constants for the teleprompter application."""

# Window settings
WINDOW_TITLE = "Teleprompter"
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

# Text display settings
DEFAULT_FONT_SIZE = 24
MIN_FONT_SIZE = 16
MAX_FONT_SIZE = 120

# Enhanced font system
FONT_FAMILIES = {
    "default": "Helvetica Neue, Arial, sans-serif",
    "modern": "Source Sans Pro, system-ui, -apple-system, sans-serif",
    "readable": "Open Sans, Segoe UI, Roboto, sans-serif",
    "classic": "Georgia, Times New Roman, serif",
}
DEFAULT_FONT_FAMILY = FONT_FAMILIES["default"]

# Font presets for different viewing distances
FONT_PRESETS = {
    "close": {"size": 18, "line_height": 1.4, "weight": "400"},
    "medium": {"size": 24, "line_height": 1.5, "weight": "400"},
    "far": {"size": 36, "line_height": 1.6, "weight": "500"},
    "presentation": {"size": 48, "line_height": 1.7, "weight": "600"},
}

# Color themes for different contrast needs
COLOR_THEMES = {
    "standard": {"background": "#000000", "text": "#FFFFFF", "accent": "#4A90E2"},
    "high_contrast": {"background": "#000000", "text": "#FFFFFF", "accent": "#FFFF00"},
    "low_light": {"background": "#1A1A1A", "text": "#E8E8E8", "accent": "#6A9BD8"},
    "warm": {"background": "#0F0A05", "text": "#FFF8F0", "accent": "#FFB366"},
}

# Current theme selection
DEFAULT_THEME = "standard"
BACKGROUND_COLOR = COLOR_THEMES[DEFAULT_THEME]["background"]
TEXT_COLOR = COLOR_THEMES[DEFAULT_THEME]["text"]
ACCENT_COLOR = COLOR_THEMES[DEFAULT_THEME]["accent"]

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
VAD_SENSITIVITY = 1.5  # Voice detection sensitivity (0.0-3.0, higher = more sensitive)
VAD_SAMPLE_RATE = 16000  # Sample rate for audio processing
VAD_FRAME_DURATION = 30  # Frame duration in milliseconds (10, 20, or 30)
VAD_START_DELAY = 0.5  # Seconds before considering speech as started
VAD_STOP_DELAY = 1.0  # Seconds to wait after silence before stopping
VAD_BUFFER_SIZE = 480  # Audio buffer size (sample_rate * frame_duration / 1000)

# Phase 4: Material Design Integration
MATERIAL_ELEVATION_LEVELS = {
    "flat": 0,
    "low": 2,
    "medium": 4,
    "high": 8,
    "very_high": 16,
}

MATERIAL_SHADOWS = {
    "flat": "none",
    "low": "0 2px 4px rgba(0, 0, 0, 0.2)",
    "medium": "0 4px 8px rgba(0, 0, 0, 0.25)",
    "high": "0 8px 16px rgba(0, 0, 0, 0.3)",
    "very_high": "0 16px 32px rgba(0, 0, 0, 0.35)",
}

MATERIAL_BORDER_RADIUS = {
    "small": 4,
    "medium": 8,
    "large": 12,
    "extra_large": 16,
}

# Primary and secondary color palette
PRIMARY_COLORS = {
    "50": "#e3f2fd",
    "100": "#bbdefb",
    "200": "#90caf9",
    "300": "#64b5f6",
    "400": "#42a5f5",
    "500": "#2196f3",  # Primary
    "600": "#1e88e5",
    "700": "#1976d2",
    "800": "#1565c0",
    "900": "#0d47a1",
}

SECONDARY_COLORS = {
    "50": "#f3e5f5",
    "100": "#e1bee7",
    "200": "#ce93d8",
    "300": "#ba68c8",
    "400": "#ab47bc",
    "500": "#9c27b0",  # Secondary
    "600": "#8e24aa",
    "700": "#7b1fa2",
    "800": "#6a1b9a",
    "900": "#4a148c",
}

# Phase 4.3: Responsive Design Breakpoints
BREAKPOINTS = {
    "mobile": 480,
    "tablet": 768,
    "desktop": 1024,
    "large_desktop": 1440,
}
