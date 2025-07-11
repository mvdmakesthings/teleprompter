"""Pydantic models for API requests and responses."""

from .domain import (
    ContentInfo,
    FileWatchEvent,
    ReadingSession,
    ScrollState,
    ServiceEvent,
    VoiceActivity,
    VoiceActivityState,
)
from .requests import (
    ContentAnalyzeRequest,
    ContentLoadRequest,
    ContentParseRequest,
    FileWatchRequest,
    ReadingControlRequest,
    ReadingMetricsRequest,
    SettingsUpdateRequest,
    VoiceDetectionRequest,
)
from .responses import (
    ContentAnalysisResponse,
    ContentLoadResponse,
    ContentParseResponse,
    ErrorResponse,
    HealthCheckResponse,
    ReadingControlResponse,
    ReadingMetricsResponse,
    SettingsResponse,
    SuccessResponse,
    VoiceDetectionResponse,
    WebSocketMessage,
)

__all__ = [
    # Domain models
    "ContentInfo",
    "FileWatchEvent",
    "ReadingSession",
    "ScrollState",
    "ServiceEvent",
    "VoiceActivity",
    "VoiceActivityState",
    # Requests
    "ContentAnalyzeRequest",
    "ContentLoadRequest",
    "ContentParseRequest",
    "FileWatchRequest",
    "ReadingControlRequest",
    "ReadingMetricsRequest",
    "SettingsUpdateRequest",
    "VoiceDetectionRequest",
    # Responses
    "ContentAnalysisResponse",
    "ContentLoadResponse",
    "ContentParseResponse",
    "ErrorResponse",
    "HealthCheckResponse",
    "ReadingControlResponse",
    "ReadingMetricsResponse",
    "SettingsResponse",
    "SuccessResponse",
    "VoiceDetectionResponse",
    "WebSocketMessage",
]
