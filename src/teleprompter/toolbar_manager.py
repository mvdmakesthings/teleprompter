"""Toolbar management for the teleprompter application."""

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QPushButton, QToolBar

from . import config
from .custom_widgets import ModernDoubleSpinBox, ModernSpinBox
from .icon_manager import icon_manager
from .style_manager import StyleManager
from .voice_control_widget import VoiceControlWidget


class ToolbarManager(QObject):
    """Manages the application toolbar and its controls."""

    # Signals for UI events
    open_file_requested = pyqtSignal()
    playback_toggled = pyqtSignal()
    reset_requested = pyqtSignal()
    speed_changed = pyqtSignal(float)
    font_size_changed = pyqtSignal(int)
    font_preset_cycled = pyqtSignal()
    presentation_mode_toggled = pyqtSignal()
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
        self.font_preset_btn = None
        self.voice_control_widget = None

        # State tracking
        self.current_font_preset_index = 0
        self.font_presets = list(config.FONT_PRESETS.keys())

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
        self._add_visual_separator("Voice")

        self._add_view_controls()

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
        self.update_play_button_icon(False)  # Start with play icon
        self.toolbar.addWidget(self.play_button)

        # Reset button
        reset_button = QPushButton()
        reset_button.setObjectName("resetButton")
        reset_button.setToolTip("Reset to beginning (R)")
        reset_button.clicked.connect(self.reset_requested.emit)

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
        self.toolbar.addWidget(prev_section_button)

        # Next section button
        next_section_button = QPushButton("▶")
        next_section_button.setObjectName("nextSectionButton")
        next_section_button.setToolTip("Next section (→)")
        next_section_button.clicked.connect(self.next_section_requested.emit)
        self.toolbar.addWidget(next_section_button)

    def _add_speed_font_controls(self):
        """Add speed and font controls group."""
        # Speed control section
        speed_group = self._create_control_group("Speed")
        self.toolbar.addWidget(speed_group)

        self.speed_spin = ModernDoubleSpinBox()
        self.speed_spin.setMinimum(config.MIN_SPEED)
        self.speed_spin.setMaximum(config.MAX_SPEED)
        self.speed_spin.setValue(config.DEFAULT_SPEED)
        self.speed_spin.setSuffix("x")
        self.speed_spin.setDecimals(2)
        self.speed_spin.setSingleStep(config.SPEED_INCREMENT)
        self.speed_spin.setToolTip("Scrolling speed (↑↓ arrows)")
        self.speed_spin.valueChanged.connect(self.speed_changed.emit)
        self.toolbar.addWidget(self.speed_spin)

        self.toolbar.addSeparator()

        # Font size control section
        font_group = self._create_control_group("Font")
        self.toolbar.addWidget(font_group)

        self.font_size_spin = ModernSpinBox()
        self.font_size_spin.setMinimum(config.MIN_FONT_SIZE)
        self.font_size_spin.setMaximum(config.MAX_FONT_SIZE)
        self.font_size_spin.setValue(config.DEFAULT_FONT_SIZE)
        self.font_size_spin.setSuffix("px")
        self.font_size_spin.setToolTip("Font size")
        self.font_size_spin.valueChanged.connect(self.font_size_changed.emit)
        self.toolbar.addWidget(self.font_size_spin)

        # Font preset button
        self.font_preset_btn = QPushButton("Auto")
        self.font_preset_btn.setMaximumWidth(50)
        self.font_preset_btn.setToolTip("Font preset for viewing distance")
        self.font_preset_btn.clicked.connect(self.font_preset_cycled.emit)
        self.toolbar.addWidget(self.font_preset_btn)

    def _add_voice_controls(self):
        """Add voice control group."""
        self.voice_control_widget = VoiceControlWidget()
        self.voice_control_widget.voice_detection_enabled.connect(
            self.voice_detection_toggled.emit
        )
        self.toolbar.addWidget(self.voice_control_widget)

    def _add_view_controls(self):
        """Add view controls group."""
        # Presentation mode button
        presentation_button = QPushButton("Present")
        presentation_button.setObjectName("presentationButton")
        presentation_button.setToolTip("Toggle presentation mode (Ctrl+P)")
        presentation_button.clicked.connect(self.presentation_mode_toggled.emit)
        self.toolbar.addWidget(presentation_button)

    def _create_control_group(self, label: str) -> QPushButton:
        """Create a styled group label for controls."""
        group_label = QPushButton(label)
        group_label.setEnabled(False)
        group_label.setStyleSheet(StyleManager.get_toolbar_group_label_stylesheet())
        return group_label

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

    def cycle_font_preset(self) -> str:
        """Cycle to the next font preset and return its name.

        Returns:
            The name of the new preset
        """
        self.current_font_preset_index = (self.current_font_preset_index + 1) % len(
            self.font_presets
        )
        preset_name = self.font_presets[self.current_font_preset_index]

        # Update button text
        preset_display_names = {
            "close": "Close",
            "medium": "Med",
            "far": "Far",
            "presentation": "Pres",
        }
        display_name = preset_display_names.get(preset_name, preset_name.title())
        if self.font_preset_btn:
            self.font_preset_btn.setText(display_name)

        return preset_name

    def set_font_preset_index(self, index: int):
        """Set the font preset index from settings."""
        self.current_font_preset_index = index
        preset_name = self.font_presets[index]

        preset_display_names = {
            "close": "Close",
            "medium": "Med",
            "far": "Far",
            "presentation": "Pres",
        }
        display_name = preset_display_names.get(preset_name, preset_name.title())
        if self.font_preset_btn:
            self.font_preset_btn.setText(display_name)

    def get_voice_detector(self):
        """Get the voice detector from the voice control widget."""
        if self.voice_control_widget:
            return self.voice_control_widget.get_voice_detector()
        return None
