"""File watcher service adapter without Qt dependencies."""

import os
import threading
from collections.abc import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ..api.models.domain import FileWatchEvent


class FileWatcherAdapter:
    """File watcher adapter using watchdog library."""

    def __init__(self, on_file_event: Callable[[FileWatchEvent], None] | None = None):
        """Initialize the file watcher adapter.
        
        Args:
            on_file_event: Callback for file events
        """
        self.on_file_event = on_file_event

        # Watchdog components
        self._observer = Observer()
        self._current_file: str | None = None
        self._event_handler: FileEventHandler | None = None

        # Debouncing
        self._debounce_delay = 0.5  # seconds
        self._debounce_timer: threading.Timer | None = None
        self._pending_event: FileWatchEvent | None = None
        self._debounce_lock = threading.Lock()

    def watch_file(self, file_path: str) -> bool:
        """Start watching a file for changes.
        
        Args:
            file_path: Path to the file to watch
            
        Returns:
            True if watching was successful, False otherwise
        """
        try:
            # Stop watching current file
            self.stop_watching()

            # Validate file exists
            if not os.path.exists(file_path):
                self._emit_event(FileWatchEvent(
                    event_type="error",
                    file_path=file_path,
                    error=f"File not found: {file_path}"
                ))
                return False

            # Create event handler
            self._event_handler = FileEventHandler(
                file_path=file_path,
                on_event=self._handle_file_event
            )

            # Watch the parent directory
            parent_dir = os.path.dirname(file_path)
            self._observer.schedule(
                self._event_handler,
                parent_dir,
                recursive=False
            )

            # Start observer
            self._observer.start()
            self._current_file = file_path

            return True

        except Exception as e:
            self._emit_event(FileWatchEvent(
                event_type="error",
                file_path=file_path,
                error=str(e)
            ))
            return False

    def stop_watching(self) -> None:
        """Stop watching the current file."""
        if self._observer.is_alive():
            self._observer.stop()
            self._observer.join(timeout=1)

        # Clear observer handlers
        self._observer.unschedule_all()

        # Create new observer for next watch
        self._observer = Observer()

        # Cancel any pending debounce
        with self._debounce_lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()
                self._debounce_timer = None

        self._current_file = None
        self._event_handler = None

    def get_watched_file(self) -> str | None:
        """Get the currently watched file path."""
        return self._current_file

    def is_watching(self) -> bool:
        """Check if currently watching a file."""
        return self._current_file is not None and self._observer.is_alive()

    def set_debounce_delay(self, delay_ms: int) -> None:
        """Set the debounce delay for file change notifications.
        
        Args:
            delay_ms: Delay in milliseconds
        """
        if delay_ms < 0:
            raise ValueError("Debounce delay must be non-negative")
        self._debounce_delay = delay_ms / 1000.0

    def _handle_file_event(self, event: FileWatchEvent) -> None:
        """Handle file event with debouncing."""
        with self._debounce_lock:
            # Cancel existing timer
            if self._debounce_timer:
                self._debounce_timer.cancel()

            # Store pending event
            self._pending_event = event

            # Start new timer
            self._debounce_timer = threading.Timer(
                self._debounce_delay,
                self._emit_pending_event
            )
            self._debounce_timer.start()

    def _emit_pending_event(self) -> None:
        """Emit the pending event after debounce delay."""
        with self._debounce_lock:
            if self._pending_event:
                self._emit_event(self._pending_event)
                self._pending_event = None

    def _emit_event(self, event: FileWatchEvent) -> None:
        """Emit file event to callback."""
        if self.on_file_event:
            self.on_file_event(event)


class FileEventHandler(FileSystemEventHandler):
    """Handler for file system events."""

    def __init__(self, file_path: str, on_event: Callable[[FileWatchEvent], None]):
        """Initialize the event handler.
        
        Args:
            file_path: Path to the file being watched
            on_event: Callback for events
        """
        super().__init__()
        self.file_path = os.path.abspath(file_path)
        self.on_event = on_event

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification event."""
        if not event.is_directory and os.path.abspath(event.src_path) == self.file_path:
            self.on_event(FileWatchEvent(
                event_type="changed",
                file_path=self.file_path
            ))

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion event."""
        if not event.is_directory and os.path.abspath(event.src_path) == self.file_path:
            self.on_event(FileWatchEvent(
                event_type="removed",
                file_path=self.file_path
            ))

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move event."""
        if hasattr(event, 'src_path') and hasattr(event, 'dest_path'):
            src_path = os.path.abspath(event.src_path)

            # Check if our file was moved
            if not event.is_directory and src_path == self.file_path:
                self.on_event(FileWatchEvent(
                    event_type="removed",
                    file_path=self.file_path
                ))

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation event."""
        # If our file is recreated after deletion
        if not event.is_directory and os.path.abspath(event.src_path) == self.file_path:
            self.on_event(FileWatchEvent(
                event_type="changed",
                file_path=self.file_path
            ))
