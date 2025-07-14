"""Core functionality for the teleprompter application."""

from .container import (
    Injectable,
    ServiceContainer,
    configure_container,
    get_container,
    inject,
)
from .exceptions import (
    AudioDeviceError,
    ConfigurationError,
    ContentError,
    ContentParseError,
    ErrorRecovery,
    FileError,
    FileLoadError,
    FileNotFoundError,
    InvalidConfigurationError,
    MissingConfigurationError,
    ServiceError,
    ServiceInitializationError,
    ServiceNotFoundError,
    TeleprompterError,
    UnsupportedFileTypeError,
    VoiceDetectionError,
    VoiceError,
)
from .json_settings import JsonSettingsStorage
from .protocols import (
    ContentParserProtocol,
    FileLoaderProtocol,
    FileManagerProtocol,
    FileWatcherProtocol,
    HtmlContentAnalyzerProtocol,
    ManagerProtocol,
    ReadingMetricsProtocol,
    ScrollControllerProtocol,
    SettingsStorageProtocol,
    VoiceDetectorProtocol,
)

__all__ = [
    # Container
    "ServiceContainer",
    "get_container",
    "configure_container",
    "inject",
    "Injectable",
    # Exceptions
    "TeleprompterError",
    "FileError",
    "FileNotFoundError",
    "UnsupportedFileTypeError",
    "FileLoadError",
    "ContentError",
    "ContentParseError",
    "VoiceError",
    "AudioDeviceError",
    "VoiceDetectionError",
    "ConfigurationError",
    "InvalidConfigurationError",
    "MissingConfigurationError",
    "ServiceError",
    "ServiceNotFoundError",
    "ServiceInitializationError",
    "ErrorRecovery",
    # Settings Implementation
    "JsonSettingsStorage",
    # Protocols
    "FileLoaderProtocol",
    "FileManagerProtocol",
    "ContentParserProtocol",
    "HtmlContentAnalyzerProtocol",
    "SettingsStorageProtocol",
    "VoiceDetectorProtocol",
    "ScrollControllerProtocol",
    "ReadingMetricsProtocol",
    "FileWatcherProtocol",
    "ManagerProtocol",
]
