"""File management for teleprompter content."""

import os
from pathlib import Path
from typing import Callable, Optional

from ...core.protocols import ContentParserProtocol
from ...utils.logging import LoggerMixin
from .file_watcher import FileWatcher


class FileManager(LoggerMixin):
    """Manages file operations and content loading for the teleprompter.

    This class handles file loading, validation, and content processing.
    """

    def __init__(self, parser: ContentParserProtocol):
        """Initialize file manager.

        Args:
            parser: Content parser for markdown processing
        """
        super().__init__()
        self._parser = parser
        self._supported_extensions = [".md", ".markdown", ".txt"]
        self._current_file_path: str | None = None

        # Initialize file watcher
        self._file_watcher = FileWatcher()
        
        # Callback functions that can be set by consumers
        self.on_file_changed: Optional[Callable[[str], None]] = None
        self.on_file_removed: Optional[Callable[[str], None]] = None
        self.on_watch_error: Optional[Callable[[str], None]] = None

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

    def load_file_with_processing(self, file_path: str) -> tuple[str, str]:
        """Load file and process it to HTML.

        Args:
            file_path: Path to the file to load

        Returns:
            Tuple of (html_content, markdown_content)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        # Validate file
        if not self.validate_file(file_path):
            raise ValueError(f"Unsupported file format: {Path(file_path).suffix}")

        # Load raw content
        markdown_content = self.load_file(file_path)

        # Parse to HTML
        html_content = self._parser.parse_content(markdown_content)

        # Store current file path and start watching
        self._current_file_path = file_path
        self._file_watcher.watch_file(file_path)
        
        # Set up file watcher callbacks
        self._file_watcher.on_file_changed = self._on_watched_file_changed
        self._file_watcher.on_file_removed = self._on_watched_file_removed
        self._file_watcher.on_watch_error = self._on_watch_error

        return html_content, markdown_content

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

    def reload_current_file(self) -> tuple[str, str] | None:
        """Reload the currently loaded file.

        This is typically called in response to file changes detected by the watcher.
        
        Returns:
            Tuple of (html_content, markdown_content) if successful, None otherwise
        """
        if self._current_file_path:
            self.log_info(f"Reloading file: {self._current_file_path}")
            try:
                return self.load_file_with_processing(self._current_file_path)
            except Exception as e:
                self.log_error(f"Failed to reload file: {str(e)}")
                return None
        return None

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
        if self.on_file_changed:
            self.on_file_changed(file_path)

    def _on_watched_file_removed(self, file_path: str) -> None:
        """Handle file removal notification from watcher.

        Args:
            file_path: Path to the removed file
        """
        self.log_warning(f"Watched file was removed: {file_path}")
        self._current_file_path = None
        if self.on_file_removed:
            self.on_file_removed(file_path)

    def _on_watch_error(self, error_message: str) -> None:
        """Handle watch error from file watcher.

        Args:
            error_message: Error message from the watcher
        """
        self.log_error(f"File watch error: {error_message}")
        if self.on_watch_error:
            self.on_watch_error(error_message)
