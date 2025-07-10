"""Unit tests for markdown parser."""

import pytest

from teleprompter.domain.content import MarkdownParser


class TestMarkdownParser:
    """Test the MarkdownParser class."""

    @pytest.fixture
    def parser(self):
        """Create a MarkdownParser instance."""
        return MarkdownParser()

    def test_parse_basic_markdown(self, parser):
        """Test parsing basic markdown elements."""
        markdown = """# Heading 1
## Heading 2
### Heading 3

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2
- List item 3
"""
        html = parser.parse(markdown)

        # Should be wrapped in HTML document
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "<head>" in html
        assert "<body>" in html

        # Check headings
        assert "<h1>Heading 1</h1>" in html
        assert "<h2>Heading 2</h2>" in html
        assert "<h3>Heading 3</h3>" in html

        # Check formatting
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html

        # Check list
        assert "<ul>" in html
        assert "<li>List item 1</li>" in html
        assert "<li>List item 2</li>" in html
        assert "<li>List item 3</li>" in html

    def test_parse_empty_content(self, parser):
        """Test parsing empty content."""
        # Even empty content should return full HTML document
        html = parser.parse("")
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "<body>" in html

    def test_parse_code_blocks(self, parser):
        """Test parsing code blocks."""
        markdown = """```python
def hello_world():
    print("Hello, World!")
```

And inline `code` too.
"""
        html = parser.parse(markdown)

        # Check code block exists
        assert "<pre>" in html
        assert "def hello_world():" in html
        # HTML entities might be escaped
        assert "Hello, World!" in html

        # Check inline code
        assert "<code>code</code>" in html

    def test_parse_links(self, parser):
        """Test parsing links."""
        markdown = "[Click here](https://example.com) for more info."
        html = parser.parse(markdown)

        assert '<a href="https://example.com">Click here</a>' in html

    def test_parse_images(self, parser):
        """Test parsing images."""
        markdown = "![Alt text](image.png)"
        html = parser.parse(markdown)

        assert '<img' in html
        assert 'image.png' in html
        assert 'Alt text' in html

    def test_parse_blockquotes(self, parser):
        """Test parsing blockquotes."""
        markdown = "> This is a quote\n> with multiple lines"
        html = parser.parse(markdown)

        assert "<blockquote>" in html
        assert "This is a quote" in html
        assert "with multiple lines" in html

    def test_parse_tables(self, parser):
        """Test parsing tables."""
        markdown = """| Header 1 | Header 2 |
| -------- | -------- |
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        html = parser.parse(markdown)

        assert "<table>" in html
        # Tables extension may use thead/tbody
        assert "Header 1" in html
        assert "Header 2" in html
        assert "Cell 1" in html
        assert "Cell 2" in html

    def test_parse_horizontal_rules(self, parser):
        """Test parsing horizontal rules."""
        markdown = "Text above\n\n---\n\nText below"
        html = parser.parse(markdown)

        # HR might be <hr> or <hr />
        assert "<hr" in html
        assert "Text above" in html
        assert "Text below" in html

    def test_parse_nested_lists(self, parser):
        """Test parsing nested lists."""
        markdown = """- Item 1
  - Nested item 1
  - Nested item 2
- Item 2
"""
        html = parser.parse(markdown)

        # Check list items exist
        assert "Item 1" in html
        assert "Nested item 1" in html
        assert "Item 2" in html

    def test_parse_mixed_lists(self, parser):
        """Test parsing mixed ordered and unordered lists."""
        markdown = """1. First item
2. Second item
3. Third item
"""
        html = parser.parse(markdown)

        assert "<ol>" in html
        assert "First item" in html
        assert "Second item" in html
        assert "Third item" in html

    def test_parse_escaping(self, parser):
        """Test parsing escaped characters."""
        markdown = r"This has \*escaped\* asterisks"
        html = parser.parse(markdown)

        # Should not be interpreted as markdown
        assert "<em>escaped</em>" not in html

    def test_parse_html_in_markdown(self, parser):
        """Test handling HTML in markdown."""
        markdown = """This has <span style="color: red;">inline HTML</span> in it."""
        html = parser.parse(markdown)

        # HTML should be preserved
        assert '<span style="color: red;">inline HTML</span>' in html

    def test_parse_multiline_paragraphs(self, parser):
        """Test parsing multiline paragraphs."""
        markdown = """This is a long paragraph that
spans multiple lines but should
be rendered as a single paragraph.

This is a separate paragraph."""

        html = parser.parse(markdown)

        # Should have two <p> tags
        assert html.count("<p>") == 2
        assert "spans multiple lines" in html
        assert "separate paragraph" in html

    def test_parse_special_characters(self, parser):
        """Test parsing special characters."""
        markdown = "This has & ampersands, < less than, > greater than"
        html = parser.parse(markdown)

        # Should be properly escaped
        assert "&amp;" in html
        assert "&lt;" in html
        assert "&gt;" in html

    def test_parse_line_breaks(self, parser):
        """Test parsing line breaks."""
        markdown = "Line one  \nLine two"  # Two spaces before newline
        html = parser.parse(markdown)

        # nl2br extension should add breaks
        assert "Line one" in html
        assert "Line two" in html

    def test_extensions_enabled(self, parser):
        """Test that markdown extensions are working."""
        # Test tables extension
        markdown_table = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = parser.parse(markdown_table)
        assert "<table>" in html

        # Test fenced code blocks
        markdown_code = "```\ncode block\n```"
        html = parser.parse(markdown_code)
        assert "<pre>" in html
        assert "code block" in html

    def test_get_word_count(self, parser):
        """Test word counting functionality."""
        # Simple text
        assert parser.get_word_count("Hello world") == 2
        assert parser.get_word_count("This is a test") == 4

        # Markdown with formatting
        markdown = "# Title\n\nThis is **bold** and *italic* text."
        # The actual implementation may count differently
        count = parser.get_word_count(markdown)
        assert count == 7  # "Title This is bold and italic text"

        # Links and images
        markdown = "Check [this link](https://example.com) and ![image](img.png)"
        assert parser.get_word_count(markdown) == 5  # "Check this link and" (image alt text is empty)

        # Code blocks should be excluded
        markdown = "Text before\n```\ncode block content\n```\nText after"
        assert parser.get_word_count(markdown) == 4  # "Text before Text after"
