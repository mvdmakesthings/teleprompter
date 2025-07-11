"""Tests for settings API endpoints."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from teleprompter.backend.api.main import app
from teleprompter.core.container import get_container
from teleprompter.core.protocols import SettingsStorageProtocol


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_settings_storage():
    """Mock the settings storage."""
    container = get_container()
    container.clear()

    mock_storage = Mock(spec=SettingsStorageProtocol)
    container.register(SettingsStorageProtocol, mock_storage)

    yield mock_storage

    container.clear()


class TestSettingsAPI:
    """Test settings API endpoints."""

    def test_get_settings(self, client, mock_settings_storage):
        """Test retrieving settings."""
        # Mock storage responses
        mock_settings_storage.get.side_effect = lambda key, default: {
            "scrollSpeed": 1.5,
            "fontSize": 56,
            "voiceEnabled": True,
            "voiceSensitivity": 3,
            "theme": "light",
        }.get(key, default)

        response = client.get("/api/settings")

        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["scrollSpeed"] == 1.5
        assert data["settings"]["fontSize"] == 56
        assert data["settings"]["voiceEnabled"] is True
        assert data["settings"]["voiceSensitivity"] == 3
        assert data["settings"]["theme"] == "light"

        # Verify storage was queried
        assert mock_settings_storage.get.called
        mock_settings_storage.get.assert_any_call("scrollSpeed", 1.0)
        mock_settings_storage.get.assert_any_call("fontSize", 48)

    def test_update_settings(self, client, mock_settings_storage):
        """Test updating settings."""
        settings_update = {
            "scrollSpeed": 2.0,
            "fontSize": 64,
            "voiceEnabled": False
        }

        response = client.post(
            "/api/settings",
            json={"settings": settings_update}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Settings updated successfully"

        # Verify storage was updated
        mock_settings_storage.set.assert_any_call("scrollSpeed", 2.0)
        mock_settings_storage.set.assert_any_call("fontSize", 64)
        mock_settings_storage.set.assert_any_call("voiceEnabled", False)
        assert mock_settings_storage.set.call_count == 3

    def test_update_single_setting(self, client, mock_settings_storage):
        """Test updating a single setting."""
        response = client.post(
            "/api/settings",
            json={"settings": {"theme": "dark"}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify only one setting was updated
        mock_settings_storage.set.assert_called_once_with("theme", "dark")

    def test_update_settings_merge_behavior(self, client, mock_settings_storage):
        """Test settings merge behavior."""
        # Test with merge=True (default)
        response = client.post(
            "/api/settings",
            json={
                "settings": {"scrollSpeed": 1.25},
                "merge": True
            }
        )

        assert response.status_code == 200
        mock_settings_storage.set.assert_called_with("scrollSpeed", 1.25)

    def test_get_settings_with_defaults(self, client, mock_settings_storage):
        """Test getting settings with default values."""
        # Mock storage to return None for all keys
        mock_settings_storage.get.return_value = None

        response = client.get("/api/settings")

        assert response.status_code == 200
        data = response.json()

        # Should get default values
        assert data["settings"]["scrollSpeed"] is None  # Based on mock behavior

        # Verify default values were requested
        mock_settings_storage.get.assert_any_call("scrollSpeed", 1.0)
        mock_settings_storage.get.assert_any_call("fontSize", 48)

    def test_update_empty_settings(self, client, mock_settings_storage):
        """Test updating with empty settings object."""
        response = client.post(
            "/api/settings",
            json={"settings": {}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # No settings should be updated
        mock_settings_storage.set.assert_not_called()

    def test_settings_error_handling(self, client, mock_settings_storage):
        """Test error handling in settings endpoints."""
        mock_settings_storage.set.side_effect = Exception("Storage error")

        response = client.post(
            "/api/settings",
            json={"settings": {"theme": "dark"}}
        )

        assert response.status_code == 500
        assert "Storage error" in response.json()["detail"]
