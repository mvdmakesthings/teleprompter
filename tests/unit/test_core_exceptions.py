"""Unit tests for core exception classes."""

from teleprompter.core import (
    AudioDeviceError,
    ErrorRecovery,
    FileLoadError,
    FileNotFoundError,
    TeleprompterError,
    UnsupportedFileTypeError,
)


class TestTeleprompterError:
    """Test the base TeleprompterError class."""

    def test_basic_exception(self):
        """Test creating a basic exception."""
        error = TeleprompterError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == {}

    def test_exception_with_details(self):
        """Test creating an exception with details."""
        details = {"key": "value", "count": 42}
        error = TeleprompterError("Test error", details)
        assert error.message == "Test error"
        assert error.details == details
        assert error.details["key"] == "value"
        assert error.details["count"] == 42


class TestFileExceptions:
    """Test file-related exceptions."""

    def test_file_not_found_error(self):
        """Test FileNotFoundError."""
        error = FileNotFoundError("/path/to/missing.txt")
        assert "File not found: /path/to/missing.txt" in str(error)
        assert error.details["file_path"] == "/path/to/missing.txt"

    def test_unsupported_file_type_error(self):
        """Test UnsupportedFileTypeError."""
        error = UnsupportedFileTypeError("file.xyz", [".md", ".txt"])
        assert "Unsupported file type: file.xyz" in str(error)
        assert error.details["file_path"] == "file.xyz"
        assert error.details["supported_types"] == [".md", ".txt"]

    def test_file_load_error(self):
        """Test FileLoadError."""
        error = FileLoadError("/path/to/file.txt", "Permission denied")
        assert "Failed to load file /path/to/file.txt: Permission denied" in str(error)
        assert error.details["file_path"] == "/path/to/file.txt"
        assert error.details["reason"] == "Permission denied"


class TestAudioDeviceError:
    """Test audio device errors."""

    def test_audio_device_error_no_name(self):
        """Test AudioDeviceError without device name."""
        error = AudioDeviceError()
        assert str(error) == "Audio device not available"
        assert error.details["device_name"] is None

    def test_audio_device_error_with_name(self):
        """Test AudioDeviceError with device name."""
        error = AudioDeviceError("Built-in Microphone")
        assert str(error) == "Audio device 'Built-in Microphone' not available"
        assert error.details["device_name"] == "Built-in Microphone"


class TestErrorRecovery:
    """Test error recovery strategies."""

    def test_recover_from_file_not_found(self):
        """Test recovery from FileNotFoundError."""
        error = FileNotFoundError("/missing.txt")
        result = ErrorRecovery.recover_from_file_error(error)
        assert result is not None
        assert "# Welcome to Teleprompter" in result
        assert "No file loaded." in result

    def test_recover_from_file_load_error(self):
        """Test recovery from FileLoadError returns None."""
        error = FileLoadError("/file.txt", "Error")
        result = ErrorRecovery.recover_from_file_error(error)
        assert result is None

    def test_should_retry_transient_errors(self):
        """Test that transient errors are marked for retry."""
        # Should retry
        assert ErrorRecovery.should_retry(AudioDeviceError())
        assert ErrorRecovery.should_retry(FileLoadError("/file.txt", "reason"))

        # Should not retry
        assert not ErrorRecovery.should_retry(FileNotFoundError("/file.txt"))
        assert not ErrorRecovery.should_retry(TeleprompterError("Generic error"))
