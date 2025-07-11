"""API request models for the teleprompter backend."""

from typing import Any

from pydantic import BaseModel, Field


class ContentLoadRequest(BaseModel):
    """Request for loading content from a file."""

    file_path: str = Field(description="Path to the file to load")


class ContentParseRequest(BaseModel):
    """Request for parsing content."""

    content: str = Field(description="Raw content to parse (e.g., Markdown)")
    format: str = Field(default="markdown", description="Content format")


class ContentAnalyzeRequest(BaseModel):
    """Request for analyzing HTML content."""

    html_content: str = Field(description="HTML content to analyze")


class ReadingMetricsRequest(BaseModel):
    """Request for calculating reading metrics."""

    word_count: int = Field(description="Total word count")
    wpm: float = Field(default=180.0, description="Reading speed in words per minute")
    current_position: float = Field(default=0.0, description="Current reading position (0.0 to 1.0)")


class ReadingControlRequest(BaseModel):
    """Request for updating reading control state."""

    action: str = Field(description="Control action: start, stop, pause, resume")
    speed: float | None = Field(None, description="New scroll speed multiplier")
    position: float | None = Field(None, description="Jump to position (0.0 to 1.0)")
    font_size: int | None = Field(None, description="New font size in pixels")


class VoiceDetectionRequest(BaseModel):
    """Request for controlling voice detection."""

    action: str = Field(description="Action: start, stop")
    sensitivity: int | None = Field(None, description="Sensitivity level (0-3)")


class SettingsUpdateRequest(BaseModel):
    """Request for updating settings."""

    settings: dict[str, Any] = Field(description="Settings to update")
    merge: bool = Field(default=True, description="Whether to merge with existing settings")


class FileWatchRequest(BaseModel):
    """Request for file watching."""

    file_path: str = Field(description="Path to the file to watch")
    enabled: bool = Field(default=True, description="Whether to enable watching")
