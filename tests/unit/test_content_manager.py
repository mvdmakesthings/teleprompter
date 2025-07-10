"""Unit tests for content manager."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from teleprompter.core.exceptions import (
    ContentLoadError,
    InvalidFileFormatError,
)
from teleprompter.core.exceptions import (
    FileNotFoundError as TeleprompterFileNotFoundError,
)
from teleprompter.domain.content import ContentManager


class TestContentManager:
    """Test the ContentManager class."""

    @pytest.fixture
    def manager(self):
        """Create a ContentManager instance."""
        return ContentManager()

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager._current_file is None
        assert manager._original_content == ""
        assert manager._html_content == ""
        assert manager._is_modified is False

    def test_load_file_success(self, manager):
        """Test successful file loading."""
        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Test Content\n\nThis is a test.")
            tmp_path = Path(tmp.name)

        try:
            # Mock the markdown parser
            with patch.object(manager._markdown_parser, "parse") as mock_parse:
                mock_parse.return_value = "<h1>Test Content</h1><p>This is a test.</p>"

                # Load the file
                manager.load_file(tmp_path)

                assert manager._current_file == tmp_path
                assert manager._original_content == "# Test Content\n\nThis is a test."
                assert (
                    manager._html_content
                    == "<h1>Test Content</h1><p>This is a test.</p>"
                )
                assert manager._is_modified is False
                mock_parse.assert_called_once_with("# Test Content\n\nThis is a test.")
        finally:
            tmp_path.unlink()

    def test_load_file_not_found(self, manager):
        """Test loading non-existent file."""
        with pytest.raises(TeleprompterFileNotFoundError) as exc_info:
            manager.load_file(Path("/non/existent/file.md"))
        assert "File not found" in str(exc_info.value)

    def test_load_file_unsupported_format(self, manager):
        """Test loading unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            with pytest.raises(InvalidFileFormatError) as exc_info:
                manager.load_file(Path(tmp.name))
            assert "Unsupported file format" in str(exc_info.value)

    def test_load_file_empty(self, manager):
        """Test loading empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("")
            tmp_path = Path(tmp.name)

        try:
            with pytest.raises(ContentLoadError) as exc_info:
                manager.load_file(tmp_path)
            assert "empty" in str(exc_info.value).lower()
        finally:
            tmp_path.unlink()

    def test_load_file_read_error(self, manager):
        """Test file read error handling."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Remove read permissions
            tmp_path.chmod(0o000)

            with pytest.raises(ContentLoadError) as exc_info:
                manager.load_file(tmp_path)
            assert "Failed to read file" in str(exc_info.value)
        finally:
            # Restore permissions and delete
            tmp_path.chmod(0o644)
            tmp_path.unlink()

    def test_set_content(self, manager):
        """Test setting content directly."""
        # Mock the markdown parser
        with patch.object(manager._markdown_parser, "parse") as mock_parse:
            mock_parse.return_value = "<p>New content</p>"

            manager.set_content("New content")

            assert manager._original_content == "New content"
            assert manager._html_content == "<p>New content</p>"
            assert manager._is_modified is True
            assert manager._current_file is None
            mock_parse.assert_called_once_with("New content")

    def test_get_html_content(self, manager):
        """Test getting HTML content."""
        manager._html_content = "<p>Test</p>"
        assert manager.get_html_content() == "<p>Test</p>"

    def test_get_plain_text(self, manager):
        """Test getting plain text content."""
        manager._original_content = "Test content"
        assert manager.get_plain_text() == "Test content"

    def test_has_content(self, manager):
        """Test checking if content exists."""
        assert manager.has_content() is False

        manager._html_content = "<p>Test</p>"
        assert manager.has_content() is True

    def test_is_modified(self, manager):
        """Test modification status."""
        assert manager.is_modified() is False

        manager._is_modified = True
        assert manager.is_modified() is True

    def test_get_current_file(self, manager):
        """Test getting current file path."""
        assert manager.get_current_file() is None

        manager._current_file = Path("/test/file.md")
        assert manager.get_current_file() == Path("/test/file.md")

    def test_clear(self, manager):
        """Test clearing content."""
        # Set up some content
        manager._current_file = Path("/test/file.md")
        manager._original_content = "Test"
        manager._html_content = "<p>Test</p>"
        manager._is_modified = True

        # Clear
        manager.clear()

        assert manager._current_file is None
        assert manager._original_content == ""
        assert manager._html_content == ""
        assert manager._is_modified is False

    def test_save_current_file(self, manager):
        """Test saving to current file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            manager._current_file = tmp_path
            manager._original_content = "# Updated Content"
            manager._is_modified = True

            manager.save()

            # Verify file was written
            assert tmp_path.read_text() == "# Updated Content"
            assert manager._is_modified is False
        finally:
            tmp_path.unlink()

    def test_save_no_current_file(self, manager):
        """Test saving without current file."""
        manager._original_content = "Content"

        with pytest.raises(ValueError, match="No file path specified"):
            manager.save()

    def test_save_as(self, manager):
        """Test saving to new file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            manager._original_content = "# New Content"
            manager._is_modified = True

            manager.save_as(tmp_path)

            # Verify file was written
            assert tmp_path.read_text() == "# New Content"
            assert manager._current_file == tmp_path
            assert manager._is_modified is False
        finally:
            tmp_path.unlink()

    def test_reload(self, manager):
        """Test reloading current file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Original")
            tmp_path = Path(tmp.name)

        try:
            # Load initial content
            with patch.object(manager._markdown_parser, "parse") as mock_parse:
                mock_parse.return_value = "<h1>Original</h1>"
                manager.load_file(tmp_path)

            # Modify the file externally
            tmp_path.write_text("# Updated")

            # Reload
            with patch.object(manager._markdown_parser, "parse") as mock_parse:
                mock_parse.return_value = "<h1>Updated</h1>"
                manager.reload()

                assert manager._original_content == "# Updated"
                assert manager._html_content == "<h1>Updated</h1>"
                assert manager._is_modified is False
        finally:
            tmp_path.unlink()

    def test_reload_no_current_file(self, manager):
        """Test reloading without current file."""
        with pytest.raises(ValueError, match="No file to reload"):
            manager.reload()

    def test_supported_formats(self, manager):
        """Test supported file formats."""
        formats = manager.get_supported_formats()
        assert ".md" in formats
        assert ".markdown" in formats
        assert ".txt" in formats

    def test_is_supported_file(self, manager):
        """Test checking if file is supported."""
        assert manager.is_supported_file(Path("test.md")) is True
        assert manager.is_supported_file(Path("test.markdown")) is True
        assert manager.is_supported_file(Path("test.txt")) is True
        assert manager.is_supported_file(Path("test.pdf")) is False
        assert manager.is_supported_file(Path("test.MD")) is True  # Case insensitive
