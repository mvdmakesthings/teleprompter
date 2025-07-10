"""Toolbar management for the teleprompter application."""

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QPushButton, QSizePolicy, QToolBar

from . import config
from .custom_widgets import ModernDoubleSpinBox, ModernSpinBox
from .icon_manager import icon_manager
from .voice_control_widget import VoiceControlWidget


class ToolbarManager(QObject):
    """Manages the application toolbar and its controls."""

    # Signals for UI events
    open_file_requested = pyqtSignal()
    playback_toggled = pyqtSignal()
    reset_requested = pyqtSignal()
    speed_changed = pyqtSignal(float)
    font_size_changed = pyqtSignal(int)
    previous_section_requested = pyqtSignal()
    next_section_requested = pyqtSignal()
    voice_detection_toggled = pyqtSignal(bool)

    def __init__(self, parent_window):
        """Initialize the toolbar manager.

        Args:
            parent_window: The main window that will contain the toolbar
        """
        super().__init__()
        self.parent_window = parent_window
        self.toolbar = None

        # Control references
        self.play_button = None
        self.speed_spin = None
        self.font_size_spin = None
        self.voice_control_widget = None

    def create_toolbar(self) -> QToolBar:
        """Create and configure the main toolbar.

        Returns:
            The configured toolbar
        """
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # Add control groups
        self._add_file_controls()
        self._add_visual_separator("File")

        self._add_playback_controls()
        self._add_visual_separator("Playback")

        self._add_speed_font_controls()
        self._add_visual_separator("Display")

        self._add_voice_controls()

        # Fix toolbar layout rendering issues
        self._fix_toolbar_layout()

        return self.toolbar

    def _add_file_controls(self):
        """Add file operation controls group."""
        open_action = QAction("Open", self.parent_window)
        open_action.setToolTip("Open markdown file (Ctrl+O)")
        open_action.triggered.connect(self.open_file_requested.emit)

        # Set icon for open action
        open_pixmap = icon_manager.get_themed_pixmap("folder-open", "default", "medium")
        if not open_pixmap.isNull():
            open_action.setIcon(QIcon(open_pixmap))
        else:
            open_action.setText("📁 Open")

        self.toolbar.addAction(open_action)

    def _add_playback_controls(self):
        """Add playback controls group with enhanced styling."""
        # Play/Pause button
        self.play_button = QPushButton()
        self.play_button.setObjectName("playButton")
        self.play_button.setToolTip("Play/Pause scrolling (Space)")
        self.play_button.clicked.connect(self.playback_toggled.emit)
        # Set consistent size policy for toolbar buttons
        self.play_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.update_play_button_icon(False)  # Start with play icon
        self.toolbar.addWidget(self.play_button)

        # Reset button
        reset_button = QPushButton()
        reset_button.setObjectName("resetButton")
        reset_button.setToolTip("Reset to beginning (R)")
        reset_button.clicked.connect(self.reset_requested.emit)
        reset_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        reset_pixmap = icon_manager.get_themed_pixmap("skip-back", "default", "medium")
        if not reset_pixmap.isNull():
            reset_button.setIcon(QIcon(reset_pixmap))
        else:
            reset_button.setText("⏮")

        self.toolbar.addWidget(reset_button)

        # Section navigation buttons
        self.toolbar.addSeparator()

        # Previous section button
        prev_section_button = QPushButton("◀")
        prev_section_button.setObjectName("prevSectionButton")
        prev_section_button.setToolTip("Previous section (←)")
        prev_section_button.clicked.connect(self.previous_section_requested.emit)
        prev_section_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.toolbar.addWidget(prev_section_button)

        # Next section button
        next_section_button = QPushButton("▶")
        next_section_button.setObjectName("nextSectionButton")
        next_section_button.setToolTip("Next section (→)")
        next_section_button.clicked.connect(self.next_section_requested.emit)
        next_section_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.toolbar.addWidget(next_section_button)

    def _add_speed_font_controls(self):
        """Add speed and font controls group."""
        # Speed control section (label removed for cleaner UI)
        self.speed_spin = ModernDoubleSpinBox()
        self.speed_spin.setMinimum(config.MIN_SPEED)
        self.speed_spin.setMaximum(config.MAX_SPEED)
        self.speed_spin.setValue(config.DEFAULT_SPEED)
        self.speed_spin.setSuffix("x")
        self.speed_spin.setDecimals(2)
        self.speed_spin.setSingleStep(config.SPEED_INCREMENT)
        self.speed_spin.setToolTip("Scrolling speed (↑↓ arrows)")
        self.speed_spin.valueChanged.connect(self.speed_changed.emit)
        self.speed_spin.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.toolbar.addWidget(self.speed_spin)

        self.toolbar.addSeparator()

        self.font_size_spin = ModernSpinBox()
        self.font_size_spin.setMinimum(config.MIN_FONT_SIZE)
        self.font_size_spin.setMaximum(config.MAX_FONT_SIZE)
        self.font_size_spin.setValue(config.DEFAULT_FONT_SIZE)
        self.font_size_spin.setSuffix("px")
        self.font_size_spin.setToolTip("Font size")
        self.font_size_spin.valueChanged.connect(self.font_size_changed.emit)
        self.font_size_spin.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.toolbar.addWidget(self.font_size_spin)

    def _add_voice_controls(self):
        """Add voice control group."""
        self.voice_control_widget = VoiceControlWidget()
        self.voice_control_widget.voice_detection_enabled.connect(
            self.voice_detection_toggled.emit
        )
        # Set consistent size policy for voice control widget
        self.voice_control_widget.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.toolbar.addWidget(self.voice_control_widget)

    def _add_visual_separator(self, group_name: str):
        """Add a visual separator between control groups."""
        self.toolbar.addSeparator()

    def update_play_button_icon(self, is_playing: bool):
        """Update the play button icon based on the playing state.

        Args:
            is_playing: Whether the teleprompter is currently playing
        """
        if not self.play_button:
            return

        if is_playing:
            # Show pause icon
            pause_pixmap = icon_manager.get_themed_pixmap("pause", "default", "medium")
            if not pause_pixmap.isNull():
                self.play_button.setIcon(QIcon(pause_pixmap))
                self.play_button.setText("")
            else:
                self.play_button.setText("⏸")
        else:
            # Show play icon
            play_pixmap = icon_manager.get_themed_pixmap("play", "default", "medium")
            if not play_pixmap.isNull():
                self.play_button.setIcon(QIcon(play_pixmap))
                self.play_button.setText("")
            else:
                self.play_button.setText("▶")

    def update_speed_display(self, speed: float):
        """Update the speed spinner display.

        Args:
            speed: The new speed value
        """
        if self.speed_spin and self.speed_spin.value() != speed:
            self.speed_spin.blockSignals(True)
            self.speed_spin.setValue(speed)
            self.speed_spin.blockSignals(False)

    def update_font_size_display(self, size: int):
        """Update the font size spinner display.

        Args:
            size: The new font size
        """
        if self.font_size_spin and self.font_size_spin.value() != size:
            self.font_size_spin.blockSignals(True)
            self.font_size_spin.setValue(size)
            self.font_size_spin.blockSignals(False)

    def get_voice_detector(self):
        """Get the voice detector from the voice control widget."""
        if self.voice_control_widget:
            return self.voice_control_widget.get_voice_detector()
        return None

    def _fix_toolbar_layout(self):
        """Fix toolbar layout rendering issues.

        This resolves the issue where extra buttons appear on startup and disappear
        after resizing by ensuring proper layout calculations and geometry updates.
        """
        if not self.toolbar:
            return

        # Force size policy on the toolbar itself
        self.toolbar.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )

        # Update geometry to force layout recalculation
        self.toolbar.updateGeometry()

        # Force an immediate layout update
        self.toolbar.adjustSize()

        # Ensure all widgets have consistent minimum sizes
        for i in range(self.toolbar.layout().count()):
            item = self.toolbar.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QPushButton):
                    # Ensure all buttons have consistent minimum size hints
                    widget.setMinimumSize(widget.sizeHint())
                    widget.updateGeometry()

        # Final update to ensure proper rendering
        self.toolbar.update()
