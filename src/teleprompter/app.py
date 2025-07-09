"""Main application window and logic."""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from . import config
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

    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.DEFAULT_WIDTH, config.DEFAULT_HEIGHT)

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

    def _setup_toolbar(self):
        """Set up the toolbar with controls."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Open file action
        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Play/Pause button with icon
        self.play_button = QPushButton("▶️")
        self.play_button.setToolTip("Play/Pause scrolling")
        self.play_button.setFixedSize(30, 26)
        self.play_button.clicked.connect(self._toggle_playback)
        toolbar.addWidget(self.play_button)

        # Reset button with icon
        reset_button = QPushButton("⏮️")
        reset_button.setToolTip("Reset to beginning")
        reset_button.setFixedSize(30, 26)
        reset_button.clicked.connect(self._reset_and_focus)
        toolbar.addWidget(reset_button)

        toolbar.addSeparator()

        # Speed control (compact spinner like font size)
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setMinimum(config.MIN_SPEED)
        self.speed_spin.setMaximum(config.MAX_SPEED)
        self.speed_spin.setValue(config.DEFAULT_SPEED)
        self.speed_spin.setSuffix("x")
        self.speed_spin.setDecimals(2)
        self.speed_spin.setSingleStep(config.SPEED_INCREMENT)
        self.speed_spin.setToolTip("Scrolling speed")
        self.speed_spin.valueChanged.connect(self._on_speed_spinner_changed)
        toolbar.addWidget(self.speed_spin)

        toolbar.addSeparator()

        # Font size control (compact - no label needed)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(config.MIN_FONT_SIZE)
        self.font_size_spin.setMaximum(config.MAX_FONT_SIZE)
        self.font_size_spin.setValue(config.DEFAULT_FONT_SIZE)
        self.font_size_spin.setSuffix("px")
        self.font_size_spin.setToolTip("Font size")
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        toolbar.addWidget(self.font_size_spin)

        toolbar.addSeparator()

        # Voice control widget
        self.voice_control_widget = VoiceControlWidget()
        self.voice_control_widget.voice_detection_enabled.connect(
            self._on_voice_detection_enabled
        )
        toolbar.addWidget(self.voice_control_widget)

        toolbar.addSeparator()

        # Fullscreen button
        fullscreen_button = QPushButton("Fullscreen")
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
        self.play_button.setText("⏸️" if self.teleprompter.is_playing else "▶️")
        # Ensure teleprompter widget has focus for keyboard controls
        self.teleprompter.ensure_focus()

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
        # Update play button text when voice controls the teleprompter
        if is_active:
            self.play_button.setText("⏸️")
        else:
            self.play_button.setText("▶️")
