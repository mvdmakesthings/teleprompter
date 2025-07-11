"""File management for teleprompter content."""

import os
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from ...core.protocols import ContentParserProtocol
from ...utils.logging import LoggerMixin
from .file_watcher import FileWatcher


class FileManager(QObject, LoggerMixin):
    """Manages file operations and content loading for the teleprompter.

    This class handles file loading, validation, and provides UI integration
    for file selection dialogs.
    """

    # Signals
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()
    file_loaded = pyqtSignal(str, str, str)  # html_content, file_path, markdown_content
    error_occurred = pyqtSignal(str, str)  # error_message, error_type
    file_reload_requested = pyqtSignal(str)  # file_path that needs reloading

    def __init__(self, parser: ContentParserProtocol, parent: QObject | None = None):
        """Initialize file manager.

        Args:
            parser: Content parser for markdown processing
            parent: Parent QObject
        """
        super().__init__(parent)
        self._parser = parser
        self._supported_extensions = [".md", ".markdown", ".txt"]
        self._current_file_path: str | None = None

        # Initialize file watcher
        self._file_watcher = FileWatcher(self)
        self._file_watcher.file_changed.connect(self._on_watched_file_changed)
        self._file_watcher.file_removed.connect(self._on_watched_file_removed)
        self._file_watcher.watch_error.connect(self._on_watch_error)

    def load_file(self, file_path: str) -> str:
        """Load content from a file.

        Args:
            file_path: Path to the file to load

        Returns:
            Raw file content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.validate_file(file_path):
            raise ValueError(f"Unsupported file format: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            with open(file_path, encoding="latin-1") as f:
                return f.read()

    def save_file(self, file_path: str, content: str) -> bool:
        """Save content to a file.

        Args:
            file_path: Path to save the file
            content: Content to save

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            self.log_error(f"Failed to save file {file_path}: {str(e)}")
            return False

    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file can be loaded, False otherwise
        """
        if not os.path.exists(file_path):
            return False

        if not os.path.isfile(file_path):
            return False

        # Check file extension
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self._supported_extensions

    def get_supported_extensions(self) -> list[str]:
        """Return list of supported file extensions.

        Returns:
            List of supported file extensions
        """
        return self._supported_extensions.copy()

    def open_file_dialog(self) -> None:
        """Open file dialog for selecting a file to load."""
        file_filters = (
            "Markdown Files (*.md *.markdown);;Text Files (*.txt);;All Files (*)"
        )

        file_path, _ = QFileDialog.getOpenFileName(
            self.parent(), "Open File", "", file_filters
        )

        if file_path:
            self._load_file_async(file_path)

    def _load_file_async(self, file_path: str) -> None:
        """Load file asynchronously with progress signals.

        Args:
            file_path: Path to the file to load
        """
        self.loading_started.emit()

        try:
            # Validate file
            if not self.validate_file(file_path):
                self._emit_error(
                    f"Unsupported file format: {Path(file_path).suffix}",
                    "File Format Error",
                )
                return

            # Load raw content
            markdown_content = self.load_file(file_path)

            # Parse to HTML
            html_content = self._parser.parse_content(markdown_content)

            # Emit success signal
            self.file_loaded.emit(html_content, file_path, markdown_content)

            # Store current file path and start watching
            self._current_file_path = file_path
            self._file_watcher.watch_file(file_path)

        except FileNotFoundError:
            self._emit_error(f"File not found: {file_path}", "File Not Found")
        except ValueError as e:
            self._emit_error(str(e), "File Processing Error")
        except Exception as e:
            self._emit_error(
                f"Unexpected error loading file: {str(e)}", "Loading Error"
            )
        finally:
            self.loading_finished.emit()

    def _emit_error(self, message: str, error_type: str) -> None:
        """Emit error signal and show error dialog.

        Args:
            message: Error message
            error_type: Type of error for categorization
        """
        self.log_error(f"{error_type}: {message}")
        self.error_occurred.emit(message, error_type)

        # Show error dialog
        msg_box = QMessageBox(self.parent())
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(error_type)
        msg_box.setText(message)
        msg_box.exec()

    def get_empty_state_html(self) -> str:
        """Get HTML content for empty state display.

        Returns:
            HTML content for empty state
        """
        return self._parser._generate_empty_state_html()

    def get_current_file_path(self) -> str | None:
        """Get the path of the currently loaded file.

        Returns:
            Path to the current file or None if no file is loaded
        """
        return self._current_file_path

    def reload_current_file(self) -> None:
        """Reload the currently loaded file.

        This is typically called in response to file changes detected by the watcher.
        """
        if self._current_file_path:
            self.log_info(f"Reloading file: {self._current_file_path}")
            self._load_file_async(self._current_file_path)

    def stop_watching(self) -> None:
        """Stop watching the current file."""
        self._file_watcher.stop_watching()
        self._current_file_path = None

    def set_auto_reload_enabled(self, enabled: bool) -> None:
        """Enable or disable automatic file reloading.

        Args:
            enabled: True to enable auto-reload, False to disable
        """
        if not enabled:
            self._file_watcher.stop_watching()
        elif enabled and self._current_file_path:
            self._file_watcher.watch_file(self._current_file_path)

    def _on_watched_file_changed(self, file_path: str) -> None:
        """Handle file change notification from watcher.

        Args:
            file_path: Path to the changed file
        """
        self.log_info(f"File changed: {file_path}")
        self.file_reload_requested.emit(file_path)

    def _on_watched_file_removed(self, file_path: str) -> None:
        """Handle file removal notification from watcher.

        Args:
            file_path: Path to the removed file
        """
        self.log_warning(f"Watched file was removed: {file_path}")
        self._emit_error(
            f"The file '{Path(file_path).name}' was deleted or moved.", "File Removed"
        )
        self._current_file_path = None

    def _on_watch_error(self, error_message: str) -> None:
        """Handle watch error from file watcher.

        Args:
            error_message: Error message from the watcher
        """
        self.log_error(f"File watch error: {error_message}")
        # Don't show dialog for watch errors, just log them
