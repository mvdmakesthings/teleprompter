"""Logging infrastructure for the teleprompter application.

This module provides a structured logging setup using structlog, with environment-based
configuration for development and production environments.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

import structlog
from PyQt6.QtCore import QtMsgType, qInstallMessageHandler


def setup_logging(
    *,
    level: str | None = None,
    format_type: str | None = None,
    log_file: str | None = None,
    enable_rich: bool = True,
) -> None:
    """Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format ('console', 'json', 'auto')
        log_file: Optional file path for file logging
        enable_rich: Whether to use rich formatting in console output

    Note:
        If not specified, configuration is determined from environment variables:
        - TELEPROMPTER_LOG_LEVEL: Log level
        - TELEPROMPTER_LOG_FORMAT: Format type
        - TELEPROMPTER_LOG_FILE: Log file path
    """
    # Get configuration from environment or defaults
    log_level = level or os.getenv("TELEPROMPTER_LOG_LEVEL", "INFO").upper()
    log_format = format_type or os.getenv("TELEPROMPTER_LOG_FORMAT", "auto")
    log_file_path = log_file or os.getenv("TELEPROMPTER_LOG_FILE")

    # Determine if we're in a terminal for auto format selection
    is_terminal = (
        sys.stderr.isatty() if log_format == "auto" else log_format == "console"
    )

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=numeric_level,
    )

    # Shared processors for all configurations
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Choose final processors based on output format
    if is_terminal and enable_rich:
        # Pretty console output for development
        try:
            # Try to use rich for beautiful console output
            final_processors = [
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        except ImportError:
            # Fallback to standard console renderer
            final_processors = [
                structlog.dev.ConsoleRenderer(colors=False),
            ]
    else:
        # JSON output for production/logging systems
        final_processors = [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    # Configure structlog
    structlog.configure(
        processors=shared_processors + final_processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set up file logging if specified
    if log_file_path:
        _setup_file_logging(log_file_path, numeric_level, shared_processors)

    # Configure third-party logging
    _configure_third_party_logging()

    # Install Qt message handler
    _install_qt_handler()


def _setup_file_logging(file_path: str, level: int, shared_processors: list) -> None:
    """Set up file-based logging with JSON format.

    Args:
        file_path: Path to the log file
        level: Numeric log level
        shared_processors: Shared processor configuration
    """
    # Ensure parent directory exists
    log_file = Path(file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create file handler with JSON formatting
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(level)

    # Use ProcessorFormatter for file output with JSON
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        foreign_pre_chain=shared_processors,
    )

    file_handler.setFormatter(file_formatter)

    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


def _configure_third_party_logging() -> None:
    """Configure logging for third-party libraries.

    Reduces noise from verbose third-party libraries while maintaining
    important error information.
    """
    # Reduce verbose logging from common libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    # PyQt can be very verbose
    logging.getLogger("PyQt6").setLevel(logging.WARNING)
    logging.getLogger("qt").setLevel(logging.WARNING)


def _install_qt_handler() -> None:
    """Install custom Qt message handler to integrate with Python logging."""

    def qt_message_handler(msg_type: QtMsgType, context, message: str) -> None:
        """Handle Qt messages and route to Python logging."""
        logger = get_logger("teleprompter.qt")

        # Map Qt message types to logging levels
        if msg_type == QtMsgType.QtDebugMsg:
            logger.debug("Qt message", message=message)
        elif msg_type == QtMsgType.QtInfoMsg:
            logger.info("Qt message", message=message)
        elif msg_type == QtMsgType.QtWarningMsg:
            logger.warning("Qt message", message=message)
        elif msg_type == QtMsgType.QtCriticalMsg:
            logger.error("Qt message", message=message)
        elif msg_type == QtMsgType.QtFatalMsg:
            logger.critical("Qt message", message=message)

    qInstallMessageHandler(qt_message_handler)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Optional logger name (defaults to calling module)

    Returns:
        Configured bound logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started", version="1.0.0")
        >>> logger.error("Failed to process", error_code=500, user_id=123)
    """
    return structlog.get_logger(name)


class TeleprompterLogger:
    """Custom logger configuration for the teleprompter application."""

    # Logger names for different components
    MAIN = "teleprompter.main"
    UI = "teleprompter.ui"
    CORE = "teleprompter.core"
    DOMAIN = "teleprompter.domain"
    INFRA = "teleprompter.infrastructure"

    # Default log format
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

    @classmethod
    def setup_logging(
        cls,
        level: int = logging.INFO,
        log_file: Path | None = None,
        detailed: bool = False,
    ) -> None:
        """Configure logging for the entire application.

        Args:
            level: Logging level (default: INFO)
            log_file: Optional file path for log output
            detailed: Whether to use detailed format with file/line info
        """
        # Choose format based on detail level
        log_format = cls.DETAILED_FORMAT if detailed else cls.DEFAULT_FORMAT

        # Configure root logger
        root_logger = logging.getLogger("teleprompter")
        root_logger.setLevel(level)

        # Remove existing handlers
        root_logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(log_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            # Ensure parent directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                cls.DETAILED_FORMAT
            )  # Always detailed in file
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

        # Install Qt message handler
        cls._install_qt_handler()

        root_logger.info("Logging configured successfully")

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance for a specific component.

        Args:
            name: Logger name (e.g., 'teleprompter.ui.widgets')

        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)

    @classmethod
    def _install_qt_handler(cls) -> None:
        """Install custom Qt message handler to integrate with Python logging."""

        def qt_message_handler(msg_type: QtMsgType, context, message: str) -> None:
            """Handle Qt messages and route to Python logging."""
            logger = cls.get_logger("teleprompter.qt")

            # Map Qt message types to logging levels
            if msg_type == QtMsgType.QtDebugMsg:
                logger.debug(f"Qt: {message}")
            elif msg_type == QtMsgType.QtInfoMsg:
                logger.info(f"Qt: {message}")
            elif msg_type == QtMsgType.QtWarningMsg:
                logger.warning(f"Qt: {message}")
            elif msg_type == QtMsgType.QtCriticalMsg:
                logger.error(f"Qt: {message}")
            elif msg_type == QtMsgType.QtFatalMsg:
                logger.critical(f"Qt: {message}")

        qInstallMessageHandler(qt_message_handler)


class LoggerMixin:
    """Mixin class to provide logging functionality to other classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            # Use full module and class name
            logger_name = f"{self.__module__}.{self.__class__.__name__}"
            self._logger = logging.getLogger(logger_name)
        return self._logger

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with optional context."""
        self.logger.debug(message, extra=kwargs)

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message with optional context."""
        self.logger.info(message, extra=kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with optional context."""
        self.logger.warning(message, extra=kwargs)

    def log_error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """Log error message with optional exception info."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def log_exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)


class PerformanceLogger:
    """Performance monitoring and logging utilities."""

    def __init__(self, logger: structlog.stdlib.BoundLogger | None = None):
        """Initialize performance logger.

        Args:
            logger: Optional logger instance (creates one if not provided)
        """
        self.logger = logger or get_logger("performance")
        self._timers: dict[str, float] = {}

    def timer(self, operation: str) -> "TimerContext":
        """Create a timing context manager.

        Args:
            operation: Name of the operation being timed

        Returns:
            Timer context manager

        Example:
            >>> perf = PerformanceLogger()
            >>> with perf.timer("file_loading"):
            ...     load_large_file()
        """
        return TimerContext(self.logger, operation)

    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        import time

        self._timers[operation] = time.perf_counter()
        self.logger.debug("Timer started", operation=operation)

    def end_timer(self, operation: str) -> float:
        """End timing and log the duration.

        Args:
            operation: Name of the operation

        Returns:
            Duration in seconds
        """
        import time

        if operation not in self._timers:
            self.logger.warning("No timer found", operation=operation)
            return 0.0

        duration = time.perf_counter() - self._timers[operation]
        del self._timers[operation]

        self.logger.info(
            "Operation completed",
            operation=operation,
            duration_seconds=duration,
            duration_ms=duration * 1000,
        )
        return duration

    def log_memory_usage(self, operation: str, **context: Any) -> None:
        """Log current memory usage.

        Args:
            operation: Description of the operation
            **context: Additional context to include
        """
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()

            self.logger.info(
                "Memory usage",
                operation=operation,
                rss_mb=memory_info.rss / 1024 / 1024,
                vms_mb=memory_info.vms / 1024 / 1024,
                percent=process.memory_percent(),
                **context,
            )
        except ImportError:
            self.logger.warning(
                "Memory logging unavailable",
                operation=operation,
                reason="psutil not installed",
                **context,
            )

    def log_timing(self, operation: str, duration_ms: float, **context: Any) -> None:
        """Log timing information.

        Args:
            operation: Name of the timed operation
            duration_ms: Duration in milliseconds
            **context: Additional context to include
        """
        self.logger.info(
            "Operation timing",
            operation=operation,
            duration_ms=duration_ms,
            duration_seconds=duration_ms / 1000,
            **context,
        )


class TimerContext:
    """Context manager for timing operations."""

    def __init__(self, logger: structlog.stdlib.BoundLogger, operation: str):
        """Initialize timer context.

        Args:
            logger: Logger instance to use
            operation: Name of the operation being timed
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self) -> "TimerContext":
        """Start timing."""
        import time

        self.start_time = time.perf_counter()
        self.logger.debug("Operation started", operation=self.operation)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop timing and log result."""
        import time

        if self.start_time is not None:
            duration = (time.perf_counter() - self.start_time) * 1000

            if exc_type is not None:
                self.logger.error(
                    "Operation failed",
                    operation=self.operation,
                    duration_ms=duration,
                    exception=str(exc_val) if exc_val else None,
                )
            else:
                self.logger.info(
                    "Operation completed",
                    operation=self.operation,
                    duration_ms=duration,
                )


# Convenience function for quick setup
def quick_setup(
    level: str = "INFO", console: bool = True, file_path: str | None = None
) -> structlog.stdlib.BoundLogger:
    """Quick logging setup for simple use cases.

    Args:
        level: Log level string
        console: Whether to enable console output
        file_path: Optional file path for logging

    Returns:
        Configured logger instance

    Example:
        >>> logger = quick_setup("DEBUG", console=True, file_path="app.log")
        >>> logger.info("Application ready")
    """
    setup_logging(
        level=level,
        format_type="console" if console else "json",
        log_file=file_path,
    )
    return get_logger("app")


# Legacy compatibility functions
def get_logger_legacy(name: str) -> logging.Logger:
    """Get a legacy logger instance."""
    return TeleprompterLogger.get_logger(name)


def setup_logging_legacy(**kwargs) -> None:
    """Set up legacy application logging."""
    TeleprompterLogger.setup_logging(**kwargs)


# Decorators for logging
def log_method_calls(logger: logging.Logger | None = None):
    """Decorator to log method entry and exit.

    Args:
        logger: Optional logger instance (uses method's class logger if None)
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Use provided logger or class logger
            log = logger or getattr(self, "logger", logging.getLogger(func.__module__))

            # Log method entry
            log.debug(f"Entering {func.__name__}")

            try:
                result = func(self, *args, **kwargs)
                log.debug(f"Exiting {func.__name__} successfully")
                return result
            except Exception as e:
                log.error(f"Error in {func.__name__}: {e}", exc_info=True)
                raise

        return wrapper

    return decorator


def log_performance(operation_name: str | None = None):
    """Decorator to log method performance.

    Args:
        operation_name: Optional custom name for the operation
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Use provided name or function name
            op_name = operation_name or func.__name__

            # Get logger
            logger = getattr(self, "logger", logging.getLogger(func.__module__))
            perf_logger = PerformanceLogger(logger)

            # Time the operation
            perf_logger.start_timer(op_name)
            try:
                result = func(self, *args, **kwargs)
                return result
            finally:
                perf_logger.end_timer(op_name)

        return wrapper

    return decorator
