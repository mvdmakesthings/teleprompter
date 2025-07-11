"""Logging infrastructure for the teleprompter application without Qt dependencies.

This module provides a structured logging setup using structlog, with environment-based
configuration for development and production environments.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

import structlog


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
        - CUEBIRD_LOG_LEVEL: Log level
        - CUEBIRD_LOG_FORMAT: Format type
        - CUEBIRD_LOG_FILE: Log file path
    """
    # Get configuration from environment or defaults
    log_level = level or os.getenv("CUEBIRD_LOG_LEVEL", "INFO").upper()
    log_format = format_type or os.getenv("CUEBIRD_LOG_FORMAT", "auto")
    log_file_path = log_file or os.getenv("CUEBIRD_LOG_FILE")

    # Determine if we're in a terminal for auto format selection
    is_terminal = (
        sys.stderr.isatty() if log_format == "auto" else log_format == "console"
    )

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Configure standard logging first
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=numeric_level,
    )

    # Build list of processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add appropriate renderer based on format
    if is_terminal and enable_rich:
        try:
            from structlog.dev import ConsoleRenderer
            processors.append(
                ConsoleRenderer(
                    exception_formatter=structlog.dev.RichTracebackFormatter(
                        show_locals=log_level == "DEBUG"
                    )
                )
            )
        except ImportError:
            # Fallback to basic console renderer
            processors.append(structlog.dev.ConsoleRenderer())
    elif is_terminal:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Setup file logging if requested
    if log_file_path:
        file_path = Path(log_file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(numeric_level)

        # Use JSON format for file logging
        file_processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.dev.ConsoleRenderer(),
                foreign_pre_chain=file_processors,
            )
        )

        logging.getLogger().addHandler(file_handler)


def get_logger(name: str | None = None) -> Any:
    """Get a structured logger instance.
    
    Args:
        name: Logger name. If None, uses caller's module name.
        
    Returns:
        Structured logger instance.
    """
    return structlog.get_logger(name)


def add_logging_context(**kwargs: Any) -> None:
    """Add context variables to all subsequent log messages.
    
    Args:
        **kwargs: Context variables to add.
        
    Example:
        add_logging_context(user_id="123", request_id="abc")
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_logging_context() -> None:
    """Clear all context variables."""
    structlog.contextvars.clear_contextvars()


def log_function_call(func):
    """Decorator to log function calls with arguments and results.
    
    Args:
        func: Function to decorate.
        
    Returns:
        Decorated function.
    """
    logger = get_logger(func.__module__)

    def wrapper(*args, **kwargs):
        logger.debug(
            "Function called",
            function=func.__name__,
            args=args,
            kwargs=kwargs,
        )
        try:
            result = func(*args, **kwargs)
            logger.debug(
                "Function completed",
                function=func.__name__,
                result=result,
            )
            return result
        except Exception as e:
            logger.exception(
                "Function failed",
                function=func.__name__,
                error=str(e),
            )
            raise

    return wrapper


class LoggingConfig:
    """Configuration for logging setup."""

    # Logger names for different components
    MAIN = "teleprompter.main"
    UI = "teleprompter.ui"
    CORE = "teleprompter.core"
    DOMAIN = "teleprompter.domain"
    INFRA = "teleprompter.infrastructure"
    BACKEND = "teleprompter.backend"

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

        root_logger.info("Logging configured successfully")

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance for a specific component.
        
        Args:
            name: Logger name (e.g., 'teleprompter.backend.api')
            
        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to provide logging functionality to other classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class.
        
        Returns:
            Logger instance using the class's module and name.
        """
        # Get the logger based on the class's module and name
        logger_name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(logger_name)

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message with optional context.
        
        Args:
            message: Log message
            **kwargs: Additional context fields
        """
        self.logger.debug(message, extra=kwargs)

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log an info message with optional context.
        
        Args:
            message: Log message
            **kwargs: Additional context fields
        """
        self.logger.info(message, extra=kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message with optional context.
        
        Args:
            message: Log message
            **kwargs: Additional context fields
        """
        self.logger.warning(message, extra=kwargs)

    def log_error(self, message: str, **kwargs: Any) -> None:
        """Log an error message with optional context.
        
        Args:
            message: Log message
            **kwargs: Additional context fields
        """
        self.logger.error(message, extra=kwargs)

    def log_exception(self, message: str, **kwargs: Any) -> None:
        """Log an exception with traceback.
        
        Args:
            message: Log message
            **kwargs: Additional context fields
        """
        self.logger.exception(message, extra=kwargs)
