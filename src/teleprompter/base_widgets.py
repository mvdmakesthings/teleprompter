"""Abstract base classes for common widget patterns.

This module provides base classes that encapsulate common widget behaviors,
reducing code duplication and promoting consistent patterns across the application.
"""

from abc import abstractmethod
from typing import Any

from PyQt6.QtCore import QEasingCurve, QObject, QPropertyAnimation, QTimer, pyqtProperty
from PyQt6.QtGui import QEnterEvent
from PyQt6.QtWidgets import QPushButton, QWidget


class AnimatedWidgetBase(QWidget):
    """Base class for widgets with animation capabilities."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._animation_duration = 200
        self._animations: dict[str, QPropertyAnimation] = {}

    def create_animation(
        self,
        property_name: str,
        start_value: Any,
        end_value: Any,
        duration: int | None = None,
    ) -> QPropertyAnimation:
        """Create and configure a property animation."""
        animation = QPropertyAnimation(self, property_name.encode())
        animation.setDuration(duration or self._animation_duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._animations[property_name] = animation
        return animation

    def start_animation(self, property_name: str) -> None:
        """Start a specific animation."""
        if property_name in self._animations:
            self._animations[property_name].start()

    def stop_animation(self, property_name: str) -> None:
        """Stop a specific animation."""
        if property_name in self._animations:
            self._animations[property_name].stop()

    def set_animation_duration(self, duration: int) -> None:
        """Set duration for all animations."""
        self._animation_duration = duration
        for animation in self._animations.values():
            animation.setDuration(duration)


class HoverAnimatedWidget(AnimatedWidgetBase):
    """Base class for widgets that animate on hover."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._hover_scale = 1.05
        self._is_hovered = False
        self.setMouseTracking(True)
        self._setup_hover_animation()

    def _setup_hover_animation(self) -> None:
        """Set up hover animation."""
        self._scale = 1.0
        self.create_animation("scale", 1.0, self._hover_scale)

    @pyqtProperty(float)
    def scale(self) -> float:
        """Get current scale."""
        return self._scale

    @scale.setter
    def scale(self, value: float) -> None:
        """Set current scale."""
        self._scale = value
        self.update()

    def enterEvent(self, event: QEnterEvent) -> None:
        """Handle mouse enter."""
        self._is_hovered = True
        animation = self._animations.get("scale")
        if animation:
            animation.setStartValue(self._scale)
            animation.setEndValue(self._hover_scale)
            animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        """Handle mouse leave."""
        self._is_hovered = False
        animation = self._animations.get("scale")
        if animation:
            animation.setStartValue(self._scale)
            animation.setEndValue(1.0)
            animation.start()
        super().leaveEvent(event)


class ModernButtonBase(QPushButton, AnimatedWidgetBase):
    """Base class for modern styled buttons with animations."""

    def __init__(self, text: str = "", parent: QWidget | None = None):
        QPushButton.__init__(self, text, parent)
        AnimatedWidgetBase.__init__(self, parent)
        self._setup_button_animations()
        self.setMouseTracking(True)

    def _setup_button_animations(self) -> None:
        """Set up button-specific animations."""
        # Shadow animation
        self._shadow_blur = 0
        self.create_animation("shadow_blur", 0, 10, 150)

        # Scale animation
        self._scale = 1.0
        self.create_animation("scale", 1.0, 0.95, 100)

    @pyqtProperty(int)
    def shadow_blur(self) -> int:
        """Get shadow blur radius."""
        return self._shadow_blur

    @shadow_blur.setter
    def shadow_blur(self, value: int) -> None:
        """Set shadow blur radius."""
        self._shadow_blur = value
        self.update()

    @pyqtProperty(float)
    def scale(self) -> float:
        """Get button scale."""
        return self._scale

    @scale.setter
    def scale(self, value: float) -> None:
        """Set button scale."""
        self._scale = value
        self.update()

    def mousePressEvent(self, event: Any) -> None:
        """Handle mouse press with animation."""
        animation = self._animations.get("scale")
        if animation:
            animation.setStartValue(self._scale)
            animation.setEndValue(0.95)
            animation.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:
        """Handle mouse release with animation."""
        animation = self._animations.get("scale")
        if animation:
            animation.setStartValue(self._scale)
            animation.setEndValue(1.0)
            animation.start()
        super().mouseReleaseEvent(event)


class ModernSpinBoxBase(AnimatedWidgetBase):
    """Base class for modern spin boxes with custom styling."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_spinbox_style()

    @abstractmethod
    def _setup_spinbox_style(self) -> None:
        """Set up spinbox-specific styling."""
        pass

    def get_arrow_style(self, up: bool) -> str:
        """Get arrow button style."""
        arrow = "▲" if up else "▼"
        return f"""
            QSpinBox::{("up" if up else "down")}-button {{
                subcontrol-origin: border;
                subcontrol-position: {("top" if up else "bottom")} right;
                width: 20px;
                border: none;
                background: rgba(255, 255, 255, 0.05);
            }}

            QSpinBox::{("up" if up else "down")}-button:hover {{
                background: rgba(255, 255, 255, 0.1);
            }}

            QSpinBox::{("up" if up else "down")}-arrow {{
                image: none;
                width: 20px;
                height: 20px;
                color: rgba(255, 255, 255, 0.6);
            }}

            QSpinBox::{("up" if up else "down")}-arrow:disabled {{
                color: rgba(255, 255, 255, 0.2);
            }}

            QSpinBox::{("up" if up else "down")}-button::after {{
                content: "{arrow}";
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }}
        """


class PulseAnimationBase(QObject):
    """Base class for pulse animations on widgets."""

    def __init__(self, widget: QWidget, parent: QObject | None = None):
        super().__init__(parent)
        self.widget = widget
        self._opacity = 1.0
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_direction = -1
        self._pulse_min = 0.3
        self._pulse_max = 1.0
        self._pulse_step = 0.05

    @pyqtProperty(float)
    def opacity(self) -> float:
        """Get current opacity."""
        return self._opacity

    @opacity.setter
    def opacity(self, value: float) -> None:
        """Set current opacity."""
        self._opacity = value
        self.widget.setStyleSheet(f"opacity: {value};")

    def start(self, interval: int = 50) -> None:
        """Start pulse animation."""
        self._pulse_timer.start(interval)

    def stop(self) -> None:
        """Stop pulse animation."""
        self._pulse_timer.stop()
        self.opacity = 1.0

    def _update_pulse(self) -> None:
        """Update pulse animation state."""
        self._opacity += self._pulse_direction * self._pulse_step

        if self._opacity <= self._pulse_min:
            self._opacity = self._pulse_min
            self._pulse_direction = 1
        elif self._opacity >= self._pulse_max:
            self._opacity = self._pulse_max
            self._pulse_direction = -1

        self.opacity = self._opacity


class DebouncedActionMixin:
    """Mixin for widgets that need debounced actions."""

    def __init__(self):
        self._debounce_timers: dict[str, QTimer] = {}

    def debounce(self, action: callable, delay: int, key: str = "default") -> None:
        """Debounce an action with specified delay."""
        if key in self._debounce_timers:
            self._debounce_timers[key].stop()

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(action)
        timer.start(delay)

        self._debounce_timers[key] = timer

    def cancel_debounce(self, key: str = "default") -> None:
        """Cancel a debounced action."""
        if key in self._debounce_timers:
            self._debounce_timers[key].stop()
            del self._debounce_timers[key]
