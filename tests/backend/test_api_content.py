"""Tests for content API endpoints."""

import os
import tempfile
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from teleprompter.backend.api.main import app
from teleprompter.core.container import get_container
from teleprompter.core.protocols import (
    ContentParserProtocol,
    FileManagerProtocol,
    HtmlContentAnalyzerProtocol,
)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_container():
    """Mock the dependency injection container."""
    container = get_container()
    container.clear()

    # Mock file manager
    mock_file_manager = Mock(spec=FileManagerProtocol)
    container.register(FileManagerProtocol, mock_file_manager)

    # Mock content parser
    mock_parser = Mock(spec=ContentParserProtocol)
    container.register(ContentParserProtocol, mock_parser)

    # Mock HTML analyzer
    mock_analyzer = Mock(spec=HtmlContentAnalyzerProtocol)
    container.register(HtmlContentAnalyzerProtocol, mock_analyzer)

    yield {
        "file_manager": mock_file_manager,
        "parser": mock_parser,
        "analyzer": mock_analyzer,
    }

    container.clear()


class TestContentAPI:
    """Test content API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "0.1.0"

    def test_load_content_success(self, client, mock_container):
        """Test successful content loading."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("# Test Content\n\nThis is a test.")
            temp_path = f.name

        try:
            # Mock file manager response
            mock_container["file_manager"].load_file.return_value = "# Test Content\n\nThis is a test."

            # Make request
            response = client.post(
                "/api/content/load",
                json={"file_path": temp_path}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "# Test Content\n\nThis is a test."
            assert data["file_path"] == temp_path
            assert data["size"] > 0
            assert "last_modified" in data

            # Verify mock was called
            mock_container["file_manager"].load_file.assert_called_once_with(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_content_file_not_found(self, client, mock_container):
        """Test content loading with non-existent file."""
        mock_container["file_manager"].load_file.side_effect = FileNotFoundError()

        response = client.post(
            "/api/content/load",
            json={"file_path": "/non/existent/file.md"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "File not found"

    def test_parse_content_success(self, client, mock_container):
        """Test successful content parsing."""
        # Mock parser responses
        mock_container["parser"].parse.return_value = "<h1>Test</h1><p>Content</p>"
        mock_container["parser"].get_word_count.return_value = 2
        mock_container["analyzer"].find_sections.return_value = ["Test"]

        response = client.post(
            "/api/content/parse",
            json={"content": "# Test\n\nContent"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["html"] == "<h1>Test</h1><p>Content</p>"
        assert data["word_count"] == 2
        assert data["sections"] == ["Test"]

        # Verify mocks were called
        mock_container["parser"].parse.assert_called_once_with("# Test\n\nContent")
        mock_container["parser"].get_word_count.assert_called_once_with("# Test\n\nContent")
        mock_container["analyzer"].find_sections.assert_called_once_with("<h1>Test</h1><p>Content</p>")

    def test_analyze_content_success(self, client, mock_container):
        """Test successful content analysis."""
        # Mock analyzer response
        mock_container["analyzer"].analyze_html.return_value = {
            "word_count": 100,
            "sections": ["Introduction", "Conclusion"],
            "estimated_reading_time": 0.5,
            "total_elements": 10,
        }

        response = client.post(
            "/api/content/analyze",
            json={"html_content": "<h1>Test</h1><p>Content</p>"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["word_count"] == 100
        assert data["sections"] == ["Introduction", "Conclusion"]
        assert data["estimated_reading_time"] == 0.5
        assert data["total_elements"] == 10

        # Verify mock was called
        mock_container["analyzer"].analyze_html.assert_called_once_with("<h1>Test</h1><p>Content</p>")

    def test_parse_content_with_format(self, client, mock_container):
        """Test content parsing with specified format."""
        mock_container["parser"].parse.return_value = "<p>HTML content</p>"
        mock_container["parser"].get_word_count.return_value = 2
        mock_container["analyzer"].find_sections.return_value = []

        response = client.post(
            "/api/content/parse",
            json={"content": "Plain text", "format": "plain"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["html"] == "<p>HTML content</p>"

    def test_content_error_handling(self, client, mock_container):
        """Test error handling in content endpoints."""
        mock_container["parser"].parse.side_effect = ValueError("Invalid content")

        response = client.post(
            "/api/content/parse",
            json={"content": "Invalid"}
        )

        assert response.status_code == 500
        assert "Invalid content" in response.json()["detail"]
