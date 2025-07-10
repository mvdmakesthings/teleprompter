"""HTML content analyzer for extracting information from parsed content."""

import re

from teleprompter.infrastructure.logging import LoggerMixin


class HtmlContentAnalyzer(LoggerMixin):
    """Analyzer for extracting information from HTML content.

    This class provides methods to analyze HTML content, extract text,
    find sections, and generate navigation scripts.
    """

    def analyze_html(self, html_content: str) -> dict:
        """Analyze HTML content for word count and sections.

        Args:
            html_content: HTML string to analyze

        Returns:
            Dictionary containing analysis results:
                - total_words: Total word count
                - sections: List of section titles
                - text_content: Plain text extracted from HTML
        """
        # Extract text content from HTML
        text_content = self._extract_text(html_content)

        # Count words
        word_count = len(text_content.split()) if text_content else 0

        # Find sections (headers)
        sections = self._extract_sections(html_content)

        self.log_debug(
            f"HTML analysis complete: {word_count} words, {len(sections)} sections"
        )

        return {
            "total_words": word_count,
            "sections": sections,
            "text_content": text_content,
        }

    def _extract_text(self, html_content: str) -> str:
        """Extract plain text from HTML content.

        Args:
            html_content: HTML string

        Returns:
            Plain text with HTML tags removed
        """
        # Remove script and style elements
        html_clean = re.sub(
            r"<(script|style)[^>]*>.*?</\1>",
            "",
            html_content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove HTML tags
        text_content = re.sub(r"<[^>]+>", " ", html_clean)

        # Clean up whitespace
        text_content = re.sub(r"\s+", " ", text_content).strip()

        return text_content

    def _extract_sections(self, html_content: str) -> list[str]:
        """Extract section headers from HTML content.

        Args:
            html_content: HTML string

        Returns:
            List of section titles
        """
        # Find all header tags (h1-h6)
        header_pattern = r"<h[1-6][^>]*>(.*?)</h[1-6]>"
        headers = re.findall(header_pattern, html_content, re.IGNORECASE)

        # Clean up header text
        sections = []
        for header in headers:
            # Remove any nested HTML tags
            clean_header = re.sub(r"<[^>]+>", "", header).strip()
            if clean_header:
                sections.append(clean_header)

        return sections

    def count_words(self, html_content: str) -> int:
        """Count words in HTML content.

        Args:
            html_content: HTML content to analyze

        Returns:
            Number of words in the content
        """
        stats = self.analyze_html(html_content)
        return stats.get("word_count", 0)

    def find_sections(self, html_content: str) -> list[str]:
        """Find sections/headings in HTML content.

        Args:
            html_content: HTML content to analyze

        Returns:
            List of section titles found in the content
        """
        return self._extract_sections(html_content)

    def find_section_in_html(self, html_content: str, section_title: str) -> str:
        """Generate JavaScript to find and scroll to a section.

        Args:
            html_content: HTML content (unused, kept for compatibility)
            section_title: Title of the section to find

        Returns:
            JavaScript code that finds and scrolls to the section
        """
        # Escape quotes in section title for JavaScript
        escaped_title = section_title.replace("'", "\\'").replace('"', '\\"')

        return f"""(function() {{
            var elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            var targetElement = null;

            for (var i = 0; i < elements.length; i++) {{
                var textContent = elements[i].textContent || elements[i].innerText;
                if (textContent.trim() === "{escaped_title}") {{
                    targetElement = elements[i];
                    break;
                }}
            }}

            if (targetElement) {{
                var rect = targetElement.getBoundingClientRect();
                var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                var targetPosition = rect.top + scrollTop - 50; // 50px offset from top
                window.scrollTo(0, Math.max(0, targetPosition));
                return targetPosition;
            }} else {{
                return -1; // Section not found
            }}
        }})();"""

    def extract_header_hierarchy(self, html_content: str) -> list[tuple[int, str, int]]:
        """Extract headers with their hierarchy levels.

        Args:
            html_content: HTML string

        Returns:
            List of tuples (level, title, position) where:
                - level: Header level (1-6)
                - title: Header text
                - position: Character position in HTML
        """
        headers = []

        # Find all header tags with their level
        header_pattern = r"<h([1-6])[^>]*>(.*?)</h\1>"

        for match in re.finditer(header_pattern, html_content, re.IGNORECASE):
            level = int(match.group(1))
            content = match.group(2)
            position = match.start()

            # Clean the header text
            clean_text = re.sub(r"<[^>]+>", "", content).strip()

            if clean_text:
                headers.append((level, clean_text, position))

        return headers

    def generate_table_of_contents(self, html_content: str) -> str:
        """Generate an HTML table of contents from the content.

        Args:
            html_content: HTML string

        Returns:
            HTML string containing the table of contents
        """
        headers = self.extract_header_hierarchy(html_content)

        if not headers:
            return "<p>No sections found</p>"

        toc_html = ["<nav class='table-of-contents'><ul>"]
        current_level = 0

        for level, title, _ in headers:
            # Adjust nesting
            if level > current_level:
                for _ in range(level - current_level):
                    toc_html.append("<ul>")
            elif level < current_level:
                for _ in range(current_level - level):
                    toc_html.append("</ul>")

            current_level = level

            # Create safe anchor ID
            anchor_id = re.sub(r"[^\w\s-]", "", title.lower())
            anchor_id = re.sub(r"[-\s]+", "-", anchor_id)

            toc_html.append(f"<li><a href='#{anchor_id}'>{title}</a></li>")

        # Close remaining lists
        for _ in range(current_level):
            toc_html.append("</ul>")

        toc_html.append("</nav>")

        return "\n".join(toc_html)

    def estimate_reading_sections(
        self, html_content: str, words_per_minute: float = 150
    ) -> list[dict]:
        """Estimate reading time for each section.

        Args:
            html_content: HTML string
            words_per_minute: Reading speed

        Returns:
            List of dictionaries with section reading estimates
        """
        headers = self.extract_header_hierarchy(html_content)
        if not headers:
            return []

        sections = []
        # text_content = self._extract_text(html_content)  # Unused variable

        for i, (level, title, pos) in enumerate(headers):
            # Find content between this header and the next
            start_pos = pos
            end_pos = headers[i + 1][2] if i + 1 < len(headers) else len(html_content)

            # Extract section HTML
            section_html = html_content[start_pos:end_pos]
            section_text = self._extract_text(section_html)

            # Calculate metrics
            word_count = len(section_text.split())
            reading_time = (word_count / words_per_minute) * 60  # seconds

            sections.append(
                {
                    "level": level,
                    "title": title,
                    "word_count": word_count,
                    "reading_time_seconds": reading_time,
                    "reading_time_formatted": self._format_time(reading_time),
                }
            )

        return sections

    def _format_time(self, seconds: float) -> str:
        """Format seconds into readable time string.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        else:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
