"""Keyboard command handling for the teleprompter widget."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

if TYPE_CHECKING:
    from .teleprompter_widget import TeleprompterWidget


class KeyboardCommand(ABC):
    """Abstract base class for keyboard commands."""

    @abstractmethod
    def execute(self, widget: TeleprompterWidget) -> bool:
        """Execute the command.

        Args:
            widget: The teleprompter widget instance

        Returns:
            True if the event was handled, False otherwise
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """Get a description of what this command does."""
        pass


class PlayPauseCommand(KeyboardCommand):
    """Toggle play/pause state."""

    def execute(self, widget) -> bool:
        widget.toggle_playback()
        return True

    def description(self) -> str:
        return "Toggle play/pause"


class ResetPositionCommand(KeyboardCommand):
    """Reset scroll position to top."""

    def execute(self, widget) -> bool:
        widget.reset()
        return True

    def description(self) -> str:
        return "Reset to beginning"


class IncreaseSpeedCommand(KeyboardCommand):
    """Increase scroll speed."""

    def __init__(self, step: float = 0.1):
        self.step = step

    def execute(self, widget) -> bool:
        widget.adjust_speed(self.step)
        return True

    def description(self) -> str:
        return f"Increase speed by {self.step}"


class DecreaseSpeedCommand(KeyboardCommand):
    """Decrease scroll speed."""

    def __init__(self, step: float = 0.1):
        self.step = step

    def execute(self, widget) -> bool:
        widget.adjust_speed(-self.step)
        return True

    def description(self) -> str:
        return f"Decrease speed by {self.step}"


class JumpCommand(KeyboardCommand):
    """Jump forward or backward by a percentage."""

    def __init__(self, percentage: float):
        self.percentage = percentage

    def execute(self, widget) -> bool:
        widget.jump_by_percentage(self.percentage)
        return True

    def description(self) -> str:
        direction = "forward" if self.percentage > 0 else "backward"
        return f"Jump {direction} by {abs(self.percentage)}%"


class NavigateSectionCommand(KeyboardCommand):
    """Navigate to next or previous section."""

    def __init__(self, direction: str):
        if direction not in ("next", "previous"):
            raise ValueError("Direction must be 'next' or 'previous'")
        self.direction = direction

    def execute(self, widget) -> bool:
        if self.direction == "next":
            widget.navigate_to_next_section()
        else:
            widget.navigate_to_previous_section()
        return True

    def description(self) -> str:
        return f"Go to {self.direction} section"


class ToggleVoiceControlCommand(KeyboardCommand):
    """Toggle voice control on/off."""

    def execute(self, widget) -> bool:
        widget.toggle_voice_control()
        return True

    def description(self) -> str:
        return "Toggle voice control"


class ToggleCursorCommand(KeyboardCommand):
    """Toggle cursor visibility."""

    def execute(self, widget) -> bool:
        widget.toggle_cursor_visibility()
        return True

    def description(self) -> str:
        return "Toggle cursor visibility"


class EscapeCommand(KeyboardCommand):
    """Handle escape key - exit fullscreen or stop."""

    def execute(self, widget) -> bool:
        if widget.isFullScreen():
            widget.window().showNormal()
        else:
            widget.pause()
        return True

    def description(self) -> str:
        return "Exit fullscreen or stop scrolling"


class KeyboardCommandRegistry:
    """Registry for keyboard commands with key mapping."""

    def __init__(self):
        self._commands: dict[int, KeyboardCommand] = {}
        self._register_default_commands()

    def _register_default_commands(self):
        """Register default keyboard commands."""
        # Playback controls
        self._commands[Qt.Key.Key_Space] = PlayPauseCommand()
        self._commands[Qt.Key.Key_R] = ResetPositionCommand()
        self._commands[Qt.Key.Key_Escape] = EscapeCommand()

        # Speed controls
        self._commands[Qt.Key.Key_Plus] = IncreaseSpeedCommand()
        self._commands[Qt.Key.Key_Equal] = IncreaseSpeedCommand()  # For + without shift
        self._commands[Qt.Key.Key_Minus] = DecreaseSpeedCommand()

        # Navigation
        self._commands[Qt.Key.Key_Right] = NavigateSectionCommand("next")
        self._commands[Qt.Key.Key_Left] = NavigateSectionCommand("previous")
        self._commands[Qt.Key.Key_Up] = IncreaseSpeedCommand(0.1)
        self._commands[Qt.Key.Key_Down] = DecreaseSpeedCommand(0.1)
        self._commands[Qt.Key.Key_PageUp] = NavigateSectionCommand("previous")
        self._commands[Qt.Key.Key_PageDown] = NavigateSectionCommand("next")

        # Feature toggles
        self._commands[Qt.Key.Key_V] = ToggleVoiceControlCommand()
        self._commands[Qt.Key.Key_C] = ToggleCursorCommand()

    def register_command(self, key: Qt.Key, command: KeyboardCommand):
        """Register a custom keyboard command.

        Args:
            key: The Qt key to bind to
            command: The command to execute
        """
        self._commands[key] = command

    def unregister_command(self, key: Qt.Key):
        """Remove a keyboard command.

        Args:
            key: The Qt key to unbind
        """
        self._commands.pop(key, None)

    def handle_key_press(self, event: QKeyEvent, widget) -> bool:
        """Handle a key press event.

        Args:
            event: The key press event
            widget: The widget that received the event

        Returns:
            True if the event was handled, False otherwise
        """
        key = event.key()

        if key in self._commands:
            command = self._commands[key]
            return command.execute(widget)

        return False

    def get_shortcuts_help(self) -> dict[str, str]:
        """Get a dictionary of keyboard shortcuts and their descriptions.

        Returns:
            Dictionary mapping key names to descriptions
        """
        shortcuts = {}

        key_names = {
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_R: "R",
            Qt.Key.Key_Escape: "Esc",
            Qt.Key.Key_Plus: "+",
            Qt.Key.Key_Equal: "+",
            Qt.Key.Key_Minus: "-",
            Qt.Key.Key_Right: "→",
            Qt.Key.Key_Left: "←",
            Qt.Key.Key_Up: "↑",
            Qt.Key.Key_Down: "↓",
            Qt.Key.Key_PageUp: "PgUp",
            Qt.Key.Key_PageDown: "PgDn",
            Qt.Key.Key_V: "V",
            Qt.Key.Key_C: "C",
        }

        for key, command in self._commands.items():
            if key in key_names:
                shortcuts[key_names[key]] = command.description()

        return shortcuts
