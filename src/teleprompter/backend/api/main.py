"""Main FastAPI application for the teleprompter backend."""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from ...core.container import get_container
from ...core.protocols import (
    ContentParserProtocol,
    FileManagerProtocol,
    HtmlContentAnalyzerProtocol,
    ReadingMetricsProtocol,
    SettingsStorageProtocol,
)
from .models import (
    ContentAnalysisResponse,
    ContentAnalyzeRequest,
    ContentLoadRequest,
    ContentLoadResponse,
    ContentParseRequest,
    ContentParseResponse,
    HealthCheckResponse,
    ReadingControlRequest,
    ReadingControlResponse,
    ReadingMetricsRequest,
    ReadingMetricsResponse,
    SettingsResponse,
    SettingsUpdateRequest,
    SuccessResponse,
    VoiceDetectionRequest,
    VoiceDetectionResponse,
    WebSocketMessage,
)
from .websocket import WebSocketManager

# Version of the API
API_VERSION = "0.1.0"

# WebSocket manager for real-time communication
ws_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Note: Container configuration is done by tests or when needed
    # to avoid importing Qt dependencies during API startup
    yield
    # Cleanup on shutdown
    container = get_container()
    container.clear()


# Create FastAPI app
app = FastAPI(
    title="CueBird Teleprompter API",
    description="Backend API for CueBird teleprompter application",
    version=API_VERSION,
    lifespan=lifespan,
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=API_VERSION,
    )


# Content API Routes
@app.post("/api/content/load", response_model=ContentLoadResponse)
async def load_content(request: ContentLoadRequest) -> ContentLoadResponse:
    """Load content from a file."""
    try:
        container = get_container()
        file_manager = container.get(FileManagerProtocol)

        content = file_manager.load_file(request.file_path)

        # Get file metadata
        import os
        stat = os.stat(request.file_path)

        return ContentLoadResponse(
            content=content,
            file_path=request.file_path,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="File not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/content/parse", response_model=ContentParseResponse)
async def parse_content(request: ContentParseRequest) -> ContentParseResponse:
    """Parse content (e.g., Markdown to HTML)."""
    try:
        container = get_container()
        parser = container.get(ContentParserProtocol)
        analyzer = container.get(HtmlContentAnalyzerProtocol)

        # Parse content
        html = parser.parse(request.content)
        word_count = parser.get_word_count(request.content)
        sections = analyzer.find_sections(html)

        return ContentParseResponse(
            html=html,
            word_count=word_count,
            sections=sections,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/content/analyze", response_model=ContentAnalysisResponse)
async def analyze_content(request: ContentAnalyzeRequest) -> ContentAnalysisResponse:
    """Analyze HTML content."""
    try:
        container = get_container()
        analyzer = container.get(HtmlContentAnalyzerProtocol)

        analysis = analyzer.analyze_html(request.html_content)

        return ContentAnalysisResponse(
            word_count=analysis["word_count"],
            sections=analysis["sections"],
            estimated_reading_time=analysis["estimated_reading_time"],
            total_elements=analysis["total_elements"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Reading API Routes
@app.post("/api/reading/metrics", response_model=ReadingMetricsResponse)
async def get_reading_metrics(request: ReadingMetricsRequest) -> ReadingMetricsResponse:
    """Calculate reading metrics."""
    try:
        container = get_container()
        metrics_service = container.get(ReadingMetricsProtocol)

        # Calculate metrics
        reading_time = metrics_service.calculate_reading_time(request.word_count, request.wpm)
        words_per_minute = metrics_service.calculate_words_per_minute(1.0)  # Base speed

        # For demonstration, use provided position to estimate times
        elapsed = reading_time * request.current_position
        remaining = reading_time * (1.0 - request.current_position)

        return ReadingMetricsResponse(
            reading_time=reading_time,
            words_per_minute=words_per_minute,
            elapsed_time=elapsed,
            remaining_time=remaining,
            progress=request.current_position,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Store reading state (in production, this would be in a proper state manager)
reading_state = {
    "is_playing": False,
    "speed": 1.0,
    "position": 0.0,
    "font_size": 48,
}


@app.post("/api/reading/control", response_model=ReadingControlResponse)
async def control_reading(request: ReadingControlRequest) -> ReadingControlResponse:
    """Control reading state."""
    global reading_state

    try:
        # Handle actions
        if request.action == "start":
            reading_state["is_playing"] = True
        elif request.action == "stop":
            reading_state["is_playing"] = False
            reading_state["position"] = 0.0
        elif request.action == "pause":
            reading_state["is_playing"] = False
        elif request.action == "resume":
            reading_state["is_playing"] = True

        # Update other parameters if provided
        if request.speed is not None:
            reading_state["speed"] = request.speed
        if request.position is not None:
            reading_state["position"] = request.position
        if request.font_size is not None:
            reading_state["font_size"] = request.font_size

        # Broadcast state change via WebSocket
        await ws_manager.broadcast(
            WebSocketMessage(
                event="reading_state_changed",
                data=reading_state,
            )
        )

        return ReadingControlResponse(**reading_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Voice Detection API Routes
voice_state = {
    "is_active": False,
    "is_voice_detected": False,
    "audio_level": 0.0,
    "sensitivity": 2,
    "error": None,
}


@app.post("/api/voice/detect", response_model=VoiceDetectionResponse)
async def control_voice_detection(request: VoiceDetectionRequest) -> VoiceDetectionResponse:
    """Control voice detection."""
    global voice_state

    try:
        if request.action == "start":
            voice_state["is_active"] = True
            voice_state["error"] = None
        elif request.action == "stop":
            voice_state["is_active"] = False
            voice_state["is_voice_detected"] = False
            voice_state["audio_level"] = 0.0

        if request.sensitivity is not None:
            voice_state["sensitivity"] = request.sensitivity

        # Broadcast state change via WebSocket
        await ws_manager.broadcast(
            WebSocketMessage(
                event="voice_state_changed",
                data=voice_state,
            )
        )

        return VoiceDetectionResponse(**voice_state)
    except Exception as e:
        voice_state["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# Settings API Routes
@app.get("/api/settings", response_model=SettingsResponse)
async def get_settings() -> SettingsResponse:
    """Get current settings."""
    try:
        container = get_container()
        settings_storage = container.get(SettingsStorageProtocol)

        # Get all settings
        settings = {}
        # For now, return some default settings
        # In production, iterate through all stored settings
        settings = {
            "scrollSpeed": settings_storage.get("scrollSpeed", 1.0),
            "fontSize": settings_storage.get("fontSize", 48),
            "voiceEnabled": settings_storage.get("voiceEnabled", False),
            "voiceSensitivity": settings_storage.get("voiceSensitivity", 2),
            "theme": settings_storage.get("theme", "dark"),
        }

        return SettingsResponse(settings=settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/settings", response_model=SuccessResponse)
async def update_settings(request: SettingsUpdateRequest) -> SuccessResponse:
    """Update settings."""
    try:
        container = get_container()
        settings_storage = container.get(SettingsStorageProtocol)

        # Update settings
        for key, value in request.settings.items():
            settings_storage.set(key, value)

        # Broadcast settings change via WebSocket
        await ws_manager.broadcast(
            WebSocketMessage(
                event="settings_changed",
                data=request.settings,
            )
        )

        return SuccessResponse(message="Settings updated successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "voice_update":
                # Update voice state
                voice_state["is_voice_detected"] = data.get("detected", False)
                voice_state["audio_level"] = data.get("level", 0.0)

                # Broadcast to all clients
                await ws_manager.broadcast(
                    WebSocketMessage(
                        event="voice_activity",
                        data=voice_state,
                    )
                )
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
