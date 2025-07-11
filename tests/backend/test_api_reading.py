"""Tests for reading API endpoints."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from teleprompter.backend.api.main import app, reading_state
from teleprompter.core.container import get_container
from teleprompter.core.protocols import ReadingMetricsProtocol


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_metrics_service():
    """Mock the reading metrics service."""
    container = get_container()
    container.clear()

    mock_service = Mock(spec=ReadingMetricsProtocol)
    container.register(ReadingMetricsProtocol, mock_service)

    yield mock_service

    container.clear()


class TestReadingAPI:
    """Test reading API endpoints."""

    def test_get_reading_metrics(self, client, mock_metrics_service):
        """Test reading metrics calculation."""
        # Mock service responses
        mock_metrics_service.calculate_reading_time.return_value = 300.0  # 5 minutes
        mock_metrics_service.calculate_words_per_minute.return_value = 180.0

        response = client.post(
            "/api/reading/metrics",
            json={
                "word_count": 900,
                "wpm": 180.0,
                "current_position": 0.5
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reading_time"] == 300.0
        assert data["words_per_minute"] == 180.0
        assert data["elapsed_time"] == 150.0  # 50% of 300
        assert data["remaining_time"] == 150.0
        assert data["progress"] == 0.5

        # Verify mock was called
        mock_metrics_service.calculate_reading_time.assert_called_once_with(900, 180.0)
        mock_metrics_service.calculate_words_per_minute.assert_called_once_with(1.0)

    def test_control_reading_start(self, client):
        """Test starting reading."""
        response = client.post(
            "/api/reading/control",
            json={"action": "start"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_playing"] is True
        assert reading_state["is_playing"] is True

    def test_control_reading_stop(self, client):
        """Test stopping reading."""
        # Start first
        reading_state["is_playing"] = True
        reading_state["position"] = 0.5

        response = client.post(
            "/api/reading/control",
            json={"action": "stop"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_playing"] is False
        assert data["position"] == 0.0
        assert reading_state["is_playing"] is False
        assert reading_state["position"] == 0.0

    def test_control_reading_pause(self, client):
        """Test pausing reading."""
        reading_state["is_playing"] = True

        response = client.post(
            "/api/reading/control",
            json={"action": "pause"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_playing"] is False

    def test_control_reading_resume(self, client):
        """Test resuming reading."""
        reading_state["is_playing"] = False

        response = client.post(
            "/api/reading/control",
            json={"action": "resume"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_playing"] is True

    def test_control_reading_update_speed(self, client):
        """Test updating reading speed."""
        response = client.post(
            "/api/reading/control",
            json={
                "action": "pause",
                "speed": 2.5
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["speed"] == 2.5
        assert reading_state["speed"] == 2.5

    def test_control_reading_update_position(self, client):
        """Test updating reading position."""
        response = client.post(
            "/api/reading/control",
            json={
                "action": "pause",
                "position": 0.75
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["position"] == 0.75
        assert reading_state["position"] == 0.75

    def test_control_reading_update_font_size(self, client):
        """Test updating font size."""
        response = client.post(
            "/api/reading/control",
            json={
                "action": "pause",
                "font_size": 64
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["font_size"] == 64
        assert reading_state["font_size"] == 64

    def test_control_reading_multiple_updates(self, client):
        """Test updating multiple parameters at once."""
        response = client.post(
            "/api/reading/control",
            json={
                "action": "start",
                "speed": 1.5,
                "position": 0.25,
                "font_size": 56
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_playing"] is True
        assert data["speed"] == 1.5
        assert data["position"] == 0.25
        assert data["font_size"] == 56

    def test_metrics_with_zero_words(self, client, mock_metrics_service):
        """Test metrics calculation with zero words."""
        mock_metrics_service.calculate_reading_time.return_value = 0.0
        mock_metrics_service.calculate_words_per_minute.return_value = 180.0

        response = client.post(
            "/api/reading/metrics",
            json={
                "word_count": 0,
                "wpm": 180.0
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reading_time"] == 0.0
        assert data["elapsed_time"] == 0.0
        assert data["remaining_time"] == 0.0
