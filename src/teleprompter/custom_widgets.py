"""Modern custom spinbox widgets with refined icons and styling."""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGraphicsOpacityEffect,
    QPushButton,
    QSpinBox,
    QWidget,
)

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


# Phase 4.2: Micro-interactions and Animation Support


class AnimatedButton(QPushButton):
    """Enhanced button with micro-interactions and animations."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_animations()

    def _setup_animations(self):
        """Set up button animations."""
        # Scale animation for press/release
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Opacity animation for hover
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuart)

    def enterEvent(self, event):
        """Animate button on hover enter."""
        super().enterEvent(event)
        # Subtle scale and opacity animation
        current_geometry = self.geometry()
        scaled_geometry = QRect(
            current_geometry.x() - 2,
            current_geometry.y() - 2,
            current_geometry.width() + 4,
            current_geometry.height() + 4,
        )

        self.scale_animation.setStartValue(current_geometry)
        self.scale_animation.setEndValue(scaled_geometry)
        self.scale_animation.start()

        self.opacity_animation.setStartValue(0.8)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

    def leaveEvent(self, event):
        """Animate button on hover leave."""
        super().leaveEvent(event)
        # Return to normal scale and opacity
        current_geometry = self.geometry()
        normal_geometry = QRect(
            current_geometry.x() + 2,
            current_geometry.y() + 2,
            current_geometry.width() - 4,
            current_geometry.height() - 4,
        )

        self.scale_animation.setStartValue(current_geometry)
        self.scale_animation.setEndValue(normal_geometry)
        self.scale_animation.start()

        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.8)
        self.opacity_animation.start()


class SpringAnimatedWidget(QWidget):
    """Widget with spring-based animations for natural motion."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_spring_animations()

    def _setup_spring_animations(self):
        """Set up spring-like animations."""
        self.spring_animation = QPropertyAnimation(self, b"pos")
        self.spring_animation.setDuration(300)
        # Spring easing curve for natural motion
        self.spring_animation.setEasingCurve(QEasingCurve.Type.OutElastic)

    def animate_to_position(self, new_pos):
        """Animate widget to new position with spring effect."""
        self.spring_animation.setStartValue(self.pos())
        self.spring_animation.setEndValue(new_pos)
        self.spring_animation.start()


class PulseAnimation(QWidget):
    """Widget that provides a subtle pulse animation for attention."""

    pulse_started = pyqtSignal()
    pulse_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_pulse_animation()

    def _setup_pulse_animation(self):
        """Set up pulse animation effect."""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.pulse_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_animation.finished.connect(self.pulse_finished)

    def start_pulse(self, cycles=1):
        """Start pulse animation for specified cycles."""
        self.pulse_started.emit()
        self.pulse_animation.setStartValue(0.3)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.setLoopCount(cycles * 2)  # Each cycle = fade out + fade in
        self.pulse_animation.start()

    def stop_pulse(self):
        """Stop pulse animation."""
        self.pulse_animation.stop()
        self.opacity_effect.setOpacity(1.0)


# Keep backward compatibility with old class names
IconSpinBox = ModernSpinBox
IconDoubleSpinBox = ModernDoubleSpinBox
