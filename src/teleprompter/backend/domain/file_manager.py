"""File management for teleprompter content without Qt dependencies."""

import os
from collections.abc import Callable
from pathlib import Path

from teleprompter.backend.api.models.domain import FileWatchEvent
from teleprompter.backend.services.file_watcher_adapter import FileWatcherAdapter
from teleprompter.backend.utils.logging import LoggerMixin
from teleprompter.core.protocols import ContentParserProtocol


class FileManager(LoggerMixin):
    """Manages file operations and content loading for the teleprompter.
    
    This class handles file loading, validation, and file watching
    without Qt dependencies.
    """

    def __init__(
        self,
        parser: ContentParserProtocol,
        on_loading_started: Callable[[], None] | None = None,
        on_loading_finished: Callable[[], None] | None = None,
        on_file_loaded: Callable[[str, str, str], None] | None = None,
        on_error_occurred: Callable[[str, str], None] | None = None,
        on_file_reload_requested: Callable[[str], None] | None = None,
    ):
        """Initialize file manager.
        
        Args:
            parser: Content parser for markdown processing
            on_loading_started: Callback when loading starts
            on_loading_finished: Callback when loading finishes
            on_file_loaded: Callback when file is loaded (html, path, markdown)
            on_error_occurred: Callback when error occurs (message, type)
            on_file_reload_requested: Callback when file reload is requested (path)
        """
        self._parser = parser
        self._supported_extensions = [".md", ".markdown", ".txt"]
        self._current_file_path: str | None = None

        # Callbacks
        self.on_loading_started = on_loading_started
        self.on_loading_finished = on_loading_finished
        self.on_file_loaded = on_file_loaded
        self.on_error_occurred = on_error_occurred
        self.on_file_reload_requested = on_file_reload_requested

        # Initialize file watcher
        self._file_watcher = FileWatcherAdapter(on_file_event=self._handle_file_event)
        self._auto_reload_enabled = True

    def _handle_file_event(self, event: FileWatchEvent) -> None:
        """Handle file events from the watcher.
        
        Args:
            event: File event information
        """
        if event.event_type == "changed":
            self._on_watched_file_changed(event.file_path)
        elif event.event_type == "removed":
            self._on_watched_file_removed(event.file_path)
        elif event.event_type == "error":
            self._on_watch_error(event.error or "Unknown error")

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

    def load_file_async(self, file_path: str) -> None:
        """Load file asynchronously with progress callbacks.
        
        Args:
            file_path: Path to the file to load
        """
        if self.on_loading_started:
            self.on_loading_started()

        try:
            # Validate file
            if not self.validate_file(file_path):
                self._emit_error(
                    f"Unsupported file format: {Path(file_path).suffix}",
                    "File Format Error"
                )
                return

            # Load raw content
            markdown_content = self.load_file(file_path)

            # Parse to HTML
            html_content = self._parser.parse_content(markdown_content)

            # Emit success callback
            if self.on_file_loaded:
                self.on_file_loaded(html_content, file_path, markdown_content)

            # Store current file path and start watching
            self._current_file_path = file_path
            if self._auto_reload_enabled:
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
            if self.on_loading_finished:
                self.on_loading_finished()

    def _emit_error(self, message: str, error_type: str) -> None:
        """Emit error through callback.
        
        Args:
            message: Error message
            error_type: Type of error for categorization
        """
        self.log_error(f"{error_type}: {message}")
        if self.on_error_occurred:
            self.on_error_occurred(message, error_type)

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
            self.load_file_async(self._current_file_path)

    def stop_watching(self) -> None:
        """Stop watching the current file."""
        self._file_watcher.stop_watching()
        self._current_file_path = None

    def set_auto_reload_enabled(self, enabled: bool) -> None:
        """Enable or disable automatic file reloading.
        
        Args:
            enabled: True to enable auto-reload, False to disable
        """
        self._auto_reload_enabled = enabled
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
        if self.on_file_reload_requested:
            self.on_file_reload_requested(file_path)

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
