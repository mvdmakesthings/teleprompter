"""Unit tests for HTML content analyzer."""

import pytest

from src.teleprompter.domain.content.analyzer import HtmlContentAnalyzer


class TestHtmlContentAnalyzer:
    """Test the HtmlContentAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create an HtmlContentAnalyzer instance."""
        return HtmlContentAnalyzer()

    def test_extract_plain_text(self, analyzer):
        """Test extracting plain text from HTML."""
        html = "<h1>Title</h1><p>This is a <strong>test</strong> paragraph.</p>"
        result = analyzer.analyze_html(html)
        assert "text_content" in result
        assert "Title" in result["text_content"]
        assert "test" in result["text_content"]

        # Test with empty HTML
        result = analyzer.analyze_html("")
        assert result["text_content"] == ""

    def test_extract_headings(self, analyzer):
        """Test extracting headings from HTML."""
        html = """
        <h1>Main Title</h1>
        <p>Some text</p>
        <h2>Section 1</h2>
        <p>More text</p>
        <h3>Subsection 1.1</h3>
        <p>Even more text</p>
        <h2>Section 2</h2>
        """

        # Use extract_header_hierarchy which returns list of (level, text, offset)
        headings = analyzer.extract_header_hierarchy(html)

        assert len(headings) == 4
        assert headings[0][0] == 1  # level
        assert headings[0][1] == "Main Title"  # text
        assert headings[1][0] == 2
        assert headings[1][1] == "Section 1"
        assert headings[2][0] == 3
        assert headings[2][1] == "Subsection 1.1"
        assert headings[3][0] == 2
        assert headings[3][1] == "Section 2"

    def test_extract_headings_with_existing_ids(self, analyzer):
        """Test extracting headings that already have IDs."""
        html = """
        <h1 id="custom-id">Title with ID</h1>
        <h2>Title without ID</h2>
        """

        headings = analyzer.extract_header_hierarchy(html)

        assert len(headings) == 2
        assert headings[0][1] == "Title with ID"
        assert headings[1][1] == "Title without ID"

    def test_generate_table_of_contents(self, analyzer):
        """Test generating table of contents."""
        html = """
        <h1>Introduction</h1>
        <h2>Background</h2>
        <h3>History</h3>
        <h3>Context</h3>
        <h2>Methods</h2>
        <h1>Results</h1>
        """

        toc = analyzer.generate_table_of_contents(html)

        # TOC should be HTML string
        assert isinstance(toc, str)
        assert "<ul>" in toc
        assert "Introduction" in toc
        assert "Background" in toc
        assert "History" in toc
        assert "Context" in toc
        assert "Methods" in toc
        assert "Results" in toc

    def test_generate_table_of_contents_max_depth(self, analyzer):
        """Test generating table of contents with max depth."""
        html = """
        <h1>Title</h1>
        <h2>Section</h2>
        <h3>Subsection</h3>
        <h4>Sub-subsection</h4>
        """

        # Generate table of contents
        toc = analyzer.generate_table_of_contents(html)

        # Should contain all heading levels
        assert "Title" in toc
        assert "Section" in toc
        assert "Subsection" in toc
        assert "Sub-subsection" in toc

    def test_count_words(self, analyzer):
        """Test word counting."""
        html = "<p>This is a test paragraph with eight words.</p>"
        assert analyzer.count_words(html) == 8

        html = "<h1>Title</h1><p>Some text here.</p><ul><li>Item one</li><li>Item two</li></ul>"
        assert analyzer.count_words(html) == 8

        # Test with empty content
        assert analyzer.count_words("") == 0
        assert analyzer.count_words("<p></p>") == 0

    def test_find_sections(self, analyzer):
        """Test finding sections by heading."""
        html = """
        <h1 id="intro">Introduction</h1>
        <p>Intro paragraph 1</p>
        <p>Intro paragraph 2</p>
        <h2 id="background">Background</h2>
        <p>Background text</p>
        <h1 id="methods">Methods</h1>
        <p>Methods description</p>
        """

        sections = analyzer.find_sections(html)

        assert len(sections) == 3

        # Check section titles
        assert sections[0] == "Introduction"
        assert sections[1] == "Background"
        assert sections[2] == "Methods"

    def test_estimate_reading_time_per_section(self, analyzer):
        """Test reading time estimation per section."""
        html = """
        <h1>Short Section</h1>
        <p>This section has about ten words in it for testing.</p>
        <h1>Long Section</h1>
        <p>This is a much longer section with many more words. It contains multiple sentences
        and paragraphs to simulate real content. The reading time should be proportionally
        longer than the short section above. Let's add even more text here to make sure
        we have enough words for a meaningful test. This should definitely take longer to
        read than the first section.</p>
        """

        estimates = analyzer.estimate_reading_sections(html, words_per_minute=200)

        assert len(estimates) == 2

        # Check that estimates have the expected structure
        assert all("title" in est for est in estimates)
        assert all("word_count" in est for est in estimates)
        assert all("reading_time_seconds" in est for est in estimates)

        # First section should be "Short Section"
        assert estimates[0]["title"] == "Short Section"

        # Second section should be "Long Section"
        assert estimates[1]["title"] == "Long Section"
        assert estimates[1]["word_count"] > estimates[0]["word_count"]
