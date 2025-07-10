"""Main application window and logic."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from . import config
from .file_manager import FileManager
from .settings_manager import SettingsManager
from .style_manager import StyleManager
from .teleprompter import TeleprompterWidget
from .toolbar_manager import ToolbarManager


class TeleprompterApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Initialize managers
        self.settings_manager = SettingsManager()
        self.file_manager = FileManager(self)
        self.style_manager = StyleManager()
        self.toolbar_manager = ToolbarManager(self)

        # Initialize state
        self.current_font_preset_index = 0
        self.current_theme_index = 0

        # Load preferences and setup UI
        self._load_preferences()
        self._setup_ui()
        self._setup_toolbar()
        self._setup_shortcuts()
        self._connect_signals()

    def _load_preferences(self):
        """Load user preferences from settings."""
        preferences = self.settings_manager.load_preferences()

        self.current_font_preset_index = preferences.get("font_preset_index", 0)
        self.current_theme_index = preferences.get("theme_index", 0)

        # Load window geometry
        geometry = preferences.get("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Load speed setting
        config.DEFAULT_SPEED = preferences.get("speed", config.DEFAULT_SPEED)

        # Set initial values in toolbar manager
        self.toolbar_manager.set_font_preset_index(self.current_font_preset_index)
        self.toolbar_manager.set_theme_index(self.current_theme_index)

    def _save_preferences(self):
        """Save user preferences to settings."""
        preferences = {
            "font_preset_index": self.current_font_preset_index,
            "theme_index": self.current_theme_index,
            "geometry": self.saveGeometry(),
        }

        if hasattr(self, "teleprompter") and hasattr(self.teleprompter, "speed"):
            preferences["speed"] = self.teleprompter.speed

        self.settings_manager.save_preferences(preferences)

    def closeEvent(self, event):
        """Handle application close event to save preferences."""
        self._save_preferences()
        super().closeEvent(event)

    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.DEFAULT_WIDTH, config.DEFAULT_HEIGHT)

        # Apply theme using style manager
        stylesheet = self.style_manager.get_application_stylesheet()
        self.setStyleSheet(stylesheet)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Teleprompter widget
        self.teleprompter = TeleprompterWidget()
        layout.addWidget(self.teleprompter)

        # Load initial content
        empty_state_html = self.file_manager.get_empty_state_html()
        self.teleprompter.load_content(empty_state_html)

        # Give focus to teleprompter widget
        self.teleprompter.setFocus()

    def _setup_toolbar(self):
        """Set up the toolbar using the toolbar manager."""
        toolbar = self.toolbar_manager.create_toolbar()
        self.addToolBar(toolbar)

    def _connect_signals(self):
        """Connect signals between components."""
        # Connect teleprompter signals
        self.teleprompter.speed_changed.connect(self._on_speed_changed)
        self.teleprompter.voice_activity_changed.connect(
            self._on_voice_activity_changed
        )
        self.teleprompter.progress_changed.connect(self._on_progress_changed)
        self.teleprompter.reading_stats_changed.connect(self._on_reading_stats_changed)

        # Connect file manager signals
        self.file_manager.loading_started.connect(self._on_loading_started)
        self.file_manager.loading_finished.connect(self._on_loading_finished)
        self.file_manager.file_loaded.connect(self._on_file_loaded)
        self.file_manager.error_occurred.connect(self._on_file_error)

        # Connect toolbar manager signals
        self.toolbar_manager.open_file_requested.connect(
            self.file_manager.open_file_dialog
        )
        self.toolbar_manager.playback_toggled.connect(self._toggle_playback)
        self.toolbar_manager.reset_requested.connect(self._reset_and_focus)
        self.toolbar_manager.speed_changed.connect(self._on_speed_spinner_changed)
        self.toolbar_manager.font_size_changed.connect(self._on_font_size_changed)
        self.toolbar_manager.font_preset_cycled.connect(self._cycle_font_preset)
        self.toolbar_manager.color_theme_cycled.connect(self._cycle_color_theme)
        self.toolbar_manager.presentation_mode_toggled.connect(
            self._toggle_presentation_mode
        )
        self.toolbar_manager.fullscreen_toggled.connect(self.toggle_fullscreen)
        self.toolbar_manager.previous_section_requested.connect(
            self._goto_previous_section
        )
        self.toolbar_manager.next_section_requested.connect(self._goto_next_section)
        self.toolbar_manager.voice_detection_toggled.connect(
            self._on_voice_detection_enabled
        )

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Space for play/pause
        play_action = QAction("Play/Pause", self)
        play_action.setShortcut(Qt.Key.Key_Space)
        play_action.triggered.connect(self._toggle_playback)
        self.addAction(play_action)

        # R for reset
        reset_action = QAction("Reset", self)
        reset_action.setShortcut(Qt.Key.Key_R)
        reset_action.triggered.connect(self._reset_and_focus)
        self.addAction(reset_action)

        # Up arrow for speed increase
        speed_up_action = QAction("Speed Up", self)
        speed_up_action.setShortcut(Qt.Key.Key_Up)
        speed_up_action.triggered.connect(self._increase_speed)
        self.addAction(speed_up_action)

        # Down arrow for speed decrease
        speed_down_action = QAction("Speed Down", self)
        speed_down_action.setShortcut(Qt.Key.Key_Down)
        speed_down_action.triggered.connect(self._decrease_speed)
        self.addAction(speed_down_action)

        # F11 for fullscreen
        fullscreen_action = QAction("Fullscreen", self)
        fullscreen_action.setShortcut(Qt.Key.Key_F11)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(fullscreen_action)

        # Escape to exit fullscreen
        exit_fullscreen_action = QAction("Exit Fullscreen", self)
        exit_fullscreen_action.setShortcut(Qt.Key.Key_Escape)
        exit_fullscreen_action.triggered.connect(self.exit_fullscreen)
        self.addAction(exit_fullscreen_action)

        # Ctrl+O for open file
        open_action = QAction("Open File", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.file_manager.open_file_dialog)
        self.addAction(open_action)

    # File manager signal handlers
    def _on_loading_started(self):
        """Handle loading start from file manager."""
        # Could show loading indicator in status bar
        pass

    def _on_loading_finished(self):
        """Handle loading finished from file manager."""
        # Could hide loading indicator
        pass

    def _on_file_loaded(self, html_content: str, file_path: str, markdown_content: str):
        """Handle successful file load from file manager."""
        self.teleprompter.load_content(html_content)
        self.setWindowTitle(f"{config.WINDOW_TITLE} - {file_path.split('/')[-1]}")
        self.teleprompter.reset()
        self.teleprompter.ensure_focus()

    def _on_file_error(self, error_message: str, error_type: str):
        """Handle file loading error from file manager."""
        # File manager handles showing error dialog, we just need to ensure focus
        self.teleprompter.ensure_focus()

    def _reset_and_focus(self):
        """Reset teleprompter and ensure focus."""
        self.teleprompter.reset()
        self.teleprompter.ensure_focus()

    def _toggle_playback(self):
        """Toggle play/pause."""
        self.teleprompter.toggle_playback()
        self.toolbar_manager.update_play_button_icon(self.teleprompter.is_playing)
        self.teleprompter.ensure_focus()

    def _on_speed_spinner_changed(self, speed: float):
        """Handle speed spinner change."""
        self.teleprompter.set_speed(speed)

    def _on_speed_changed(self, speed: float):
        """Handle speed change from teleprompter (keyboard shortcuts)."""
        self.toolbar_manager.update_speed_display(speed)

    def _on_font_size_changed(self, size: int):
        """Handle font size change."""
        self.teleprompter.set_font_size(size)

    def _cycle_font_preset(self):
        """Cycle through font presets for different viewing distances."""
        preset_name = self.toolbar_manager.cycle_font_preset()
        self.current_font_preset_index = self.toolbar_manager.current_font_preset_index

        # Apply the preset
        self.teleprompter.set_font_preset(preset_name)

        # Update the font size spinner to reflect the preset size
        preset_size = config.FONT_PRESETS[preset_name]["size"]
        self.toolbar_manager.update_font_size_display(preset_size)

    def _cycle_color_theme(self):
        """Cycle through color themes for different contrast needs."""
        theme_name = self.toolbar_manager.cycle_color_theme()
        self.current_theme_index = self.toolbar_manager.current_theme_index

        # Apply the theme
        self.teleprompter.set_color_theme(theme_name)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()

    def _on_voice_detection_enabled(self, enabled: bool):
        """Handle voice detection enable/disable."""
        # Delegate to toolbar manager for voice control widget management
        if enabled:
            voice_detector = self.toolbar_manager.get_voice_detector()
            self.teleprompter.set_voice_detector(voice_detector)
        else:
            self.teleprompter.set_voice_detector(None)

        self.teleprompter.enable_voice_control(enabled)

    def _on_voice_activity_changed(self, is_active: bool):
        """Handle voice activity status change."""
        # Update play button icon when voice controls the teleprompter
        self.toolbar_manager.update_play_button_icon(self.teleprompter.is_playing)

    def _on_progress_changed(self, progress: float):
        """Handle progress change from teleprompter."""
        # This could be used to update a progress indicator in the UI
        # For now, we'll just store it for potential future use
        pass

    def _on_reading_stats_changed(self, stats: dict):
        """Handle reading statistics change from teleprompter."""
        # This could be used to display reading information in the status bar
        # For example: word count, estimated time, sections, etc.
        pass

    def _goto_previous_section(self):
        """Navigate to the previous section."""
        self.teleprompter.navigate_to_previous_section()
        self.teleprompter.setFocus()

    def _goto_next_section(self):
        """Navigate to the next section."""
        self.teleprompter.navigate_to_next_section()
        self.teleprompter.setFocus()

    def _toggle_presentation_mode(self):
        """Toggle presentation mode for distraction-free reading."""
        self.teleprompter.toggle_presentation_mode()
        self.teleprompter.setFocus()

    def _increase_speed(self):
        """Increase scrolling speed."""
        self.teleprompter.adjust_speed(config.SPEED_INCREMENT)

    def _decrease_speed(self):
        """Decrease scrolling speed."""
        self.teleprompter.adjust_speed(-config.SPEED_INCREMENT)

    def _reset_and_focus(self):
        """Reset teleprompter and ensure focus."""
        self.teleprompter.reset()
        self.teleprompter.ensure_focus()
