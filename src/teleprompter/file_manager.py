"""File operations management for the teleprompter application."""

import os

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QWidget

from . import config
from .markdown_parser import MarkdownParser


class FileManager(QObject):
    """Manages file operations with loading states and error handling."""

    # Signals
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()
    file_loaded = pyqtSignal(str, str, str)  # html_content, file_path, markdown_content
    error_occurred = pyqtSignal(str, str)  # error_message, error_type

    def __init__(self, parent: QWidget | None = None):
        """Initialize the file manager.

        Args:
            parent: Parent widget for dialogs
        """
        super().__init__()
        self.parent = parent
        self.parser = MarkdownParser()
        self.current_file: str | None = None
        self.current_markdown_content = ""

    def open_file_dialog(self) -> str | None:
        """Open file dialog and return selected file path.

        Returns:
            Selected file path or None if cancelled
        """
        file_filter = "Markdown files (" + " ".join(config.MARKDOWN_EXTENSIONS) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Open Markdown File", "", file_filter
        )

        if file_path:
            self.load_file(file_path)
            return file_path
        return None

    def load_file(self, file_path: str):
        """Load a file with proper loading and error state management.

        Args:
            file_path: Path to the file to load
        """
        self.loading_started.emit()

        try:
            # Validate file
            self._validate_file(file_path)

            # Read and parse file
            with open(file_path, encoding="utf-8") as f:
                markdown_content = f.read()

            # Parse content
            html_content = self.parser.parse_file(file_path)

            # Store current state
            self.current_file = file_path
            self.current_markdown_content = markdown_content

            # Emit success
            self.file_loaded.emit(html_content, file_path, markdown_content)

        except FileNotFoundError as e:
            self.error_occurred.emit(str(e), "File Not Found")
        except PermissionError as e:
            self.error_occurred.emit(str(e), "Permission Denied")
        except UnicodeDecodeError:
            self.error_occurred.emit(
                "File contains invalid text encoding. Please save the file as UTF-8.",
                "Encoding Error",
            )
        except ValueError as e:
            self.error_occurred.emit(str(e), "File Error")
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)}", "Unknown Error")
        finally:
            self.loading_finished.emit()

    def _validate_file(self, file_path: str):
        """Validate file before loading.

        Args:
            file_path: Path to validate

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
            ValueError: If file is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {file_path}")

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > config.MAX_FILE_SIZE:
            raise ValueError(
                f"File too large ({file_size} bytes). Maximum size is {config.MAX_FILE_SIZE} bytes."
            )

        if file_size == 0:
            raise ValueError("File is empty")

    def get_loading_html(self) -> str:
        """Get HTML for loading state."""
        return self.parser._generate_loading_html()

    def get_error_html(self, error_message: str, error_type: str = "Error") -> str:
        """Get HTML for error state.

        Args:
            error_message: The error message to display
            error_type: Type of error

        Returns:
            HTML string for error display
        """
        return self.parser._generate_error_html(error_message, error_type)

    def get_empty_state_html(self) -> str:
        """Get HTML for empty state."""
        return self.parser._generate_empty_state_html()

    def get_error_suggestions(self, error_message: str) -> str:
        """Get helpful suggestions based on error type.

        Args:
            error_message: The error message

        Returns:
            Formatted suggestions string
        """
        suggestions = f"{error_message}\\n\\n"

        if "not found" in error_message.lower():
            suggestions += "Suggestions:\\n• Check that the file path is correct\\n• Ensure the file hasn't been moved or deleted\\n• Try browsing for the file again"
        elif "permission" in error_message.lower():
            suggestions += "Suggestions:\\n• Check file permissions\\n• Try running as administrator\\n• Ensure the file is not locked by another program"
        elif "encoding" in error_message.lower():
            suggestions += "Suggestions:\\n• Save the file with UTF-8 encoding\\n• Try opening with a text editor first\\n• Check for special characters in the file"
        elif "size" in error_message.lower():
            suggestions += "Suggestions:\\n• Split large documents into smaller files\\n• Remove unnecessary content\\n• Consider using a more powerful text editor"
        else:
            suggestions += "Suggestions:\\n• Try opening a different file\\n• Check the file format is supported\\n• Restart the application if problems persist"

        return suggestions

    @property
    def has_file(self) -> bool:
        """Check if a file is currently loaded."""
        return self.current_file is not None

    def get_current_file_name(self) -> str:
        """Get the name of the current file."""
        if self.current_file:
            return os.path.basename(self.current_file)
        return "Untitled"

    # FileLoaderProtocol implementation
    def validate_file(self, file_path: str) -> bool:
        """Validate if a file can be loaded."""
        try:
            self._validate_file(file_path)
            return True
        except (FileNotFoundError, PermissionError, ValueError):
            return False

    def get_supported_extensions(self) -> list[str]:
        """Return list of supported file extensions."""
        return list(config.MARKDOWN_EXTENSIONS)
