"""Main application window and logic."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from . import config
from .container import ServiceContainer
from .file_manager import FileManager
from .protocols import (
    SettingsStorageProtocol,
    StyleProviderProtocol,
)
from .teleprompter import TeleprompterWidget
from .toolbar_manager import ToolbarManager


class TeleprompterApp(QMainWindow):
    """Main application window."""

    def __init__(self, container: ServiceContainer):
        """Initialize the application with dependency injection.

        Args:
            container: The dependency injection container
        """
        super().__init__()

        # Resolve dependencies from container
        self.container = container
        self.settings_manager = container.get(SettingsStorageProtocol)
        self.style_manager = container.get(StyleProviderProtocol)

        # Create file manager with parent reference
        # Note: FileManager needs QWidget parent, so we create it separately
        self.file_manager = FileManager(self)

        # Create toolbar manager with parent reference
        self.toolbar_manager = ToolbarManager(self)

        # Load preferences and setup UI
        self._load_preferences()
        self._setup_ui()
        self._setup_toolbar()
        self._setup_shortcuts()
        self._connect_signals()

    def _load_preferences(self):
        """Load user preferences from settings."""
        preferences = self.settings_manager.load_preferences()

        # Load window geometry
        geometry = preferences.get("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Load speed setting
        config.DEFAULT_SPEED = preferences.get("speed", config.DEFAULT_SPEED)

    def _save_preferences(self):
        """Save user preferences to settings."""
        preferences = {
            "geometry": self.saveGeometry(),
        }

        if hasattr(self, "teleprompter") and hasattr(self.teleprompter, "speed"):
            preferences["speed"] = self.teleprompter.speed

        self.settings_manager.save_preferences(preferences)

    def resizeEvent(self, event):
        """Handle window resize events to ensure toolbar extension button visibility."""
        super().resizeEvent(event)
        # Notify toolbar manager about resize to handle extension button
        if hasattr(self, "toolbar_manager") and self.toolbar_manager:
            # Use a timer to avoid excessive calls during resize
            if not hasattr(self, "_resize_timer"):
                from PyQt6.QtCore import QTimer

                self._resize_timer = QTimer()
                self._resize_timer.setSingleShot(True)
                self._resize_timer.timeout.connect(self._on_resize_finished)
            self._resize_timer.start(200)  # Delay to batch resize events

    def _on_resize_finished(self):
        """Handle completed window resize to update toolbar layout."""
        if hasattr(self, "toolbar_manager") and self.toolbar_manager:
            self.toolbar_manager.force_extension_button_update()

    def closeEvent(self, event):
        """Handle application close event to save preferences."""
        self._save_preferences()
        # Clean up timers
        if hasattr(self, "_resize_timer"):
            self._resize_timer.stop()
        if hasattr(self, "toolbar_manager") and hasattr(
            self.toolbar_manager, "_visibility_timer"
        ):
            self.toolbar_manager._visibility_timer.stop()
        super().closeEvent(event)

    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.DEFAULT_WIDTH, config.DEFAULT_HEIGHT)

        # Apply theme using style manager
        stylesheet = self.style_manager.get_stylesheet("application")
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
