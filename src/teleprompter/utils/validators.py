"""Input validation utilities for the teleprompter application.

This module provides comprehensive validation functions for user inputs,
configuration values, and data integrity throughout the application.
"""

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from ..core.exceptions import (
    InvalidConfigurationError,
    TeleprompterError,
    UnsupportedFileTypeError,
)

T = TypeVar("T")


class ValidationError(TeleprompterError):
    """Raised when validation fails."""

    def __init__(self, field: str, value: Any, reason: str, **kwargs):
        super().__init__(
            f"Validation failed for '{field}': {reason}",
            error_code="VALIDATION_FAILED",
            context={"field": field, "value": str(value), "reason": reason},
            **kwargs
        )
        # Legacy compatibility
        self.field = field
        self.value = value
        self.reason = reason


class Validators:
    """Collection of common validation functions."""

    @staticmethod
    def validate_required(value: Any, field_name: str) -> Any:
        """Validate that a value is not None or empty.

        Args:
            value: Value to validate
            field_name: Name of the field for error messages

        Returns:
            The validated value

        Raises:
            ValidationError: If value is None or empty
        """
        if value is None:
            raise ValidationError(field_name, value, "Value is required")

        # Check for empty strings, lists, dicts
        if hasattr(value, "__len__") and len(value) == 0:
            raise ValidationError(field_name, value, "Value cannot be empty")

        return value

    @staticmethod
    def validate_type(value: Any, expected_type: type, field_name: str) -> Any:
        """Validate that a value is of the expected type.

        Args:
            value: Value to validate
            expected_type: Expected type
            field_name: Name of the field for error messages

        Returns:
            The validated value

        Raises:
            ValidationError: If value is not of expected type
        """
        if not isinstance(value, expected_type):
            raise ValidationError(
                field_name,
                value,
                f"Expected type {expected_type.__name__}, got {type(value).__name__}"
            )
        return value

    @staticmethod
    def validate_range(
        value: int | float,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        field_name: str = "value"
    ) -> int | float:
        """Validate that a numeric value is within a specified range.

        Args:
            value: Value to validate
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            field_name: Name of the field for error messages

        Returns:
            The validated value

        Raises:
            ValidationError: If value is outside the specified range
        """
        if min_value is not None and value < min_value:
            raise ValidationError(
                field_name,
                value,
                f"Value must be >= {min_value}"
            )

        if max_value is not None and value > max_value:
            raise ValidationError(
                field_name,
                value,
                f"Value must be <= {max_value}"
            )

        return value

    @staticmethod
    def validate_choice(
        value: T,
        choices: list[T] | tuple[T, ...] | set[T],
        field_name: str = "value"
    ) -> T:
        """Validate that a value is one of the allowed choices.

        Args:
            value: Value to validate
            choices: Allowed values
            field_name: Name of the field for error messages

        Returns:
            The validated value

        Raises:
            ValidationError: If value is not in choices
        """
        if value not in choices:
            raise ValidationError(
                field_name,
                value,
                f"Value must be one of: {', '.join(str(c) for c in choices)}"
            )
        return value

    @staticmethod
    def validate_file_path(
        path: str | Path | None,
        must_exist: bool = False,
        extensions: list[str] | None = None
    ) -> Path | None:
        """Validate a file path.

        Args:
            path: File path to validate (can be None)
            must_exist: Whether the file must exist
            extensions: List of allowed extensions (e.g., ['.md', '.txt'])

        Returns:
            Validated Path object or None if path is None

        Raises:
            ValidationError: If path is invalid
            FileNotFoundError: If must_exist=True and file doesn't exist
            UnsupportedFileTypeError: If extension is not allowed
        """
        if path is None:
            return None
            
        path = Path(path)

        if must_exist and not path.exists():
            from teleprompter.core.exceptions import FileNotFoundError
            raise FileNotFoundError(str(path))

        if extensions and path.suffix not in extensions:
            raise UnsupportedFileTypeError(str(path), extensions)

        return path

    @staticmethod
    def validate_directory_path(
        path: str | Path | None,
        must_exist: bool = False,
        create_if_missing: bool = False
    ) -> Path | None:
        """Validate a directory path.

        Args:
            path: Directory path to validate (can be None)
            must_exist: Whether the directory must exist
            create_if_missing: Create directory if it doesn't exist

        Returns:
            Validated Path object or None if path is None

        Raises:
            ValidationError: If path is invalid
        """
        if path is None:
            return None
            
        path = Path(path)

        if must_exist and not path.exists():
            if create_if_missing:
                path.mkdir(parents=True, exist_ok=True)
            else:
                raise ValidationError(
                    "directory_path",
                    str(path),
                    "Directory does not exist"
                )

        if path.exists() and not path.is_dir():
            raise ValidationError(
                "directory_path",
                str(path),
                "Path exists but is not a directory"
            )

        return path

    @staticmethod
    def validate_regex(
        value: str,
        pattern: str,
        field_name: str = "value",
        error_message: str | None = None
    ) -> str:
        """Validate that a string matches a regex pattern.

        Args:
            value: String to validate
            pattern: Regex pattern
            field_name: Name of the field for error messages
            error_message: Custom error message

        Returns:
            The validated value

        Raises:
            ValidationError: If value doesn't match pattern
        """
        if not re.match(pattern, value):
            message = error_message or f"Value does not match pattern: {pattern}"
            raise ValidationError(field_name, value, message)
        return value

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate an email address format.

        Args:
            email: Email address to validate

        Returns:
            The validated email

        Raises:
            ValidationError: If email format is invalid
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return Validators.validate_regex(
            email,
            pattern,
            "email",
            "Invalid email format"
        )

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate a URL format.

        Args:
            url: URL to validate

        Returns:
            The validated URL

        Raises:
            ValidationError: If URL format is invalid
        """
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return Validators.validate_regex(
            url,
            pattern,
            "url",
            "Invalid URL format"
        )


class ConfigValidator:
    """Validator for configuration values."""

    def __init__(self):
        """Initialize the configuration validator."""
        self.validators: dict[str, Callable] = {}

    def register(self, key: str, validator: Callable) -> None:
        """Register a validator for a configuration key.

        Args:
            key: Configuration key
            validator: Validation function
        """
        self.validators[key] = validator

    def validate(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate a configuration dictionary.

        Args:
            config: Configuration to validate

        Returns:
            Validated configuration

        Raises:
            InvalidConfigurationError: If validation fails
        """
        validated = {}

        for key, value in config.items():
            if key in self.validators:
                try:
                    validated[key] = self.validators[key](value)
                except (ValidationError, ValueError) as e:
                    raise InvalidConfigurationError(
                        key,
                        value,
                        str(e)
                    ) from e
            else:
                # Pass through unregistered keys
                validated[key] = value

        return validated


class TeleprompterConfigValidator(ConfigValidator):
    """Validator for teleprompter-specific configuration."""

    def __init__(self):
        """Initialize with teleprompter validation rules."""
        super().__init__()
        self._register_validators()

    def _register_validators(self) -> None:
        """Register all teleprompter configuration validators."""
        # Window configuration
        self.register("window_width", lambda v: Validators.validate_range(
            v, min_value=640, max_value=7680, field_name="window_width"
        ))
        self.register("window_height", lambda v: Validators.validate_range(
            v, min_value=480, max_value=4320, field_name="window_height"
        ))

        # Font configuration
        self.register("font_size", lambda v: Validators.validate_range(
            v, min_value=8, max_value=200, field_name="font_size"
        ))
        self.register("font_family", lambda v: Validators.validate_type(
            v, str, "font_family"
        ))

        # Speed configuration
        self.register("scroll_speed", lambda v: Validators.validate_range(
            v, min_value=0.05, max_value=10.0, field_name="scroll_speed"
        ))
        self.register("default_wpm", lambda v: Validators.validate_range(
            v, min_value=50, max_value=1000, field_name="default_wpm"
        ))

        # Voice control
        self.register("voice_sensitivity", lambda v: Validators.validate_range(
            v, min_value=0, max_value=3, field_name="voice_sensitivity"
        ))

        # Theme
        self.register("theme", lambda v: Validators.validate_choice(
            v, ["dark", "light", "high_contrast"], field_name="theme"
        ))

        # File paths
        self.register("last_file", lambda v: Validators.validate_file_path(
            v, must_exist=False
        ))
        self.register("settings_directory", lambda v: Validators.validate_directory_path(
            v, must_exist=False, create_if_missing=True
        ))


# Decorator for validation
def validate_input(**validators):
    """Decorator to validate function inputs.

    Args:
        **validators: Keyword arguments mapping parameter names to validation functions

    Example:
        @validate_input(
            text=lambda v: Validators.validate_required(v, "text"),
            size=lambda v: Validators.validate_range(v, 1, 100, "size")
        )
        def process(text: str, size: int):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Validate specified parameters
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    try:
                        bound.arguments[param_name] = validator(
                            bound.arguments[param_name]
                        )
                    except Exception as e:
                        raise ValidationError(
                            param_name,
                            bound.arguments[param_name],
                            str(e)
                        ) from e

            return func(*bound.args, **bound.kwargs)

        return wrapper
    return decorator
