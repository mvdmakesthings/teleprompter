"""Unit tests for content manager."""

from unittest.mock import Mock

import pytest

from src.teleprompter.domain.content.manager import ContentManager


class TestContentManager:
    """Test the ContentManager class."""

    @pytest.fixture
    def mock_parser(self):
        """Create a mock parser."""
        parser = Mock()
        parser.parse.return_value = "<p>Default HTML</p>"
        parser.get_word_count.return_value = 0
        return parser

    @pytest.fixture
    def manager(self, mock_parser):
        """Create a ContentManager instance."""
        return ContentManager(mock_parser)

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager._current_content == ""
        assert manager._parsed_content == ""
        assert manager._word_count == 0
        assert manager._sections == []

    def test_load_content(self, manager, mock_parser):
        """Test loading content."""
        # Setup mock parser
        mock_parser.parse.return_value = "<h1>Test Content</h1><p>This is a test.</p>"
        mock_parser.get_word_count.return_value = 4

        # Load content
        content = "# Test Content\n\nThis is a test."
        manager.load_content(content)

        # Verify state
        assert manager._current_content == content
        assert manager._parsed_content == "<h1>Test Content</h1><p>This is a test.</p>"
        assert manager._word_count == 4
        assert manager._sections == [(0, "Test Content")]

        # Verify parser was called
        mock_parser.parse.assert_called_once_with(content)
        mock_parser.get_word_count.assert_called_once_with(content)

    def test_get_parsed_content(self, manager):
        """Test getting parsed HTML content."""
        manager._parsed_content = "<p>Test HTML</p>"
        assert manager.get_parsed_content() == "<p>Test HTML</p>"

    def test_get_word_count(self, manager):
        """Test getting word count."""
        manager._word_count = 42
        assert manager.get_word_count() == 42

    def test_get_sections(self, manager):
        """Test getting sections."""
        manager._sections = [(0, "Section 1"), (10, "Section 2")]
        sections = manager.get_sections()
        assert sections == [(0, "Section 1"), (10, "Section 2")]
        # Ensure it returns a copy
        sections.append((20, "Section 3"))
        assert len(manager._sections) == 2

    def test_extract_sections(self, manager):
        """Test section extraction from markdown."""
        content = """# Main Title
Some text here.

## Section 1
More text.

### Subsection 1.1
Detailed text.

## Section 2
Final text."""

        manager._current_content = content
        manager._extract_sections()

        assert len(manager._sections) == 4
        assert manager._sections[0] == (0, "Main Title")
        assert manager._sections[1] == (3, "Section 1")
        assert manager._sections[2] == (6, "Subsection 1.1")
        assert manager._sections[3] == (9, "Section 2")

    def test_find_section_at_progress(self, manager):
        """Test finding section at reading progress."""
        # Setup sections
        manager._sections = [(0, "Intro"), (10, "Chapter 1"), (20, "Chapter 2")]
        manager._current_content = "\n" * 30  # 30 lines

        # Test various progress points
        assert manager.find_section_at_progress(0.0) == 0  # Start
        assert manager.find_section_at_progress(0.4) == 1  # Line 12, after Chapter 1
        assert manager.find_section_at_progress(0.8) == 2  # Line 24, after Chapter 2
        assert manager.find_section_at_progress(1.0) == 2  # End

        # Test with no sections
        manager._sections = []
        assert manager.find_section_at_progress(0.5) is None

    def test_get_section_progress(self, manager):
        """Test getting progress for a section."""
        manager._sections = [(0, "Intro"), (10, "Chapter 1"), (20, "Chapter 2")]
        manager._current_content = "\n" * 30  # 30 lines

        assert manager.get_section_progress(0) == 0.0  # Line 0 / 30
        # Line 10 / 31 lines (30 newlines = 31 lines)
        assert abs(manager.get_section_progress(1) - (10 / 31)) < 0.01
        assert abs(manager.get_section_progress(2) - (20 / 31)) < 0.01

        # Test invalid indices
        assert manager.get_section_progress(-1) == 0.0
        assert manager.get_section_progress(3) == 0.0

        # Test with no sections
        manager._sections = []
        assert manager.get_section_progress(0) == 0.0

    def test_get_section_info(self, manager, mock_parser):
        """Test getting detailed section information."""
        # Setup
        content = "# Section 1\nWord one two.\n\n# Section 2\nWord three four five."
        manager._current_content = content
        manager._sections = [(0, "Section 1"), (3, "Section 2")]

        # Mock parser to return different word counts
        mock_parser.get_word_count.side_effect = [3, 3]  # 3 words per section

        # Test first section
        info = manager.get_section_info(0)
        assert info["index"] == 0
        assert info["title"] == "Section 1"
        assert info["line_number"] == 0
        assert info["word_count"] == 3
        assert info["progress"] == 0.0

        # Test second section
        info = manager.get_section_info(1)
        assert info["index"] == 1
        assert info["title"] == "Section 2"
        assert info["line_number"] == 3
        assert info["word_count"] == 3
        assert info["progress"] == 0.6  # 3/5 lines

        # Test invalid index
        assert manager.get_section_info(-1) is None
        assert manager.get_section_info(2) is None

    def test_get_content_summary(self, manager):
        """Test getting content summary."""
        manager._word_count = 150
        manager._sections = [(0, "Intro"), (10, "Chapter 1")]
        manager._current_content = "Some content"

        summary = manager.get_content_summary()

        assert summary["total_words"] == 150
        assert summary["total_sections"] == 2
        assert summary["has_content"] is True
        assert summary["content_length"] == 12
        assert len(summary["sections"]) == 2
        assert summary["sections"][0] == {"index": 0, "title": "Intro", "line": 0}
        assert summary["sections"][1] == {"index": 1, "title": "Chapter 1", "line": 10}

    def test_empty_content(self, manager):
        """Test behavior with empty content."""
        # Initial state should be empty
        assert manager.get_word_count() == 0
        assert manager.get_sections() == []
        assert manager.get_parsed_content() == ""

        summary = manager.get_content_summary()
        assert summary["has_content"] is False
        assert summary["total_words"] == 0
        assert summary["total_sections"] == 0
