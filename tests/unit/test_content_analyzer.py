"""Unit tests for HTML content analyzer."""

import pytest

from teleprompter.domain.content import HtmlContentAnalyzer


class TestHtmlContentAnalyzer:
    """Test the HtmlContentAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create an HtmlContentAnalyzer instance."""
        return HtmlContentAnalyzer()

    def test_extract_plain_text(self, analyzer):
        """Test extracting plain text from HTML."""
        html = "<h1>Title</h1><p>This is a <strong>test</strong> paragraph.</p>"
        text = analyzer.extract_plain_text(html)
        assert text == "Title\nThis is a test paragraph."

        # Test with nested tags
        html = "<div><h2>Header</h2><ul><li>Item 1</li><li>Item 2</li></ul></div>"
        text = analyzer.extract_plain_text(html)
        assert text == "Header\nItem 1\nItem 2"

        # Test with empty HTML
        assert analyzer.extract_plain_text("") == ""
        assert analyzer.extract_plain_text("<p></p>") == ""

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

        headings = analyzer.extract_headings(html)

        assert len(headings) == 4
        assert headings[0] == {"level": 1, "text": "Main Title", "id": "main-title"}
        assert headings[1] == {"level": 2, "text": "Section 1", "id": "section-1"}
        assert headings[2] == {
            "level": 3,
            "text": "Subsection 1.1",
            "id": "subsection-1.1",
        }
        assert headings[3] == {"level": 2, "text": "Section 2", "id": "section-2"}

    def test_extract_headings_with_existing_ids(self, analyzer):
        """Test extracting headings that already have IDs."""
        html = """
        <h1 id="custom-id">Title with ID</h1>
        <h2>Title without ID</h2>
        """

        headings = analyzer.extract_headings(html)

        assert headings[0]["id"] == "custom-id"
        assert headings[1]["id"] == "title-without-id"

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

        expected = [
            {
                "level": 1,
                "text": "Introduction",
                "id": "introduction",
                "children": [
                    {
                        "level": 2,
                        "text": "Background",
                        "id": "background",
                        "children": [
                            {
                                "level": 3,
                                "text": "History",
                                "id": "history",
                                "children": [],
                            },
                            {
                                "level": 3,
                                "text": "Context",
                                "id": "context",
                                "children": [],
                            },
                        ],
                    },
                    {"level": 2, "text": "Methods", "id": "methods", "children": []},
                ],
            },
            {"level": 1, "text": "Results", "id": "results", "children": []},
        ]

        assert toc == expected

    def test_generate_table_of_contents_max_depth(self, analyzer):
        """Test generating table of contents with max depth."""
        html = """
        <h1>Title</h1>
        <h2>Section</h2>
        <h3>Subsection</h3>
        <h4>Sub-subsection</h4>
        """

        # Max depth 2 (h1 and h2)
        toc = analyzer.generate_table_of_contents(html, max_depth=2)

        assert len(toc) == 1
        assert len(toc[0]["children"]) == 1
        assert len(toc[0]["children"][0]["children"]) == 0  # h3 excluded

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

        # Check first section
        assert sections[0]["heading"]["text"] == "Introduction"
        assert sections[0]["heading"]["id"] == "intro"
        assert "Intro paragraph 1" in sections[0]["content"]
        assert "Intro paragraph 2" in sections[0]["content"]
        assert "Background text" not in sections[0]["content"]

        # Check second section
        assert sections[1]["heading"]["text"] == "Background"
        assert sections[1]["heading"]["id"] == "background"
        assert "Background text" in sections[1]["content"]

        # Check third section
        assert sections[2]["heading"]["text"] == "Methods"
        assert sections[2]["heading"]["id"] == "methods"
        assert "Methods description" in sections[2]["content"]

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

        estimates = analyzer.estimate_reading_time_per_section(
            html, words_per_minute=200
        )

        assert len(estimates) == 2

        # First section: ~10 words at 200 wpm = 3 seconds
        assert estimates[0]["section"]["heading"]["text"] == "Short Section"
        assert estimates[0]["word_count"] == 10
        assert estimates[0]["reading_time_seconds"] == 3

        # Second section should have more words and longer reading time
        assert estimates[1]["section"]["heading"]["text"] == "Long Section"
        assert estimates[1]["word_count"] > 40
        assert estimates[1]["reading_time_seconds"] > 12

    def test_add_ids_to_headings(self, analyzer):
        """Test adding IDs to headings in HTML."""
        html = """
        <h1>First Title</h1>
        <h2>Subsection</h2>
        <h1 id="existing">Already Has ID</h1>
        <h2>Another Section</h2>
        """

        result = analyzer.add_ids_to_headings(html)

        # Check that IDs were added
        assert 'id="first-title"' in result
        assert 'id="subsection"' in result
        assert 'id="existing"' in result  # Should preserve existing ID
        assert 'id="another-section"' in result

    def test_slugify(self, analyzer):
        """Test text slugification."""
        assert analyzer._slugify("Hello World") == "hello-world"
        assert analyzer._slugify("Test 123") == "test-123"
        assert analyzer._slugify("Special!@#$%^&*()Characters") == "special-characters"
        assert analyzer._slugify("Multiple   Spaces") == "multiple-spaces"
        assert analyzer._slugify("  Leading and Trailing  ") == "leading-and-trailing"
