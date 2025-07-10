"""Unit tests for logging infrastructure."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from teleprompter.infrastructure.logging import (
    LoggerMixin,
    PerformanceLogger,
    TeleprompterLogger,
    get_logger,
    log_method_calls,
    log_performance,
)


class TestTeleprompterLogger:
    """Test the TeleprompterLogger class."""

    def test_logger_names(self):
        """Test that logger names are correctly defined."""
        assert TeleprompterLogger.MAIN == "teleprompter.main"
        assert TeleprompterLogger.UI == "teleprompter.ui"
        assert TeleprompterLogger.CORE == "teleprompter.core"
        assert TeleprompterLogger.DOMAIN == "teleprompter.domain"
        assert TeleprompterLogger.INFRA == "teleprompter.infrastructure"

    def test_setup_logging_basic(self, caplog):
        """Test basic logging setup."""
        TeleprompterLogger.setup_logging(level=logging.DEBUG)

        logger = get_logger("teleprompter.test")
        logger.debug("Debug message")
        logger.info("Info message")

        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text

    def test_setup_logging_with_file(self, tmp_path):
        """Test logging setup with file output."""
        log_file = tmp_path / "test.log"
        TeleprompterLogger.setup_logging(
            level=logging.INFO, log_file=log_file, detailed=True
        )

        logger = get_logger("teleprompter.test")
        logger.info("Test message in file")

        # Check file was created and contains message
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message in file" in content
        assert "[test_infrastructure_logging.py:" in content  # Detailed format

    def test_get_logger(self):
        """Test getting logger instances."""
        logger1 = TeleprompterLogger.get_logger("test.module1")
        logger2 = TeleprompterLogger.get_logger("test.module2")
        logger3 = TeleprompterLogger.get_logger("test.module1")

        assert logger1.name == "test.module1"
        assert logger2.name == "test.module2"
        assert logger1 is logger3  # Same logger returned


class TestLoggerMixin:
    """Test the LoggerMixin class."""

    class MockClass(LoggerMixin):
        """Mock class using LoggerMixin."""

        pass

    def test_logger_property(self):
        """Test that logger property works correctly."""
        obj = self.MockClass()
        logger = obj.logger

        assert isinstance(logger, logging.Logger)
        assert logger.name.endswith("MockClass")
        # Should return same logger on subsequent calls
        assert obj.logger is logger

    def test_log_methods(self, caplog):
        """Test convenience logging methods."""
        obj = self.MockClass()
        obj.logger.setLevel(logging.DEBUG)

        obj.log_debug("Debug", extra_field="value1")
        obj.log_info("Info", extra_field="value2")
        obj.log_warning("Warning", extra_field="value3")
        obj.log_error("Error", extra_field="value4")

        assert "Debug" in caplog.text
        assert "Info" in caplog.text
        assert "Warning" in caplog.text
        assert "Error" in caplog.text

    def test_log_exception(self, caplog):
        """Test exception logging."""
        obj = self.MockClass()

        try:
            raise ValueError("Test exception")
        except ValueError:
            obj.log_exception("Caught exception")

        assert "Caught exception" in caplog.text
        assert "ValueError: Test exception" in caplog.text


class TestPerformanceLogger:
    """Test the PerformanceLogger class."""

    def test_timer_operations(self, caplog):
        """Test timer start and end operations."""
        logger = logging.getLogger("test")
        perf_logger = PerformanceLogger(logger)

        perf_logger.start_timer("operation1")
        # Simulate some work
        import time

        time.sleep(0.01)
        duration = perf_logger.end_timer("operation1")

        assert duration > 0.01
        assert "Operation 'operation1' completed" in caplog.text

    def test_timer_not_found(self, caplog):
        """Test ending a timer that wasn't started."""
        logger = logging.getLogger("test")
        perf_logger = PerformanceLogger(logger)

        duration = perf_logger.end_timer("nonexistent")

        assert duration == 0.0
        assert "No timer found for operation: nonexistent" in caplog.text

    @patch("teleprompter.infrastructure.logging.psutil")
    def test_log_memory_usage(self, mock_psutil, caplog):
        """Test memory usage logging with psutil available."""
        # Mock psutil
        mock_process = MagicMock()
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        mock_memory_info.vms = 200 * 1024 * 1024  # 200MB
        mock_process.memory_info.return_value = mock_memory_info
        mock_psutil.Process.return_value = mock_process

        logger = logging.getLogger("test")
        perf_logger = PerformanceLogger(logger)
        perf_logger.log_memory_usage()

        assert "Memory usage - RSS: 100.0MB, VMS: 200.0MB" in caplog.text


class TestDecorators:
    """Test logging decorators."""

    class MockClass(LoggerMixin):
        """Mock class for testing decorators."""

        @log_method_calls()
        def test_method(self, arg1, arg2=None):
            """Test method with decorator."""
            return f"Result: {arg1}, {arg2}"

        @log_method_calls()
        def failing_method(self):
            """Method that raises exception."""
            raise ValueError("Test error")

        @log_performance("custom_operation")
        def slow_method(self):
            """Method with performance logging."""
            import time

            time.sleep(0.01)
            return "Done"

    def test_log_method_calls_success(self, caplog):
        """Test method call logging on success."""
        obj = self.MockClass()
        result = obj.test_method("value1", arg2="value2")

        assert result == "Result: value1, value2"
        assert "Entering test_method" in caplog.text
        assert "Exiting test_method successfully" in caplog.text

    def test_log_method_calls_failure(self, caplog):
        """Test method call logging on failure."""
        obj = self.MockClass()

        with pytest.raises(ValueError):
            obj.failing_method()

        assert "Entering failing_method" in caplog.text
        assert "Error in failing_method: Test error" in caplog.text

    def test_log_performance_decorator(self, caplog):
        """Test performance logging decorator."""
        obj = self.MockClass()
        result = obj.slow_method()

        assert result == "Done"
        assert "Started timing: custom_operation" in caplog.text
        assert "Operation 'custom_operation' completed" in caplog.text
