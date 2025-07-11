"""Content management for handling text and markdown operations."""

from teleprompter.core.protocols import ContentParserProtocol
from teleprompter.utils.logging import LoggerMixin


class ContentManager(LoggerMixin):
    """Manager for handling text and markdown content operations.

    This class manages content loading, parsing, and section extraction
    for the teleprompter application.
    """

    def __init__(self, parser: ContentParserProtocol):
        """Initialize content manager with a parser.

        Args:
            parser: Content parser implementation
        """
        self._parser = parser
        self._current_content: str = ""
        self._parsed_content: str = ""
        self._word_count: int = 0
        self._sections: list[tuple[int, str]] = []  # (line_number, header_text)

    def load_content(self, content: str) -> None:
        """Load and process new content.

        Args:
            content: Raw content to load (typically Markdown)
        """
        self._current_content = content
        self._parsed_content = self._parser.parse(content)
        self._word_count = self._parser.get_word_count(content)
        self._extract_sections()

        self.log_info(
            f"Content loaded: {self._word_count} words, {len(self._sections)} sections"
        )

    def get_parsed_content(self) -> str:
        """Get the parsed HTML content.

        Returns:
            HTML representation of the content
        """
        return self._parsed_content

    def get_word_count(self) -> int:
        """Get total word count of the content.

        Returns:
            Number of words in the content
        """
        return self._word_count

    def get_sections(self) -> list[tuple[int, str]]:
        """Get list of sections found in the content.

        Returns:
            List of tuples containing (line_number, header_text)
        """
        return self._sections.copy()

    def _extract_sections(self) -> None:
        """Extract section headers from markdown content."""
        self._sections.clear()
        lines = self._current_content.split("\n")

        for i, line in enumerate(lines):
            # Check for markdown headers
            stripped = line.strip()
            if stripped.startswith("#"):
                # Extract header level and text
                header_match = stripped.split(" ", 1)
                if len(header_match) == 2:
                    level = len(header_match[0])  # Count # symbols
                    header_text = header_match[1].strip()
                    if header_text:
                        self._sections.append((i, header_text))
                        self.log_debug(
                            f"Found section at line {i}: Level {level} - {header_text}"
                        )

    def find_section_at_progress(self, progress: float) -> int | None:
        """Find section index at given reading progress.

        Args:
            progress: Reading progress (0.0-1.0)

        Returns:
            Index of the section at the given progress, or None if no sections
        """
        if not self._sections:
            return None

        total_lines = len(self._current_content.split("\n"))
        current_line = int(progress * total_lines)

        # Find the last section before current line
        for i in range(len(self._sections) - 1, -1, -1):
            if self._sections[i][0] <= current_line:
                return i

        return 0

    def get_section_progress(self, section_index: int) -> float:
        """Get progress value for a specific section.

        Args:
            section_index: Index of the section

        Returns:
            Progress value (0.0-1.0) representing the section's position
        """
        if (
            not self._sections
            or section_index < 0
            or section_index >= len(self._sections)
        ):
            return 0.0

        total_lines = len(self._current_content.split("\n"))
        section_line = self._sections[section_index][0]

        return section_line / total_lines if total_lines > 0 else 0.0

    def get_section_info(self, section_index: int) -> dict | None:
        """Get detailed information about a section.

        Args:
            section_index: Index of the section

        Returns:
            Dictionary with section details or None if invalid index
        """
        if (
            not self._sections
            or section_index < 0
            or section_index >= len(self._sections)
        ):
            return None

        line_number, header_text = self._sections[section_index]

        # Calculate word count for this section
        lines = self._current_content.split("\n")

        # Find end line (next section or end of content)
        end_line = len(lines)
        if section_index + 1 < len(self._sections):
            end_line = self._sections[section_index + 1][0]

        # Extract section content
        section_lines = lines[line_number:end_line]
        section_content = "\n".join(section_lines)
        section_word_count = self._parser.get_word_count(section_content)

        return {
            "index": section_index,
            "title": header_text,
            "line_number": line_number,
            "word_count": section_word_count,
            "progress": self.get_section_progress(section_index),
        }

    def get_content_summary(self) -> dict:
        """Get a summary of the loaded content.

        Returns:
            Dictionary containing content statistics
        """
        return {
            "total_words": self._word_count,
            "total_sections": len(self._sections),
            "sections": [
                {"index": i, "title": title, "line": line}
                for i, (line, title) in enumerate(self._sections)
            ],
            "has_content": bool(self._current_content),
            "content_length": len(self._current_content),
        }
