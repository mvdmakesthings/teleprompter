"""Modern custom spinbox widgets with refined icons and styling."""

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDoubleSpinBox, QPushButton, QSpinBox

from .icon_manager import icon_manager


class ModernSpinBox(QSpinBox):
    """Modern QSpinBox with proper icon integration and refined styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_modern_style()

    def _setup_modern_style(self):
        """Set up modern styling with proper icon buttons."""
        # Hide default arrows
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        # Create custom buttons with modern styling
        self._up_button = QPushButton(self)
        self._down_button = QPushButton(self)

        # Modern button styling with proper scaling
        button_style = """
            QPushButton {
                background-color: transparent;
                border: 1px solid #404040;
                color: #c0c0c0;
                padding: 0px;
                margin: 0px;
                min-width: 18px;
                max-width: 18px;
                min-height: 12px;
                max-height: 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #404040;
                border-color: #0078d4;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0078d4;
                border-color: #106ebe;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: transparent;
                border-color: #2a2a2a;
                color: #666666;
            }
        """

        self._up_button.setStyleSheet(button_style)
        self._down_button.setStyleSheet(button_style)

        # Connect buttons
        self._up_button.clicked.connect(self.stepUp)
        self._down_button.clicked.connect(self.stepDown)

        # Load modern icons with proper sizing
        self._update_icons()

        # Set tooltips for better UX
        self._up_button.setToolTip("Increase value")
        self._down_button.setToolTip("Decrease value")

    def _update_icons(self):
        """Update icons with proper theming."""
        # Use small size for spinbox arrows
        up_pixmap = icon_manager.get_themed_pixmap("chevron-up", "default", "small")
        down_pixmap = icon_manager.get_themed_pixmap("chevron-down", "default", "small")

        if not up_pixmap.isNull() and not down_pixmap.isNull():
            self._up_button.setIcon(QIcon(up_pixmap))
            self._down_button.setIcon(QIcon(down_pixmap))
        else:
            # Fallback to Unicode arrows
            self._up_button.setText("▲")
            self._down_button.setText("▼")

    def resizeEvent(self, event):
        """Position the custom buttons with proper margins."""
        super().resizeEvent(event)

        # Calculate proper button positioning
        button_width = 18
        button_height = max(12, (self.height() - 8) // 2)
        x = self.width() - button_width - 4
        y_offset = 3

        self._up_button.setGeometry(x, y_offset, button_width, button_height)
        self._down_button.setGeometry(
            x, y_offset + button_height + 2, button_width, button_height
        )

        # Ensure buttons are on top
        self._up_button.raise_()
        self._down_button.raise_()

    def changeEvent(self, event):
        """Handle theme changes and updates."""
        super().changeEvent(event)
        if event.type() == event.Type.PaletteChange:
            self._update_icons()


class ModernDoubleSpinBox(QDoubleSpinBox):
    """Modern QDoubleSpinBox with proper icon integration and refined styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_modern_style()

    def _setup_modern_style(self):
        """Set up modern styling with proper icon buttons."""
        # Hide default arrows
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

        # Create custom buttons with modern styling
        self._up_button = QPushButton(self)
        self._down_button = QPushButton(self)

        # Modern button styling with proper scaling
        button_style = """
            QPushButton {
                background-color: transparent;
                border: 1px solid #404040;
                color: #c0c0c0;
                padding: 0px;
                margin: 0px;
                min-width: 18px;
                max-width: 18px;
                min-height: 12px;
                max-height: 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #404040;
                border-color: #0078d4;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0078d4;
                border-color: #106ebe;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: transparent;
                border-color: #2a2a2a;
                color: #666666;
            }
        """

        self._up_button.setStyleSheet(button_style)
        self._down_button.setStyleSheet(button_style)

        # Connect buttons
        self._up_button.clicked.connect(self.stepUp)
        self._down_button.clicked.connect(self.stepDown)

        # Load modern icons with proper sizing
        self._update_icons()

        # Set tooltips for better UX
        self._up_button.setToolTip("Increase value")
        self._down_button.setToolTip("Decrease value")

    def _update_icons(self):
        """Update icons with proper theming."""
        # Use small size for spinbox arrows
        up_pixmap = icon_manager.get_themed_pixmap("chevron-up", "default", "small")
        down_pixmap = icon_manager.get_themed_pixmap("chevron-down", "default", "small")

        if not up_pixmap.isNull() and not down_pixmap.isNull():
            self._up_button.setIcon(QIcon(up_pixmap))
            self._down_button.setIcon(QIcon(down_pixmap))
        else:
            # Fallback to Unicode arrows
            self._up_button.setText("▲")
            self._down_button.setText("▼")

    def resizeEvent(self, event):
        """Position the custom buttons with proper margins."""
        super().resizeEvent(event)

        # Calculate proper button positioning
        button_width = 18
        button_height = max(12, (self.height() - 8) // 2)
        x = self.width() - button_width - 4
        y_offset = 3

        self._up_button.setGeometry(x, y_offset, button_width, button_height)
        self._down_button.setGeometry(
            x, y_offset + button_height + 2, button_width, button_height
        )

        # Ensure buttons are on top
        self._up_button.raise_()
        self._down_button.raise_()

    def changeEvent(self, event):
        """Handle theme changes and updates."""
        super().changeEvent(event)
        if event.type() == event.Type.PaletteChange:
            self._update_icons()


# Keep backward compatibility with old class names
IconSpinBox = ModernSpinBox
IconDoubleSpinBox = ModernDoubleSpinBox
