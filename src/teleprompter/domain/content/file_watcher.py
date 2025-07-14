"""File watching service for automatic content reloading."""

import os
import threading
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from ...utils.logging import LoggerMixin


class FileWatcher(LoggerMixin):
    """Monitor files for changes and notify via callbacks.

    This service uses the watchdog library to detect file modifications and
    includes debouncing to prevent multiple rapid reloads.
    """

    def __init__(self):
        """Initialize the file watcher."""
        super().__init__()

        # File system watcher
        self._observer = Observer()
        self._current_file: str | None = None
        self._debounce_delay = 0.5  # seconds
        self._debounce_timer: Optional[threading.Timer] = None
        self._pending_file: str | None = None

        # Callback functions
        self.on_file_changed: Optional[Callable[[str], None]] = None
        self.on_file_removed: Optional[Callable[[str], None]] = None
        self.on_watch_error: Optional[Callable[[str], None]] = None

        # Event handler
        self._event_handler = self._create_event_handler()

    def _create_event_handler(self):
        """Create watchdog event handler."""
        class Handler(FileSystemEventHandler):
            def __init__(self, watcher):
                self.watcher = watcher
                
            def on_modified(self, event):
                if not event.is_directory and event.src_path == self.watcher._current_file:
                    self.watcher._on_file_changed(event.src_path)
                    
            def on_deleted(self, event):
                if not event.is_directory and event.src_path == self.watcher._current_file:
                    self.watcher._on_file_removed(event.src_path)
                    
        return Handler(self)

    def watch_file(self, file_path: str) -> bool:
        """Start watching a file for changes.

        Args:
            file_path: Path to the file to watch

        Returns:
            True if watching was successful, False otherwise
        """
        # Stop watching current file if any
        self.stop_watching()

        # Validate file exists
        if not os.path.exists(file_path):
            self.log_error(f"Cannot watch non-existent file: {file_path}")
            if self.on_watch_error:
                self.on_watch_error(f"File not found: {file_path}")
            return False

        try:
            # Watch the directory containing the file
            file_path = os.path.abspath(file_path)
            directory = os.path.dirname(file_path)
            
            self._observer.schedule(self._event_handler, directory, recursive=False)
            self._observer.start()
            
            self._current_file = file_path
            self.log_info(f"Started watching file: {file_path}")
            return True
        except Exception as e:
            self.log_error(f"Failed to watch file: {file_path}, error: {str(e)}")
            if self.on_watch_error:
                self.on_watch_error(f"Failed to watch file: {file_path}")
            return False

    def stop_watching(self) -> None:
        """Stop watching the current file."""
        if self._current_file:
            try:
                self._observer.stop()
                self._observer.join()
                # Create new observer for next watch
                self._observer = Observer()
            except Exception as e:
                self.log_error(f"Error stopping file watcher: {str(e)}")
                
            self.log_info(f"Stopped watching file: {self._current_file}")
            self._current_file = None
            self._pending_file = None
            
            # Cancel any pending debounce timer
            if self._debounce_timer:
                self._debounce_timer.cancel()
                self._debounce_timer = None

    def get_watched_file(self) -> str | None:
        """Get the currently watched file path.

        Returns:
            Path to the watched file or None if not watching
        """
        return self._current_file

    def is_watching(self) -> bool:
        """Check if currently watching a file.

        Returns:
            True if watching a file, False otherwise
        """
        return self._current_file is not None

    def set_debounce_delay(self, delay_seconds: float) -> None:
        """Set the debounce delay for file change notifications.

        Args:
            delay_seconds: Delay in seconds
        """
        self._debounce_delay = max(0, delay_seconds)

    def _on_file_changed(self, file_path: str) -> None:
        """Handle file change notification from watchdog.

        Args:
            file_path: Path to the changed file
        """
        self.log_debug(f"File change detected: {file_path}")

        # Check if file still exists
        if not os.path.exists(file_path):
            self.log_warning(f"Watched file was removed: {file_path}")
            self._on_file_removed(file_path)
            return

        # Cancel previous timer and start new one for debouncing
        if self._debounce_timer:
            self._debounce_timer.cancel()
            
        self._pending_file = file_path
        self._debounce_timer = threading.Timer(self._debounce_delay, self._emit_file_changed)
        self._debounce_timer.start()
        self.log_debug(f"Started debounce timer for {self._debounce_delay}s")

    def _on_file_removed(self, file_path: str) -> None:
        """Handle file removal notification.

        Args:
            file_path: Path to the removed file
        """
        self.log_warning(f"Watched file was removed: {file_path}")
        if self.on_file_removed:
            self.on_file_removed(file_path)
        self.stop_watching()

    def _emit_file_changed(self) -> None:
        """Emit the file changed signal after debounce delay."""
        if self._pending_file:
            self.log_info(f"File changed: {self._pending_file}")
            if self.on_file_changed:
                self.on_file_changed(self._pending_file)
            self._pending_file = None
