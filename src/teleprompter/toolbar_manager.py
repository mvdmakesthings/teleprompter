"""Toolbar management for the teleprompter application."""

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QPushButton, QSizePolicy, QToolBar, QToolButton

from . import config
from .custom_widgets import ModernDoubleSpinBox, ModernSpinBox
from .icon_manager import icon_manager
from .voice_control_widget import VoiceControlWidget


class ModernToolBar(QToolBar):
    """Custom QToolBar with enhanced extension button styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._extension_button_timer = QTimer()
        self._extension_button_timer.timeout.connect(self._find_and_style_extension_button)
        self._extension_button_timer.setSingleShot(True)

    def resizeEvent(self, event):
        """Override resize event to handle extension button styling."""
        super().resizeEvent(event)
        # Delay the extension button search to allow Qt to create it
        self._extension_button_timer.start(100)

    def _find_and_style_extension_button(self):
        """Find and style the extension button after a delay."""
        toolbar_buttons = self.findChildren(QToolButton)
        
        # First, try to find obvious extension buttons
        for button in toolbar_buttons:
            # Multiple ways to identify the extension button:
            # 1. No default action (primary method)
            # 2. Qt object names like "qt_toolbar_ext_button"
            # 3. Button with specific property characteristics
            is_extension_button = (
                not button.defaultAction() or
                button.objectName() in ["qt_toolbar_ext_button", "ExtensionButton"] or
                (hasattr(button, 'isExtensionButton') and button.isExtensionButton()) or
                button.objectName().startswith("qt_") and "ext" in button.objectName().lower()
            )

            if is_extension_button and button.objectName() != "toolbarExtensionButton":
                self._apply_extension_button_styling(button)
                return

        # Fallback: If no obvious extension button found but toolbar might be overflowing
        # Look for buttons that appear to be on the right edge or are partially hidden
        if toolbar_buttons:
            # Check if any button might be the extension button by position
            toolbar_rect = self.rect()
            for button in toolbar_buttons:
                button_rect = button.geometry()
                # If button is near or beyond the right edge, it might be the extension button
                if (button_rect.right() >= toolbar_rect.width() - 50 and
                    button.objectName() != "toolbarExtensionButton" and
                    not button.defaultAction()):
                    self._apply_extension_button_styling(button)
                    break

    def _apply_extension_button_styling(self, button):
        """Apply comprehensive styling to the extension button."""
        from PyQt6.QtCore import QSize
        from PyQt6.QtWidgets import QSizePolicy
        from PyQt6.QtGui import QIcon

        # Set unique object name for CSS targeting
        button.setObjectName("toolbarExtensionButton")

        # Set proper size constraints to prevent cut-off
        button.setMinimumSize(36, 32)
        button.setMaximumSize(48, 36)

        # Set a modern icon size
        button.setIconSize(QSize(18, 18))

        # Try to get a modern icon from icon manager, fallback to text
        more_icon = self._create_more_options_icon()
        if not more_icon.isNull():
            button.setIcon(more_icon)
            button.setText("")  # Clear text when using icon
        else:
            # Use a modern "more options" icon (three dots) as fallback
            button.setText("⋯")  # Horizontal ellipsis - modern and clean

        button.setToolTip("More toolbar options")

        # Ensure proper size policy to maintain visibility
        button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )

        # Force style refresh
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()

    def _create_more_options_icon(self):
        """Create a modern three-dot icon programmatically."""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QPen
        from PyQt6.QtCore import Qt, QRectF

        # Create a 18x18 pixmap for the icon
        pixmap = QPixmap(18, 18)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Use light gray color for dots
        painter.setBrush(QBrush(Qt.GlobalColor.lightGray))
        painter.setPen(QPen(Qt.GlobalColor.transparent))

        # Draw three horizontal dots (modern material design style)
        dot_size = 3
        spacing = 2
        total_width = 3 * dot_size + 2 * spacing
        start_x = (18 - total_width) / 2
        center_y = 9

        for i in range(3):
            x = start_x + i * (dot_size + spacing)
            painter.drawEllipse(QRectF(x, center_y - dot_size/2, dot_size, dot_size))

        painter.end()

        return QIcon(pixmap)


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
        self.toolbar = ModernToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # Set proper icon size for all toolbar buttons
        from PyQt6.QtCore import QSize
        self.toolbar.setIconSize(QSize(20, 20))

        # Ensure adequate spacing between toolbar items
        self.toolbar.layout().setSpacing(4)

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

    def refresh_toolbar_styling(self):
        """Refresh toolbar styling, including any extension button that may have appeared."""
        if self.toolbar:
            # Re-attempt to style the extension button in case it appeared after resize
            self.toolbar._find_and_style_extension_button()
            self.toolbar.update()

    def force_extension_button_update(self):
        """Force an update of the extension button styling."""
        if self.toolbar:
            # Immediately check for and style extension buttons
            self.toolbar._find_and_style_extension_button()
            # Also trigger a delayed check in case Qt hasn't created the button yet
            self.toolbar._extension_button_timer.start(50)
