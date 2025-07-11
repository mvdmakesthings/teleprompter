"""Domain models for API serialization."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class VoiceActivityState(str, Enum):
    """Voice activity states."""

    IDLE = "idle"
    LISTENING = "listening"
    SPEAKING = "speaking"
    ERROR = "error"


class VoiceActivity(BaseModel):
    """Voice activity data model."""

    state: VoiceActivityState = Field(description="Current voice activity state")
    is_speaking: bool = Field(description="Whether voice is currently detected")
    audio_level: float = Field(description="Current audio level (0.0-1.0)")
    sensitivity: int = Field(description="Detection sensitivity (0-3)")
    timestamp: datetime = Field(default_factory=datetime.now)


class FileWatchEvent(BaseModel):
    """File watch event data model."""

    event_type: str = Field(description="Type of event: changed, removed, error")
    file_path: str = Field(description="Path to the affected file")
    timestamp: datetime = Field(default_factory=datetime.now)
    error: str | None = Field(None, description="Error message if event_type is error")


class ScrollState(BaseModel):
    """Scroll state data model."""

    position: float = Field(description="Current scroll position (0.0-1.0)")
    speed: float = Field(description="Scroll speed multiplier")
    is_playing: bool = Field(description="Whether scrolling is active")
    timestamp: datetime = Field(default_factory=datetime.now)


class ContentInfo(BaseModel):
    """Content information data model."""

    file_path: str | None = Field(None, description="Path to loaded file")
    word_count: int = Field(description="Total word count")
    sections: list[str] = Field(description="List of section headings")
    html_content: str | None = Field(None, description="Parsed HTML content")
    last_modified: datetime | None = Field(None, description="File modification time")


class ReadingSession(BaseModel):
    """Reading session data model."""

    start_time: datetime | None = Field(None, description="Session start time")
    elapsed_seconds: float = Field(0.0, description="Elapsed reading time")
    words_read: int = Field(0, description="Estimated words read")
    average_wpm: float = Field(0.0, description="Average words per minute")
    is_paused: bool = Field(False, description="Whether session is paused")


class ServiceEvent(BaseModel):
    """Generic service event for WebSocket communication."""

    service: str = Field(description="Service name that generated the event")
    event_type: str = Field(description="Type of event")
    data: dict[str, Any] = Field(description="Event data")
    timestamp: datetime = Field(default_factory=datetime.now)
