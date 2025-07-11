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
    UIError,
    UnsupportedFileTypeError,
    VoiceDetectionError,
    VoiceError,
    WidgetInitializationError,
)
from .protocols import (
    AnimatedWidgetProtocol,
    ContentParserProtocol,
    FileLoaderProtocol,
    IconProviderProtocol,
    ManagerProtocol,
    ReadingMetricsProtocol,
    ResponsiveLayoutProtocol,
    ScrollControllerProtocol,
    SettingsStorageProtocol,
    StyleProviderProtocol,
    ToolbarFactoryProtocol,
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
    "UIError",
    "WidgetInitializationError",
    "ServiceError",
    "ServiceNotFoundError",
    "ServiceInitializationError",
    "ErrorRecovery",
    # Protocols
    "FileLoaderProtocol",
    "ContentParserProtocol",
    "StyleProviderProtocol",
    "SettingsStorageProtocol",
    "VoiceDetectorProtocol",
    "ScrollControllerProtocol",
    "ReadingMetricsProtocol",
    "ToolbarFactoryProtocol",
    "IconProviderProtocol",
    "ManagerProtocol",
    "AnimatedWidgetProtocol",
    "ResponsiveLayoutProtocol",
]
