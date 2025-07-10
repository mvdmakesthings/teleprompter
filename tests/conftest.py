"""Shared pytest fixtures and configuration."""

from unittest.mock import Mock

import pytest
from PyQt6.QtWidgets import QApplication

from teleprompter.container import ServiceContainer
from teleprompter.protocols import (
    ContentParserProtocol,
    FileLoaderProtocol,
    SettingsStorageProtocol,
    StyleProviderProtocol,
)


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def container():
    """Create a test service container with mocked services."""
    container = ServiceContainer()

    # Create mocks for all protocols
    mock_file_loader = Mock(spec=FileLoaderProtocol)
    mock_content_parser = Mock(spec=ContentParserProtocol)
    mock_settings = Mock(spec=SettingsStorageProtocol)
    mock_style_provider = Mock(spec=StyleProviderProtocol)

    # Configure default mock behaviors
    mock_file_loader.get_supported_extensions.return_value = [".md", ".txt"]
    mock_content_parser.parse.return_value = "<p>Test content</p>"
    mock_content_parser.get_word_count.return_value = 100
    mock_settings.get.return_value = None
    mock_style_provider.get_stylesheet.return_value = ""

    # Register mocks
    container.register(FileLoaderProtocol, lambda: mock_file_loader)
    container.register(ContentParserProtocol, lambda: mock_content_parser)
    container.register(SettingsStorageProtocol, lambda: mock_settings)
    container.register(StyleProviderProtocol, lambda: mock_style_provider)

    return container


@pytest.fixture
def mock_content():
    """Provide sample markdown content for testing."""
    return """# Test Document

This is a test paragraph with some content.

## Section 1
More content here.

## Section 2
Final content."""


@pytest.fixture
def mock_html_content():
    """Provide sample HTML content for testing."""
    return """<h1>Test Document</h1>
<p>This is a test paragraph with some content.</p>
<h2>Section 1</h2>
<p>More content here.</p>
<h2>Section 2</h2>
<p>Final content.</p>"""
