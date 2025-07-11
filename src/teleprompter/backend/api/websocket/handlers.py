"""WebSocket connection and message handlers."""


from fastapi import WebSocket

from ..models import WebSocketMessage


class WebSocketManager:
    """Manager for WebSocket connections."""

    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: WebSocketMessage, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        await websocket.send_json(message.model_dump())

    async def broadcast(self, message: WebSocketMessage):
        """Broadcast a message to all connected clients."""
        # Remove disconnected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message.model_dump())
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
