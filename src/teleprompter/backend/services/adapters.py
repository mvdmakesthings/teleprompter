"""Service adapters to interface between the API and domain layers."""

import asyncio
import contextlib
from typing import Any

from ..api.models import WebSocketMessage
from ..api.models.domain import (
    FileWatchEvent,
    ScrollState,
    VoiceActivity,
    VoiceActivityState,
)
from ..api.websocket import WebSocketManager
from .file_watcher_adapter import FileWatcherAdapter as FileWatcherImpl
from .voice_adapter import VoiceDetectorAdapter as VoiceDetectorImpl


class FileWatcherAdapter:
    """Adapter for file watching functionality."""

    def __init__(self, ws_manager: WebSocketManager):
        """Initialize the file watcher adapter."""
        self.ws_manager = ws_manager
        self._file_watcher: FileWatcherImpl | None = None
        self._watched_file: str | None = None

    async def start_watching(self, file_path: str) -> bool:
        """Start watching a file for changes."""
        try:
            # Create a new file watcher with callback
            self._file_watcher = FileWatcherImpl(
                on_file_event=lambda event: asyncio.create_task(self._handle_file_event(event))
            )

            # Start watching the file
            success = self._file_watcher.watch_file(file_path)
            if success:
                self._watched_file = file_path

            return success
        except Exception as e:
            event = FileWatchEvent(
                event_type="error",
                file_path=file_path,
                error=str(e)
            )
            await self._handle_file_event(event)
            return False

    async def stop_watching(self):
        """Stop watching the current file."""
        if self._file_watcher:
            self._file_watcher.stop_watching()
            self._watched_file = None

    async def _handle_file_event(self, event: FileWatchEvent):
        """Handle file event and broadcast via WebSocket."""
        # Map event types to WebSocket events
        event_map = {
            "changed": "file_changed",
            "removed": "file_removed",
            "error": "file_watch_error"
        }

        ws_event = event_map.get(event.event_type, "file_event")

        await self.ws_manager.broadcast(
            WebSocketMessage(
                event=ws_event,
                data=event.model_dump(),
            )
        )


class VoiceDetectorAdapter:
    """Adapter for voice detection functionality."""

    def __init__(self, ws_manager: WebSocketManager):
        """Initialize the voice detector adapter."""
        self.ws_manager = ws_manager
        self._voice_detector: VoiceDetectorImpl | None = None

    async def start_detection(self, sensitivity: int = 2) -> bool:
        """Start voice detection."""
        try:
            # Create voice detector with callback
            self._voice_detector = VoiceDetectorImpl(
                on_voice_activity=lambda activity: asyncio.create_task(
                    self._handle_voice_activity(activity)
                )
            )

            # Set sensitivity
            self._voice_detector.set_sensitivity(sensitivity)

            # Start detection
            self._voice_detector.start()

            return True
        except Exception:
            activity = VoiceActivity(
                state=VoiceActivityState.ERROR,
                is_speaking=False,
                audio_level=0.0,
                sensitivity=sensitivity
            )
            await self._handle_voice_activity(activity)
            return False

    async def stop_detection(self):
        """Stop voice detection."""
        if self._voice_detector:
            self._voice_detector.stop()
            self._voice_detector = None

    async def _handle_voice_activity(self, activity: VoiceActivity):
        """Handle voice activity and broadcast via WebSocket."""
        await self.ws_manager.broadcast(
            WebSocketMessage(
                event="voice_activity",
                data=activity.model_dump(),
            )
        )

        # Also send specific events for state changes
        if activity.state == VoiceActivityState.SPEAKING:
            await self.ws_manager.broadcast(
                WebSocketMessage(
                    event="voice_started",
                    data={"timestamp": activity.timestamp.isoformat()},
                )
            )
        elif activity.state == VoiceActivityState.LISTENING and hasattr(self, '_was_speaking'):
            await self.ws_manager.broadcast(
                WebSocketMessage(
                    event="voice_stopped",
                    data={"timestamp": activity.timestamp.isoformat()},
                )
            )

        # Track speaking state
        self._was_speaking = activity.state == VoiceActivityState.SPEAKING


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
            with contextlib.suppress(asyncio.CancelledError):
                await self._scroll_task
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
        return ScrollState(
            position=self._position,
            speed=self._speed,
            is_playing=self._is_playing
        ).model_dump()

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
                    state = ScrollState(
                        position=self._position,
                        speed=self._speed,
                        is_playing=self._is_playing
                    )

                    await self.ws_manager.broadcast(
                        WebSocketMessage(
                            event="scroll_position",
                            data=state.model_dump(),
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
