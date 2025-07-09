"""Main application window and logic."""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from . import config
from .markdown_parser import MarkdownParser
from .teleprompter import TeleprompterWidget


class TeleprompterApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.parser = MarkdownParser()
        self.current_file = None

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

        # Play/Pause button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._toggle_playback)
        toolbar.addWidget(self.play_button)

        # Reset button
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.teleprompter.reset)
        toolbar.addWidget(reset_button)

        toolbar.addSeparator()

        # Speed label
        self.speed_label = QLabel(f"Speed: {config.DEFAULT_SPEED:.1f}x")
        toolbar.addWidget(self.speed_label)

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
4. **Fullscreen**: Click "Fullscreen" or press F11
5. **Exit Fullscreen**: Press Escape

## Keyboard Shortcuts

- **Space**: Play/Pause
- **R**: Reset to beginning
- **Up/Down**: Adjust speed
- **F11**: Toggle fullscreen
- **Escape**: Exit fullscreen

---

*Load a markdown file to begin...*
"""
        html_content = self.parser.parse_content(welcome_text)
        self.teleprompter.load_content(html_content)

    def open_file(self):
        """Open a markdown file."""
        file_filter = "Markdown files (" + " ".join(config.MARKDOWN_EXTENSIONS) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            file_filter
        )

        if file_path:
            try:
                html_content = self.parser.parse_file(file_path)
                self.teleprompter.load_content(html_content)
                self.current_file = file_path
                self.setWindowTitle(f"{config.WINDOW_TITLE} - {os.path.basename(file_path)}")
                self.teleprompter.reset()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _toggle_playback(self):
        """Toggle play/pause."""
        self.teleprompter.toggle_playback()
        self.play_button.setText("Pause" if self.teleprompter.is_playing else "Play")

    def _on_speed_changed(self, speed: float):
        """Handle speed change."""
        self.speed_label.setText(f"Speed: {speed:.1f}x")

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
