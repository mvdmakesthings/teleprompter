"""API response models for the teleprompter backend."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str = Field(description="Service health status")
    timestamp: datetime = Field(description="Current server timestamp")
    version: str = Field(description="API version")


class ContentLoadResponse(BaseModel):
    """Response for content loading."""

    content: str = Field(description="Raw content of the loaded file")
    file_path: str = Field(description="Path to the loaded file")
    size: int = Field(description="File size in bytes")
    last_modified: datetime = Field(description="Last modification timestamp")


class ContentParseResponse(BaseModel):
    """Response for content parsing."""

    html: str = Field(description="Parsed HTML content")
    word_count: int = Field(description="Total word count")
    sections: list[str] = Field(description="List of section headings")


class ContentAnalysisResponse(BaseModel):
    """Response for content analysis."""

    word_count: int = Field(description="Total word count")
    sections: list[str] = Field(description="List of section headings")
    estimated_reading_time: float = Field(description="Estimated reading time in minutes")
    total_elements: int = Field(description="Total number of HTML elements")


class ReadingMetricsResponse(BaseModel):
    """Response for reading metrics."""

    reading_time: float = Field(description="Estimated reading time in seconds")
    words_per_minute: float = Field(description="Current reading speed in WPM")
    elapsed_time: float = Field(description="Elapsed reading time in seconds")
    remaining_time: float = Field(description="Remaining reading time in seconds")
    progress: float = Field(description="Reading progress (0.0 to 1.0)")


class ReadingControlResponse(BaseModel):
    """Response for reading control state."""

    is_playing: bool = Field(description="Whether scrolling is active")
    speed: float = Field(description="Current scroll speed multiplier")
    position: float = Field(description="Current scroll position (0.0 to 1.0)")
    font_size: int = Field(description="Current font size in pixels")


class VoiceDetectionResponse(BaseModel):
    """Response for voice detection state."""

    is_active: bool = Field(description="Whether voice detection is running")
    is_voice_detected: bool = Field(description="Whether voice is currently detected")
    audio_level: float = Field(description="Current audio level (0.0 to 1.0)")
    sensitivity: int = Field(description="Current sensitivity level (0-3)")
    error: str | None = Field(None, description="Error message if any")


class SettingsResponse(BaseModel):
    """Response for settings retrieval."""

    settings: dict[str, Any] = Field(description="Current application settings")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
    code: str | None = Field(None, description="Error code")


class SuccessResponse(BaseModel):
    """Generic success response."""

    success: bool = Field(default=True, description="Operation success status")
    message: str | None = Field(None, description="Optional success message")


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    event: str = Field(description="Event type")
    data: dict[str, Any] = Field(description="Event data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
