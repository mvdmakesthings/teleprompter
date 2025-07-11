"""Tests for voice detection API endpoints."""

import pytest
from fastapi.testclient import TestClient

from teleprompter.backend.api.main import app, voice_state


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_voice_state():
    """Reset voice state before each test."""
    global voice_state
    voice_state.update({
        "is_active": False,
        "is_voice_detected": False,
        "audio_level": 0.0,
        "sensitivity": 2,
        "error": None,
    })
    yield


class TestVoiceAPI:
    """Test voice detection API endpoints."""

    def test_start_voice_detection(self, client):
        """Test starting voice detection."""
        response = client.post(
            "/api/voice/detect",
            json={"action": "start"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert data["error"] is None
        assert voice_state["is_active"] is True

    def test_stop_voice_detection(self, client):
        """Test stopping voice detection."""
        # Start first
        voice_state["is_active"] = True
        voice_state["is_voice_detected"] = True
        voice_state["audio_level"] = 0.5

        response = client.post(
            "/api/voice/detect",
            json={"action": "stop"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["is_voice_detected"] is False
        assert data["audio_level"] == 0.0
        assert voice_state["is_active"] is False

    def test_update_voice_sensitivity(self, client):
        """Test updating voice detection sensitivity."""
        response = client.post(
            "/api/voice/detect",
            json={
                "action": "start",
                "sensitivity": 3
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sensitivity"] == 3
        assert voice_state["sensitivity"] == 3

    def test_voice_detection_state_persistence(self, client):
        """Test that voice state persists between requests."""
        # Start detection with specific sensitivity
        response1 = client.post(
            "/api/voice/detect",
            json={
                "action": "start",
                "sensitivity": 1
            }
        )
        assert response1.status_code == 200

        # Update only action, sensitivity should persist
        response2 = client.post(
            "/api/voice/detect",
            json={"action": "stop"}
        )
        assert response2.status_code == 200
        data = response2.json()
        assert data["sensitivity"] == 1

    def test_voice_detection_sensitivity_range(self, client):
        """Test voice detection sensitivity values."""
        for sensitivity in [0, 1, 2, 3]:
            response = client.post(
                "/api/voice/detect",
                json={
                    "action": "start",
                    "sensitivity": sensitivity
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["sensitivity"] == sensitivity

    def test_voice_detection_invalid_action(self, client):
        """Test voice detection with invalid action."""
        # Note: Currently the API doesn't validate actions,
        # but this test documents expected behavior
        response = client.post(
            "/api/voice/detect",
            json={"action": "invalid"}
        )
        # Should still return 200 but not change state
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    def test_voice_detection_response_format(self, client):
        """Test voice detection response format."""
        response = client.post(
            "/api/voice/detect",
            json={"action": "start"}
        )

        assert response.status_code == 200
        data = response.json()

        # Check all expected fields are present
        assert "is_active" in data
        assert "is_voice_detected" in data
        assert "audio_level" in data
        assert "sensitivity" in data
        assert "error" in data

        # Check types
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["is_voice_detected"], bool)
        assert isinstance(data["audio_level"], int | float)
        assert isinstance(data["sensitivity"], int)
        assert data["error"] is None or isinstance(data["error"], str)
