"""File watching service for automatic content reloading."""

import os

from PyQt6.QtCore import QFileSystemWatcher, QObject, QTimer, pyqtSignal

from ...utils.logging import LoggerMixin


class FileWatcher(QObject, LoggerMixin):
    """Monitor files for changes and emit signals when modifications occur.

    This service uses QFileSystemWatcher to detect file modifications and
    includes debouncing to prevent multiple rapid reloads.
    """

    # Signals
    file_changed = pyqtSignal(str)  # Emitted when watched file is modified
    file_removed = pyqtSignal(str)  # Emitted when watched file is deleted
    watch_error = pyqtSignal(str)  # Emitted when watching fails

    def __init__(self, parent: QObject | None = None):
        """Initialize the file watcher.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)

        # File system watcher
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_file_changed)

        # Current watched file
        self._current_file: str | None = None

        # Debounce timer to prevent rapid reloads
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_file_changed)
        self._debounce_delay = 500  # milliseconds

        # Track if we're waiting to emit
        self._pending_file: str | None = None

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
            self.watch_error.emit(f"File not found: {file_path}")
            return False

        # Add file to watcher
        if self._watcher.addPath(file_path):
            self._current_file = file_path
            self.log_info(f"Started watching file: {file_path}")
            return True
        else:
            self.log_error(f"Failed to watch file: {file_path}")
            self.watch_error.emit(f"Failed to watch file: {file_path}")
            return False

    def stop_watching(self) -> None:
        """Stop watching the current file."""
        if self._current_file:
            self._watcher.removePath(self._current_file)
            self.log_info(f"Stopped watching file: {self._current_file}")
            self._current_file = None
            self._pending_file = None
            self._debounce_timer.stop()

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

    def set_debounce_delay(self, delay_ms: int) -> None:
        """Set the debounce delay for file change notifications.

        Args:
            delay_ms: Delay in milliseconds
        """
        self._debounce_delay = max(0, delay_ms)

    def _on_file_changed(self, file_path: str) -> None:
        """Handle file change notification from QFileSystemWatcher.

        Args:
            file_path: Path to the changed file
        """
        self.log_debug(f"File change detected: {file_path}")

        # Check if file still exists
        if not os.path.exists(file_path):
            self.log_warning(f"Watched file was removed: {file_path}")
            self.file_removed.emit(file_path)
            self.stop_watching()
            return

        # QFileSystemWatcher stops watching after a file is modified on some systems
        # Re-add the file to continue watching
        if file_path not in self._watcher.files():
            self.log_debug(f"Re-adding file to watcher: {file_path}")
            self._watcher.addPath(file_path)

        # Start or restart debounce timer
        self._pending_file = file_path
        self._debounce_timer.stop()
        self._debounce_timer.start(self._debounce_delay)
        self.log_debug(f"Started debounce timer for {self._debounce_delay}ms")

    def _emit_file_changed(self) -> None:
        """Emit the file changed signal after debounce delay."""
        if self._pending_file:
            self.log_info(f"File changed: {self._pending_file}")
            self.file_changed.emit(self._pending_file)
            self._pending_file = None
