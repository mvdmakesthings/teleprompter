"""Core backend components without Qt dependencies."""

from .protocols import (
    AnimatedWidgetProtocol,
    ContentParserProtocol,
    FileLoaderProtocol,
    FileManagerProtocol,
    FileWatcherProtocol,
    HtmlContentAnalyzerProtocol,
    IconProviderProtocol,
    ManagerProtocol,
    ReadingMetricsProtocol,
    ResponsiveLayoutProtocol,
    ScrollControllerProtocol,
    SettingsStorageProtocol,
    StyleProviderProtocol,
    VoiceDetectorProtocol,
)

__all__ = [
    "AnimatedWidgetProtocol",
    "ContentParserProtocol",
    "FileLoaderProtocol",
    "FileManagerProtocol",
    "FileWatcherProtocol",
    "HtmlContentAnalyzerProtocol",
    "IconProviderProtocol",
    "ManagerProtocol",
    "ReadingMetricsProtocol",
    "ResponsiveLayoutProtocol",
    "ScrollControllerProtocol",
    "SettingsStorageProtocol",
    "StyleProviderProtocol",
    "VoiceDetectorProtocol",
]
