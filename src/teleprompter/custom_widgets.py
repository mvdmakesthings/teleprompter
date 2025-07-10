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

from .base_widgets import (
    DebouncedActionMixin,
    HoverAnimatedWidget,
    ModernButtonBase,
    ModernSpinBoxBase,
    PulseAnimationBase,
)
from .icon_manager import icon_manager
from .style_manager import get_style_manager


class ModernSpinBox(QSpinBox, ModernSpinBoxBase):
    """Modern QSpinBox with proper icon integration and refined styling."""

    def __init__(self, parent=None):
        QSpinBox.__init__(self, parent)
        ModernSpinBoxBase.__init__(self, parent)
        self._setup_modern_style()
        self._setup_spinbox_style()

    def _setup_modern_style(self):
        """Set up modern styling with proper icon buttons."""
        # Hide default arrows
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        # Create custom buttons with modern styling
        self._up_button = QPushButton(self)
        self._down_button = QPushButton(self)

        # Modern button styling with proper scaling
        button_style = get_style_manager().get_spinbox_button_stylesheet()

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
            # Fallback to modern Unicode arrows
            self._up_button.setText("⌃")
            self._down_button.setText("⌄")

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

    def _setup_spinbox_style(self):
        """Implement abstract method from base class."""
        # Apply base spinbox styling
        arrow_style = self.get_arrow_style(True) + self.get_arrow_style(False)
        self.setStyleSheet(self.styleSheet() + arrow_style)


class ModernDoubleSpinBox(QDoubleSpinBox, ModernSpinBoxBase):
    """Modern QDoubleSpinBox with proper icon integration and refined styling."""

    def __init__(self, parent=None):
        QDoubleSpinBox.__init__(self, parent)
        ModernSpinBoxBase.__init__(self, parent)
        self._setup_modern_style()
        self._setup_spinbox_style()

    def _setup_modern_style(self):
        """Set up modern styling with proper icon buttons."""
        # Hide default arrows
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

        # Create custom buttons with modern styling
        self._up_button = QPushButton(self)
        self._down_button = QPushButton(self)

        # Modern button styling with proper scaling
        button_style = get_style_manager().get_spinbox_button_stylesheet()

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
            # Fallback to modern Unicode arrows
            self._up_button.setText("⌃")
            self._down_button.setText("⌄")

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

    def _setup_spinbox_style(self):
        """Implement abstract method from base class."""
        # Apply base spinbox styling
        arrow_style = self.get_arrow_style(True) + self.get_arrow_style(False)
        self.setStyleSheet(self.styleSheet() + arrow_style)


# Phase 4.2: Micro-interactions and Animation Support


class AnimatedButton(ModernButtonBase):
    """Enhanced button with micro-interactions and animations."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_additional_animations()

    def _setup_additional_animations(self):
        """Set up additional button animations beyond base class."""
        # Geometry animation for hover effect
        self.geometry_animation = QPropertyAnimation(self, b"geometry")
        self.geometry_animation.setDuration(150)
        self.geometry_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

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

        self.geometry_animation.setStartValue(current_geometry)
        self.geometry_animation.setEndValue(scaled_geometry)
        self.geometry_animation.start()

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

        self.geometry_animation.setStartValue(current_geometry)
        self.geometry_animation.setEndValue(normal_geometry)
        self.geometry_animation.start()

        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.8)
        self.opacity_animation.start()


class SpringAnimatedWidget(HoverAnimatedWidget):
    """Widget with spring-based animations for natural motion."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_spring_animations()

    def _setup_spring_animations(self):
        """Set up spring-like animations."""
        # Create position animation with spring effect
        self.create_animation("position", self.pos(), self.pos(), 300)
        position_anim = self._animations.get("position")
        if position_anim:
            position_anim.setEasingCurve(QEasingCurve.Type.OutElastic)

    def animate_to_position(self, new_pos):
        """Animate widget to new position with spring effect."""
        position_anim = self._animations.get("position")
        if position_anim:
            position_anim.setStartValue(self.pos())
            position_anim.setEndValue(new_pos)
            position_anim.start()


class PulseAnimationWidget(QWidget, DebouncedActionMixin):
    """Widget that provides a subtle pulse animation for attention."""

    pulse_started = pyqtSignal()
    pulse_finished = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        DebouncedActionMixin.__init__(self)
        self._pulse_animation = PulseAnimationBase(self, self)
        self._pulse_animation.start()  # Initialize animation
        self._pulse_animation.stop()  # But don't start pulsing yet

    def start_pulse(self, cycles=1, interval=50):
        """Start pulse animation for specified cycles."""
        self.pulse_started.emit()
        # Use debounce to prevent rapid start/stop
        self.debounce(lambda: self._start_pulse_internal(interval), 100, "pulse")

    def _start_pulse_internal(self, interval):
        """Internal method to start pulse."""
        self._pulse_animation.start(interval)

    def stop_pulse(self):
        """Stop pulse animation."""
        self.cancel_debounce("pulse")
        self._pulse_animation.stop()
        self.pulse_finished.emit()
