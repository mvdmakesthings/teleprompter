"""Integration tests for service layer."""

import tempfile
import time
from pathlib import Path

import pytest

from teleprompter.container import configure_container
from teleprompter.core.protocols import (
    ContentParserProtocol,
    FileLoaderProtocol,
    HtmlContentAnalyzerProtocol,
    ReadingMetricsProtocol,
    ScrollControllerProtocol,
)
from teleprompter.core.services import (
    ContentManager,
)


@pytest.fixture
def container():
    """Configure and provide the DI container."""
    return configure_container()


@pytest.fixture
def sample_files():
    """Create sample files for testing."""
    files = {}

    # Simple markdown file
    simple_content = """# Simple Document

This is a simple test document.

## Section 1
Some content here.

## Section 2
More content here.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(simple_content)
        files['simple'] = f.name

    # Complex markdown file
    complex_content = """# Complex Document

## Table of Contents
- [Introduction](#introduction)
- [Main Content](#main-content)
- [Conclusion](#conclusion)

## Introduction

This is a **complex** document with various *markdown* features.

### Code Example
```python
def hello_world():
    print("Hello, World!")
```

## Main Content

1. First item
2. Second item
3. Third item

> This is a blockquote
> with multiple lines

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

## Conclusion

[Link to somewhere](https://example.com)

![Image description](image.png)
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(complex_content)
        files['complex'] = f.name

    yield files

    # Cleanup
    for file_path in files.values():
        Path(file_path).unlink(missing_ok=True)


class TestServiceIntegration:
    """Test integration between services."""

    def test_file_loading_and_parsing(self, container, sample_files):
        """Test file loading and parsing integration."""
        file_manager = container.get(FileLoaderProtocol)
        parser = container.get(ContentParserProtocol)

        # Load and parse simple file
        content = file_manager.load_file(sample_files['simple'])
        assert content is not None

        html = parser.parse(content)
        assert "<h1>" in html
        assert "<h2>" in html
        assert "Simple Document" in html

    def test_content_analysis_integration(self, container, sample_files):
        """Test content analysis with real content."""
        file_manager = container.get(FileLoaderProtocol)
        parser = container.get(ContentParserProtocol)
        analyzer = container.get(HtmlContentAnalyzerProtocol)

        # Load, parse, and analyze complex file
        content = file_manager.load_file(sample_files['complex'])
        html = parser.parse(content)

        # Analyze content
        word_count = analyzer.count_words(html)
        assert word_count > 50  # Complex document has many words

        sections = analyzer.find_sections(html)
        assert len(sections) >= 3  # Should find main sections
        assert "Introduction" in sections
        assert "Main Content" in sections
        assert "Conclusion" in sections

        # Full analysis
        analysis = analyzer.analyze_html(html)
        assert analysis['total_words'] == word_count
        assert analysis['sections'] == sections
        assert 'reading_time' in analysis

    def test_reading_metrics_integration(self, container):
        """Test reading metrics calculations."""
        metrics = container.get(ReadingMetricsProtocol)

        # Set up test data
        word_count = 300
        metrics.set_word_count(word_count)

        # Test WPM calculation
        wpm = metrics.calculate_words_per_minute(1.0)
        assert wpm == 200  # Default WPM

        wpm_fast = metrics.calculate_words_per_minute(2.0)
        assert wpm_fast == 400  # 2x speed

        # Test reading time calculation
        reading_time = metrics.calculate_reading_time(word_count, wpm)
        assert reading_time == 90  # 300 words at 200 WPM = 1.5 minutes = 90 seconds

        # Test progress tracking
        metrics.start_reading()
        time.sleep(0.1)

        metrics.set_progress(0.5)  # 50% complete
        elapsed = metrics.get_elapsed_time()
        assert elapsed > 0

        remaining = metrics.get_remaining_time()
        assert remaining > 0

        # Test average WPM
        avg_wpm = metrics.get_average_wpm()
        assert avg_wpm > 0

    def test_scroll_controller_integration(self, container):
        """Test scroll controller functionality."""
        controller = container.get(ScrollControllerProtocol)

        # Set up viewport
        controller.set_viewport_dimensions(800, 2000)  # 800px viewport, 2000px content

        # Test scrolling
        controller.start_scrolling()
        assert controller.is_scrolling()

        # Set speed
        controller.set_speed(2.0)
        assert controller.get_speed() == 2.0

        # Calculate next position
        delta_time = 0.016  # ~60 FPS
        next_pos = controller.calculate_next_position(delta_time)
        assert next_pos > 0

        # Update position
        controller.update_scroll_position(next_pos)

        # Get progress
        progress = controller.get_progress()
        assert 0 <= progress <= 1

        # Pause and stop
        controller.pause_scrolling()
        assert not controller.is_scrolling()

        controller.stop_scrolling()
        assert controller._scroll_position == 0

    def test_content_manager_integration(self, container):
        """Test content manager with all services."""
        parser = container.get(ContentParserProtocol)
        content_manager = ContentManager(parser)

        # Load markdown content
        markdown = """# Test Document

This is a test with **bold** and *italic* text.

## Features
- Item 1
- Item 2
- Item 3
"""

        content_manager.load_markdown(markdown)

        # Get HTML
        html = content_manager.get_html()
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html
        assert "<ul>" in html

        # Get plain text
        plain_text = content_manager.get_plain_text()
        assert "Test Document" in plain_text
        assert "bold" in plain_text
        assert "italic" in plain_text

        # Check state
        assert content_manager.has_content()

        # Clear content
        content_manager.clear()
        assert not content_manager.has_content()


class TestServiceChaining:
    """Test chaining multiple services together."""

    def test_complete_content_pipeline(self, container, sample_files):
        """Test complete content processing pipeline."""
        # Get all services
        file_loader = container.get(FileLoaderProtocol)
        parser = container.get(ContentParserProtocol)
        analyzer = container.get(HtmlContentAnalyzerProtocol)
        metrics = container.get(ReadingMetricsProtocol)
        scroll_controller = container.get(ScrollControllerProtocol)

        # Step 1: Load file
        content = file_loader.load_file(sample_files['complex'])
        assert content

        # Step 2: Parse to HTML
        html = parser.parse(content)
        assert html

        # Step 3: Analyze content
        analysis = analyzer.analyze_html(html)
        word_count = analysis['total_words']
        sections = analysis['sections']

        # Step 4: Set up metrics
        metrics.set_word_count(word_count)
        wpm = metrics.calculate_words_per_minute(1.0)
        reading_time = metrics.calculate_reading_time(word_count, wpm)

        # Step 5: Configure scrolling
        # Assume 50 pixels per line, 30 lines visible
        content_height = word_count * 10  # Rough estimate
        viewport_height = 800

        scroll_controller.set_viewport_dimensions(viewport_height, content_height)
        scroll_controller.set_speed(1.0)

        # Verify everything is connected
        assert word_count > 0
        assert len(sections) > 0
        assert reading_time > 0
        assert scroll_controller.get_speed() == 1.0

    def test_real_time_reading_simulation(self, container):
        """Simulate real-time reading with all services."""
        metrics = container.get(ReadingMetricsProtocol)
        scroll_controller = container.get(ScrollControllerProtocol)

        # Set up content
        word_count = 600  # 3 minutes at 200 WPM
        metrics.set_word_count(word_count)

        # Set up scrolling
        content_height = 3000
        viewport_height = 600
        scroll_controller.set_viewport_dimensions(viewport_height, content_height)

        # Start reading
        metrics.start_reading()
        scroll_controller.start_scrolling()

        # Simulate reading for a short time
        positions = []
        for _i in range(10):  # 10 frames
            time.sleep(0.016)  # ~60 FPS

            # Update scroll position
            delta_time = 0.016
            next_pos = scroll_controller.calculate_next_position(delta_time)
            scroll_controller.update_scroll_position(next_pos)

            # Update progress
            progress = scroll_controller.get_progress()
            metrics.set_progress(progress)

            positions.append(next_pos)

        # Stop reading
        scroll_controller.pause_scrolling()
        metrics.pause_reading()

        # Verify simulation
        assert len(positions) == 10
        assert all(positions[i] < positions[i+1] for i in range(9))  # Monotonic increase
        assert metrics.get_elapsed_time() > 0
        assert metrics.get_remaining_time() > 0


class TestServiceErrorHandling:
    """Test error handling in services."""

    def test_file_loader_error_handling(self, container):
        """Test file loader with invalid files."""
        file_loader = container.get(FileLoaderProtocol)

        # Non-existent file
        with pytest.raises((FileNotFoundError, ValueError)):
            file_loader.load_file("/path/to/nonexistent/file.md")

        # Invalid file type
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            exe_path = f.name

        try:
            is_valid = file_loader.validate_file(exe_path)
            assert not is_valid
        finally:
            Path(exe_path).unlink(missing_ok=True)

    def test_parser_error_handling(self, container):
        """Test parser with invalid content."""
        parser = container.get(ContentParserProtocol)

        # Empty content
        html = parser.parse("")
        assert html  # Should return valid HTML even for empty content

        # Invalid markdown
        html = parser.parse("```\nUnclosed code block")
        assert html  # Should handle gracefully

        # Very large content
        large_content = "x" * 1000000  # 1MB of text
        html = parser.parse(large_content)
        assert len(html) > len(large_content)  # Should add HTML tags

    def test_metrics_boundary_conditions(self, container):
        """Test metrics with boundary conditions."""
        metrics = container.get(ReadingMetricsProtocol)

        # Zero words
        metrics.set_word_count(0)
        reading_time = metrics.calculate_reading_time(0, 200)
        assert reading_time == 0

        # Very high speed
        wpm = metrics.calculate_words_per_minute(10.0)
        assert wpm == 2000  # 10x speed

        # Progress boundaries
        metrics.set_progress(-0.1)  # Should clamp to 0
        assert metrics.get_progress() == 0

        metrics.set_progress(1.5)  # Should clamp to 1
        assert metrics.get_progress() == 1


@pytest.mark.parametrize("file_size", [100, 1000, 10000])
def test_performance_with_different_file_sizes(container, file_size):
    """Test service performance with different file sizes."""
    parser = container.get(ContentParserProtocol)
    analyzer = container.get(HtmlContentAnalyzerProtocol)

    # Generate content of specified size (words)
    content = " ".join(["word"] * file_size)

    # Measure parsing time
    start_time = time.time()
    html = parser.parse(content)
    parse_time = time.time() - start_time

    # Measure analysis time
    start_time = time.time()
    analysis = analyzer.analyze_html(html)
    analyze_time = time.time() - start_time

    # Performance should scale reasonably
    assert parse_time < file_size / 1000  # Less than 1ms per word
    assert analyze_time < file_size / 1000
    assert analysis['total_words'] >= file_size * 0.9  # Allow some variance
