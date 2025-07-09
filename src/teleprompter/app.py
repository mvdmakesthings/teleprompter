"""Main application window and logic."""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from . import config
from .custom_widgets import IconDoubleSpinBox, IconSpinBox
from .icon_manager import icon_manager
from .markdown_parser import MarkdownParser
from .teleprompter import TeleprompterWidget
from .voice_control_widget import VoiceControlWidget


class TeleprompterApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.parser = MarkdownParser()
        self.current_file = None
        self.current_markdown_content = ""

        self._setup_ui()
        self._setup_toolbar()
        self._setup_shortcuts()
        self._setup_button_hover_effects()
        self._setup_button_hover_effects()

    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.DEFAULT_WIDTH, config.DEFAULT_HEIGHT)

        # Apply modern dark theme
        self._apply_modern_theme()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Teleprompter widget
        self.teleprompter = TeleprompterWidget()
        self.teleprompter.speed_changed.connect(self._on_speed_changed)
        self.teleprompter.voice_activity_changed.connect(
            self._on_voice_activity_changed
        )
        layout.addWidget(self.teleprompter)

        # Load initial content
        self._load_welcome_content()

        # Give focus to teleprompter widget
        self.teleprompter.setFocus()

    def _apply_modern_theme(self):
        """Apply minimal flat dark theme with gun metal grey colors."""
        self.setStyleSheet("""
            /* Main window styling */
            QMainWindow {
                background-color: #0f0f0f;
                color: #e0e0e0;
            }

            /* Toolbar styling */
            QToolBar {
                background-color: #1a1a1a;
                border: none;
                border-bottom: 1px solid #333333;
                padding: 2px;
                spacing: 4px;
                font-size: 12px;
                font-weight: normal;
            }

            QToolBar::separator {
                background-color: #333333;
                width: 1px;
                margin: 2px 4px;
            }

            /* Button styling */
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #c0c0c0;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: normal;
                min-height: 20px;
                min-width: 24px;
            }

            QPushButton:hover {
                background-color: #363636;
                border-color: #0078d4;
                color: #ffffff;
            }

            QPushButton:pressed {
                background-color: #0078d4;
                border-color: #106ebe;
                color: #ffffff;
            }

            /* Modern action button styling for play/pause and reset */
            QPushButton#playButton, QPushButton#resetButton {
                background-color: #333333;
                border: 1px solid #4a4a4a;
                padding: 8px;
                min-width: 36px;
                min-height: 24px;
                border-radius: 4px;
            }

            QPushButton#playButton:hover, QPushButton#resetButton:hover {
                background-color: #404040;
                border-color: #0078d4;
                color: #ffffff;
            }

            QPushButton#playButton:pressed, QPushButton#resetButton:pressed {
                background-color: #0078d4;
                border-color: #106ebe;
            }

            /* Spinbox styling */
            QSpinBox, QDoubleSpinBox {
                background-color: #262626;
                border: 1px solid #404040;
                border-radius: 2px;
                color: #e0e0e0;
                padding: 2px 4px;
                font-size: 12px;
                min-width: 50px;
                max-width: 65px;
                min-height: 18px;
            }

            QSpinBox:hover, QDoubleSpinBox:hover {
                border-color: #505050;
                background-color: #2e2e2e;
            }

            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #0078d4;
                background-color: #2e2e2e;
            }
        """)

    def _setup_toolbar(self):
        """Set up the toolbar with modern controls inspired by professional video software."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        # File section
        open_action = QAction("Open File", self)
        open_action.setToolTip("Open markdown file (Ctrl+O)")
        open_action.triggered.connect(self.open_file)

        # Set icon for open action
        open_pixmap = icon_manager.get_themed_pixmap("folder-open", "default", "medium")
        if not open_pixmap.isNull():
            open_action.setIcon(QIcon(open_pixmap))
        else:
            open_action.setText("📁 Open File")  # Fallback to emoji

        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Transport controls section
        # Play/Pause button with modern styling
        self.play_button = QPushButton()
        self.play_button.setObjectName("playButton")
        self.play_button.setToolTip("Play/Pause scrolling (Space)")
        self.play_button.clicked.connect(self._toggle_playback)

        # Set play icon
        self._update_play_button_icon()

        toolbar.addWidget(self.play_button)

        # Reset button
        reset_button = QPushButton()
        reset_button.setObjectName("resetButton")
        reset_button.setToolTip("Reset to beginning (R)")
        reset_button.clicked.connect(self._reset_and_focus)

        # Set reset icon
        reset_pixmap = icon_manager.get_themed_pixmap("skip-back", "default", "medium")
        if not reset_pixmap.isNull():
            reset_button.setIcon(QIcon(reset_pixmap))
        else:
            reset_button.setText("⏮")  # Fallback to emoji

        toolbar.addWidget(reset_button)

        toolbar.addSeparator()

        # Speed control section
        speed_label = QPushButton("Speed")
        speed_label.setEnabled(False)
        speed_label.setStyleSheet("""
            QPushButton:disabled {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 11px;
                font-weight: normal;
                padding: 2px 4px;
            }
        """)
        toolbar.addWidget(speed_label)

        self.speed_spin = IconDoubleSpinBox()
        self.speed_spin.setMinimum(config.MIN_SPEED)
        self.speed_spin.setMaximum(config.MAX_SPEED)
        self.speed_spin.setValue(config.DEFAULT_SPEED)
        self.speed_spin.setSuffix("x")
        self.speed_spin.setDecimals(2)
        self.speed_spin.setSingleStep(config.SPEED_INCREMENT)
        self.speed_spin.setToolTip("Scrolling speed (↑↓ arrows)")
        self.speed_spin.valueChanged.connect(self._on_speed_spinner_changed)
        toolbar.addWidget(self.speed_spin)

        toolbar.addSeparator()

        # Font size control section
        font_label = QPushButton("Font")
        font_label.setEnabled(False)
        font_label.setStyleSheet("""
            QPushButton:disabled {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 11px;
                font-weight: normal;
                padding: 2px 4px;
            }
        """)
        toolbar.addWidget(font_label)

        self.font_size_spin = IconSpinBox()
        self.font_size_spin.setMinimum(config.MIN_FONT_SIZE)
        self.font_size_spin.setMaximum(config.MAX_FONT_SIZE)
        self.font_size_spin.setValue(config.DEFAULT_FONT_SIZE)
        self.font_size_spin.setSuffix("px")
        self.font_size_spin.setToolTip("Font size")
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        toolbar.addWidget(self.font_size_spin)

        toolbar.addSeparator()

        # Voice control section
        self.voice_control_widget = VoiceControlWidget()
        self.voice_control_widget.voice_detection_enabled.connect(
            self._on_voice_detection_enabled
        )
        toolbar.addWidget(self.voice_control_widget)

        toolbar.addSeparator()

        # View controls section
        fullscreen_button = QPushButton("🖥️ Fullscreen")
        fullscreen_button.setToolTip("Enter fullscreen mode (F11)")
        fullscreen_button.clicked.connect(self.toggle_fullscreen)
        toolbar.addWidget(fullscreen_button)

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # File shortcuts
        open_action = QAction(self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        self.addAction(open_action)

        # Fullscreen shortcut
        fullscreen_action = QAction(self)
        fullscreen_action.setShortcut(Qt.Key.Key_F11)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(fullscreen_action)

        # Escape to exit fullscreen
        escape_action = QAction(self)
        escape_action.setShortcut(Qt.Key.Key_Escape)
        escape_action.triggered.connect(self.exit_fullscreen)
        self.addAction(escape_action)

    def _load_welcome_content(self):
        """Load welcome/instruction content."""
        welcome_text = """
# Welcome to Teleprompter

## Quick Start Guide

1. **Open a File**: Click "Open File" or press Ctrl+O (Cmd+O on Mac)
2. **Play/Pause**: Click "Play" or press Space
3. **Adjust Speed**: Use Up/Down arrow keys
4. **Voice Control**: Enable voice detection to start/stop with your voice
5. **Fullscreen**: Click "Fullscreen" or press F11
6. **Exit Fullscreen**: Press Escape

## Keyboard Shortcuts

- **Space**: Play/Pause
- **R**: Reset to beginning
- **Up/Down**: Adjust speed
- **F11**: Toggle fullscreen
- **Escape**: Exit fullscreen

## Voice Control

Enable voice detection to automatically start scrolling when you begin speaking and stop when you pause. You can:

- Adjust **Sensitivity** to fine-tune voice detection
- Select your preferred **Microphone**
- Monitor **Audio Level** to ensure proper detection

## Manual Navigation

- **Mouse Wheel**: Scroll up/down to navigate (auto-pauses scrolling)
- **Click**: Resume scrolling from current position

---

*Load a markdown file to begin...*
"""
        self.current_markdown_content = welcome_text
        html_content = self.parser.parse_content(welcome_text)
        self.teleprompter.load_content(html_content)

    def open_file(self):
        """Open a markdown file."""
        file_filter = "Markdown files (" + " ".join(config.MARKDOWN_EXTENSIONS) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Markdown File", "", file_filter
        )

        if file_path:
            try:
                with open(file_path, encoding="utf-8") as f:
                    self.current_markdown_content = f.read()
                html_content = self.parser.parse_file(file_path)
                self.teleprompter.load_content(html_content)
                self.current_file = file_path
                self.setWindowTitle(
                    f"{config.WINDOW_TITLE} - {os.path.basename(file_path)}"
                )
                self.teleprompter.reset()
                # Ensure teleprompter widget has focus for keyboard controls
                self.teleprompter.ensure_focus()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _reset_and_focus(self):
        """Reset teleprompter and ensure focus."""
        self.teleprompter.reset()
        self.teleprompter.ensure_focus()

    def _toggle_playback(self):
        """Toggle play/pause."""
        self.teleprompter.toggle_playback()
        self._update_play_button_icon()
        # Ensure teleprompter widget has focus for keyboard controls
        self.teleprompter.ensure_focus()

    def _update_play_button_icon(self):
        """Update the play button icon based on the current state."""
        if hasattr(self, "teleprompter") and self.teleprompter.is_playing:
            # Show pause icon
            pause_pixmap = icon_manager.get_themed_pixmap("pause", "default", "medium")
            if not pause_pixmap.isNull():
                self.play_button.setIcon(QIcon(pause_pixmap))
                self.play_button.setText("")
            else:
                self.play_button.setText("⏸")  # Fallback to emoji
        else:
            # Show play icon
            play_pixmap = icon_manager.get_themed_pixmap("play", "default", "medium")
            if not play_pixmap.isNull():
                self.play_button.setIcon(QIcon(play_pixmap))
                self.play_button.setText("")
            else:
                self.play_button.setText("▶")  # Fallback to emoji

    def _setup_button_hover_effects(self):
        """Set up hover effects for better visual feedback."""

        # Add hover effects to play button
        def on_play_button_enter():
            if hasattr(self, "teleprompter") and self.teleprompter.is_playing:
                pause_pixmap = icon_manager.get_themed_pixmap(
                    "pause", "hover", "medium"
                )
                if not pause_pixmap.isNull():
                    self.play_button.setIcon(QIcon(pause_pixmap))
            else:
                play_pixmap = icon_manager.get_themed_pixmap("play", "hover", "medium")
                if not play_pixmap.isNull():
                    self.play_button.setIcon(QIcon(play_pixmap))

        def on_play_button_leave():
            self._update_play_button_icon()

        # Install event filters for hover effects
        self.play_button.enterEvent = lambda e: on_play_button_enter()
        self.play_button.leaveEvent = lambda e: on_play_button_leave()

    def _on_speed_spinner_changed(self, speed: float):
        """Handle speed spinner change."""
        self.teleprompter.set_speed(speed)

    def _on_speed_changed(self, speed: float):
        """Handle speed change from teleprompter (keyboard shortcuts)."""
        # Update the speed spinner to reflect the new speed
        if hasattr(self, "speed_spin") and self.speed_spin.value() != speed:
            self.speed_spin.blockSignals(True)
            self.speed_spin.setValue(speed)
            self.speed_spin.blockSignals(False)

    def _on_font_size_changed(self, size: int):
        """Handle font size change."""
        self.teleprompter.set_font_size(size)

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
        if enabled:
            # Connect voice detector to teleprompter
            voice_detector = self.voice_control_widget.get_voice_detector()
            self.teleprompter.set_voice_detector(voice_detector)
        else:
            # Disconnect voice detector
            self.teleprompter.set_voice_detector(None)

        self.teleprompter.enable_voice_control(enabled)

    def _on_voice_activity_changed(self, is_active: bool):
        """Handle voice activity status change."""
        # Update play button icon when voice controls the teleprompter
        self._update_play_button_icon()
