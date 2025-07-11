"""Tests for WebSocket functionality."""


import pytest
from fastapi.testclient import TestClient

from teleprompter.backend.api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestWebSocket:
    """Test WebSocket endpoints."""

    def test_websocket_connection(self, client):
        """Test basic WebSocket connection."""
        with client.websocket_connect("/ws") as websocket:
            # Send a ping
            websocket.send_json({"type": "ping"})

            # Should receive a pong
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_websocket_voice_update(self, client):
        """Test voice update through WebSocket."""
        with client.websocket_connect("/ws") as websocket:
            # Send voice update
            websocket.send_json({
                "type": "voice_update",
                "detected": True,
                "level": 0.75
            })

            # Should receive broadcast of voice activity
            data = websocket.receive_json()
            assert data["event"] == "voice_activity"
            assert data["data"]["is_voice_detected"] is True
            assert data["data"]["audio_level"] == 0.75

    def test_websocket_multiple_clients(self, client):
        """Test broadcasting to multiple WebSocket clients."""
        with client.websocket_connect("/ws") as ws1, client.websocket_connect("/ws") as ws2:
                # Send voice update from first client
                ws1.send_json({
                    "type": "voice_update",
                    "detected": False,
                    "level": 0.1
                })

                # Both clients should receive the broadcast
                data1 = ws1.receive_json()
                data2 = ws2.receive_json()

                assert data1 == data2
                assert data1["event"] == "voice_activity"
                assert data1["data"]["is_voice_detected"] is False
                assert data1["data"]["audio_level"] == 0.1

    def test_websocket_disconnect_handling(self, client):
        """Test WebSocket disconnection handling."""
        # Connect and immediately disconnect
        websocket = client.websocket_connect("/ws")
        websocket.__enter__()
        websocket.__exit__(None, None, None)

        # Connection should be closed without errors
        # (This mainly tests that disconnection doesn't crash the server)

    def test_websocket_invalid_message(self, client):
        """Test handling of invalid WebSocket messages."""
        with client.websocket_connect("/ws") as websocket:
            # Send message with unknown type
            websocket.send_json({"type": "unknown"})

            # Should not receive any response for unknown types
            # Send a ping to verify connection is still alive
            websocket.send_json({"type": "ping"})
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_websocket_message_format(self, client):
        """Test WebSocket message format validation."""
        with client.websocket_connect("/ws") as websocket:
            # Send voice update
            websocket.send_json({
                "type": "voice_update",
                "detected": True,
                "level": 0.5
            })

            # Check broadcast message format
            data = websocket.receive_json()
            assert "event" in data
            assert "data" in data
            assert "timestamp" in data
            assert isinstance(data["timestamp"], str)  # ISO format timestamp
