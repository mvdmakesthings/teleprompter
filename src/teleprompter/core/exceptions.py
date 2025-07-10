"""Custom exceptions for the teleprompter application.

This module defines a hierarchy of custom exceptions that provide meaningful
error information and enable proper error handling throughout the application.
"""

from typing import Any


class TeleprompterError(Exception):
    """Base exception for all teleprompter-related errors.

    All custom exceptions in the teleprompter application should inherit from this class.
    This provides a common base for catching all application-specific errors.

    Attributes:
        message: Human-readable error message
        error_code: Optional error code for programmatic handling
        context: Additional context information about the error
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize teleprompter error.

        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            context: Additional context information about the error
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause

        # Chain the exception if a cause was provided
        if cause is not None:
            self.__cause__ = cause

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]

        if self.error_code:
            parts.append(f"[{self.error_code}]")

        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"({context_str})")

        return " ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


# Maintain backward compatibility with existing exception names
class FileError(TeleprompterError):
    """Base exception for file-related errors."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize for backward compatibility."""
        super().__init__(message, context=details or {}, error_code="FILE_ERROR")
        self.details = details or {}


class FileNotFoundError(FileError):
    """Raised when a requested file cannot be found."""

    def __init__(self, file_path: str):
        """Initialize with the missing file path."""
        super().__init__(f"File not found: {file_path}", {"file_path": file_path})


class UnsupportedFileTypeError(FileError):
    """Raised when attempting to load an unsupported file type."""

    def __init__(self, file_path: str, supported_types: list[str]):
        """Initialize with file path and supported types."""
        super().__init__(
            f"Unsupported file type: {file_path}",
            {"file_path": file_path, "supported_types": supported_types},
        )


class FileLoadError(FileError):
    """Raised when a file cannot be loaded or read."""

    def __init__(self, file_path: str, reason: str):
        """Initialize with file path and failure reason."""
        super().__init__(
            f"Failed to load file {file_path}: {reason}",
            {"file_path": file_path, "reason": reason},
        )


class ContentError(TeleprompterError):
    """Base exception for content-related errors."""

    pass


class ContentParseError(ContentError):
    """Raised when content cannot be parsed."""

    def __init__(self, content_type: str, reason: str):
        """Initialize with content type and parse failure reason."""
        super().__init__(
            f"Failed to parse {content_type}: {reason}",
            {"content_type": content_type, "reason": reason},
        )


class ContentLoadError(ContentError):
    """Raised when content cannot be loaded."""

    def __init__(self, reason: str):
        """Initialize with load failure reason."""
        super().__init__(f"Failed to load content: {reason}", {"reason": reason})


class InvalidFileFormatError(FileError):
    """Raised when a file has an invalid format."""

    def __init__(self, file_path: str, expected_format: str | None = None):
        """Initialize with file path and expected format."""
        message = f"Invalid file format: {file_path}"
        if expected_format:
            message += f" (expected {expected_format})"

        super().__init__(
            message, {"file_path": file_path, "expected_format": expected_format}
        )


class VoiceError(TeleprompterError):
    """Base exception for voice control errors."""

    pass


class AudioDeviceError(VoiceError):
    """Raised when audio device is not available or accessible."""

    def __init__(self, device_name: str | None = None):
        """Initialize with optional device name."""
        message = "Audio device not available"
        if device_name:
            message = f"Audio device '{device_name}' not available"

        super().__init__(message, {"device_name": device_name})


class VoiceDetectionError(VoiceError):
    """Raised when voice detection fails."""

    def __init__(self, reason: str):
        """Initialize with failure reason."""
        super().__init__(f"Voice detection failed: {reason}", {"reason": reason})


class ConfigurationError(TeleprompterError):
    """Base exception for configuration errors."""

    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are invalid."""

    def __init__(self, key: str, value: any, reason: str):
        """Initialize with configuration details."""
        super().__init__(
            f"Invalid configuration for '{key}': {reason}",
            {"key": key, "value": value, "reason": reason},
        )


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, key: str):
        """Initialize with missing configuration key."""
        super().__init__(f"Required configuration missing: '{key}'", {"key": key})


class UIError(TeleprompterError):
    """Base exception for UI-related errors."""

    pass


class WidgetInitializationError(UIError):
    """Raised when a widget fails to initialize."""

    def __init__(self, widget_name: str, reason: str):
        """Initialize with widget details."""
        super().__init__(
            f"Failed to initialize {widget_name}: {reason}",
            {"widget_name": widget_name, "reason": reason},
        )


class ServiceError(TeleprompterError):
    """Base exception for service-related errors."""

    pass


class ServiceNotFoundError(ServiceError):
    """Raised when a required service is not found in the container."""

    def __init__(self, service_type: str):
        """Initialize with service type."""
        super().__init__(
            f"Service not found: {service_type}", context={"service_type": service_type}
        )


class ServiceInitializationError(ServiceError):
    """Raised when a service fails to initialize."""

    def __init__(self, service_name: str, reason: str):
        """Initialize with service details."""
        super().__init__(
            f"Failed to initialize service {service_name}: {reason}",
            {"service_name": service_name, "reason": reason},
        )


# New exception types for better error handling


class ParameterValidationError(TeleprompterError):
    """Raised when function parameters fail validation."""

    def __init__(
        self, parameter_name: str, value: Any, constraint: str, **kwargs
    ) -> None:
        super().__init__(
            f"Parameter '{parameter_name}' validation failed: {constraint} (got: {value})",
            error_code="PARAMETER_VALIDATION_FAILED",
            context={
                "parameter_name": parameter_name,
                "value": str(value),
                "constraint": constraint,
            },
            **kwargs,
        )


class StateValidationError(TeleprompterError):
    """Raised when object state validation fails."""

    def __init__(
        self, object_type: str, expected_state: str, actual_state: str, **kwargs
    ) -> None:
        super().__init__(
            f"{object_type} state validation failed: expected {expected_state}, got {actual_state}",
            error_code="STATE_VALIDATION_FAILED",
            context={
                "object_type": object_type,
                "expected_state": expected_state,
                "actual_state": actual_state,
            },
            **kwargs,
        )


class TimeoutError(TeleprompterError):
    """Raised when an operation times out."""

    def __init__(self, operation: str, timeout_seconds: float, **kwargs) -> None:
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            error_code="OPERATION_TIMEOUT",
            context={"operation": operation, "timeout_seconds": timeout_seconds},
            **kwargs,
        )


# Error recovery strategies
class ErrorRecovery:
    """Provides error recovery strategies for different error types."""

    @staticmethod
    def recover_from_file_error(error: FileError) -> str | None:
        """Attempt to recover from file errors.

        Args:
            error: The file error to recover from

        Returns:
            Alternative content or None if recovery not possible
        """
        if isinstance(error, FileNotFoundError):
            # Return default content for missing files
            return "# Welcome to CueBird\n\nNo file loaded."
        return None

    @staticmethod
    def recover_from_audio_error(error: AudioDeviceError) -> bool:
        """Attempt to recover from audio device errors.

        Args:
            error: The audio error to recover from

        Returns:
            True if recovered, False otherwise
        """
        # Could attempt to use default audio device
        # or disable voice features temporarily
        return False

    @staticmethod
    def should_retry(error: TeleprompterError) -> bool:
        """Determine if an operation should be retried after an error.

        Args:
            error: The error to evaluate

        Returns:
            True if operation should be retried
        """
        # Transient errors that might succeed on retry
        transient_errors = (
            AudioDeviceError,
            FileLoadError,
        )
        return isinstance(error, transient_errors)


# Convenience functions for error handling


def handle_file_error(file_path: str, operation: str = "access") -> None:
    """Check if file exists and is accessible, raise appropriate error if not.

    Args:
        file_path: Path to the file to check
        operation: Operation being performed on the file

    Raises:
        FileNotFoundError: If file doesn't exist
        FileError: If file cannot be accessed
    """
    import os

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    # Check basic read permissions
    if operation in ("read", "access") and not os.access(file_path, os.R_OK):
        raise FileError(
            f"Permission denied when attempting to {operation} file: {file_path}"
        )

    # Check write permissions
    if operation == "write" and not os.access(file_path, os.W_OK):
        raise FileError(
            f"Permission denied when attempting to {operation} file: {file_path}"
        )


def validate_parameter(
    name: str,
    value: Any,
    expected_type: type,
    min_value: float | None = None,
    max_value: float | None = None,
    allowed_values: list | None = None,
) -> None:
    """Validate a parameter against constraints.

    Args:
        name: Parameter name
        value: Parameter value
        expected_type: Expected type
        min_value: Minimum allowed value (for numeric types)
        max_value: Maximum allowed value (for numeric types)
        allowed_values: List of allowed values

    Raises:
        ParameterValidationError: If validation fails
    """
    # Type check
    if not isinstance(value, expected_type):
        raise ParameterValidationError(
            name, value, f"must be of type {expected_type.__name__}"
        )

    # Range checks for numeric values
    if min_value is not None and value < min_value:
        raise ParameterValidationError(name, value, f"must be >= {min_value}")

    if max_value is not None and value > max_value:
        raise ParameterValidationError(name, value, f"must be <= {max_value}")

    # Allowed values check
    if allowed_values is not None and value not in allowed_values:
        raise ParameterValidationError(name, value, f"must be one of {allowed_values}")
