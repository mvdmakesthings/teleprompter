"""Service adapters to interface between the API and domain layers."""

import asyncio
from typing import Any

from ...core.container import get_container
from ...core.protocols import (
    FileWatcherProtocol,
    VoiceDetectorProtocol,
)
from ..api.models import WebSocketMessage
from ..api.websocket import WebSocketManager


class FileWatcherAdapter:
    """Adapter for file watching functionality."""

    def __init__(self, ws_manager: WebSocketManager):
        """Initialize the file watcher adapter."""
        self.ws_manager = ws_manager
        self._file_watcher = None
        self._watched_file = None

    async def start_watching(self, file_path: str) -> bool:
        """Start watching a file for changes."""
        try:
            container = get_container()
            self._file_watcher = container.get(FileWatcherProtocol)

            # Stop any existing watch
            if self._file_watcher.is_watching():
                self._file_watcher.stop_watching()

            # Start watching the new file
            success = self._file_watcher.watch_file(file_path)
            if success:
                self._watched_file = file_path

                # Connect signals to WebSocket broadcasts
                # Note: In the refactored version, we'll need to adapt
                # Qt signals to async callbacks
                await self._setup_signal_handlers()

            return success
        except Exception as e:
            await self.ws_manager.broadcast(
                WebSocketMessage(
                    event="file_watch_error",
                    data={"error": str(e), "file": file_path},
                )
            )
            return False

    async def stop_watching(self):
        """Stop watching the current file."""
        if self._file_watcher:
            self._file_watcher.stop_watching()
            self._watched_file = None

    async def _setup_signal_handlers(self):
        """Set up handlers for file watcher signals."""
        # In the refactored version, this will connect to async callbacks
        # For now, this is a placeholder
        pass

    async def _on_file_changed(self):
        """Handle file change event."""
        await self.ws_manager.broadcast(
            WebSocketMessage(
                event="file_changed",
                data={"file": self._watched_file},
            )
        )

    async def _on_file_removed(self):
        """Handle file removal event."""
        await self.ws_manager.broadcast(
            WebSocketMessage(
                event="file_removed",
                data={"file": self._watched_file},
            )
        )


class VoiceDetectorAdapter:
    """Adapter for voice detection functionality."""

    def __init__(self, ws_manager: WebSocketManager):
        """Initialize the voice detector adapter."""
        self.ws_manager = ws_manager
        self._voice_detector = None
        self._detection_task = None

    async def start_detection(self, sensitivity: int = 2) -> bool:
        """Start voice detection."""
        try:
            container = get_container()
            self._voice_detector = container.get(VoiceDetectorProtocol)

            # Set sensitivity
            self._voice_detector.set_sensitivity(sensitivity)

            # Start detection
            self._voice_detector.start()

            # Start monitoring task
            self._detection_task = asyncio.create_task(self._monitor_voice())

            return True
        except Exception as e:
            await self.ws_manager.broadcast(
                WebSocketMessage(
                    event="voice_error",
                    data={"error": str(e)},
                )
            )
            return False

    async def stop_detection(self):
        """Stop voice detection."""
        if self._detection_task:
            self._detection_task.cancel()
            self._detection_task = None

        if self._voice_detector:
            self._voice_detector.stop()

    async def _monitor_voice(self):
        """Monitor voice activity and broadcast updates."""
        # In the refactored version, this will poll the voice detector
        # and broadcast updates via WebSocket
        # For now, this is a placeholder that would be implemented
        # when we remove Qt dependencies
        while True:
            try:
                await asyncio.sleep(0.1)  # Poll every 100ms

                if self._voice_detector and self._voice_detector.is_running():
                    audio_level = self._voice_detector.get_audio_level()

                    # Broadcast audio level
                    await self.ws_manager.broadcast(
                        WebSocketMessage(
                            event="voice_level",
                            data={"level": audio_level},
                        )
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.ws_manager.broadcast(
                    WebSocketMessage(
                        event="voice_error",
                        data={"error": str(e)},
                    )
                )


class ScrollControllerAdapter:
    """Adapter for scroll control functionality."""

    def __init__(self, ws_manager: WebSocketManager):
        """Initialize the scroll controller adapter."""
        self.ws_manager = ws_manager
        self._position = 0.0
        self._speed = 1.0
        self._is_playing = False
        self._scroll_task = None

    async def start_scrolling(self):
        """Start scrolling."""
        self._is_playing = True
        if not self._scroll_task:
            self._scroll_task = asyncio.create_task(self._scroll_loop())

    async def stop_scrolling(self):
        """Stop scrolling."""
        self._is_playing = False
        if self._scroll_task:
            self._scroll_task.cancel()
            self._scroll_task = None
        self._position = 0.0

    async def pause_scrolling(self):
        """Pause scrolling."""
        self._is_playing = False

    def set_speed(self, speed: float):
        """Set scroll speed."""
        self._speed = max(0.05, min(5.0, speed))

    def set_position(self, position: float):
        """Set scroll position."""
        self._position = max(0.0, min(1.0, position))

    def get_state(self) -> dict[str, Any]:
        """Get current scroll state."""
        return {
            "is_playing": self._is_playing,
            "speed": self._speed,
            "position": self._position,
        }

    async def _scroll_loop(self):
        """Main scrolling loop."""
        while True:
            try:
                if self._is_playing and self._position < 1.0:
                    # Calculate position increment based on speed
                    # This is a simplified calculation
                    increment = 0.001 * self._speed
                    self._position = min(1.0, self._position + increment)

                    # Broadcast position update
                    await self.ws_manager.broadcast(
                        WebSocketMessage(
                            event="scroll_position",
                            data={"position": self._position},
                        )
                    )

                    # If reached the end, stop
                    if self._position >= 1.0:
                        self._is_playing = False
                        await self.ws_manager.broadcast(
                            WebSocketMessage(
                                event="scroll_finished",
                                data={},
                            )
                        )

                await asyncio.sleep(1/60)  # 60 FPS
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.ws_manager.broadcast(
                    WebSocketMessage(
                        event="scroll_error",
                        data={"error": str(e)},
                    )
                )
