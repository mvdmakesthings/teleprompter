"""Unit tests for logging infrastructure."""

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import time

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
        # Use standard logging setup, not structlog
        with caplog.at_level(logging.DEBUG):
            TeleprompterLogger.setup_logging(level=logging.DEBUG)

            logger = TeleprompterLogger.get_logger("test")
            logger.debug("Debug message")
            logger.info("Info message")

            # Check if messages were logged (may be in different format)
            assert len(caplog.records) >= 2
            # Find our messages in the records
            messages = [r.message for r in caplog.records]
            assert any("Debug message" in msg for msg in messages)
            assert any("Info message" in msg for msg in messages)

    def test_setup_logging_with_file(self, tmp_path):
        """Test logging setup with file output."""
        log_file = tmp_path / "test.log"
        TeleprompterLogger.setup_logging(
            level=logging.INFO, log_file=log_file, detailed=True
        )

        # Use a logger that inherits from teleprompter namespace
        logger = TeleprompterLogger.get_logger("teleprompter.test")
        logger.info("Test message in file")

        # Give time for file write
        time.sleep(0.1)

        # Check file was created and contains message
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message in file" in content

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

        with caplog.at_level(logging.DEBUG):
            obj.log_debug("Debug", extra_field="value1")
            obj.log_info("Info", extra_field="value2")
            obj.log_warning("Warning", extra_field="value3")
            obj.log_error("Error", extra_field="value4")

            # Check messages were logged
            messages = [r.message for r in caplog.records]
            assert any("Debug" in msg for msg in messages)
            assert any("Info" in msg for msg in messages)
            assert any("Warning" in msg for msg in messages)
            assert any("Error" in msg for msg in messages)

    def test_log_exception(self, caplog):
        """Test exception logging."""
        obj = self.MockClass()

        with caplog.at_level(logging.ERROR):
            try:
                raise ValueError("Test exception")
            except ValueError:
                obj.log_exception("An error occurred")

            # Check exception was logged
            assert len(caplog.records) >= 1
            error_record = caplog.records[-1]
            assert error_record.levelno == logging.ERROR
            assert "An error occurred" in error_record.message
            assert error_record.exc_info is not None


class TestPerformanceLogger:
    """Test the PerformanceLogger class."""

    def test_start_stop_timer(self):
        """Test starting and stopping timers."""
        perf_logger = PerformanceLogger()

        perf_logger.start_timer("test_operation")
        time.sleep(0.01)  # Small delay
        duration = perf_logger.end_timer("test_operation")

        assert duration > 0
        assert duration < 1  # Should be much less than 1 second

    def test_timer_not_found(self):
        """Test stopping non-existent timer."""
        perf_logger = PerformanceLogger()

        # Should return 0.0 for non-existent timer
        duration = perf_logger.end_timer("non_existent")
        assert duration == 0.0

    def test_log_memory_usage(self, caplog):
        """Test memory usage logging."""
        # Set up standard logging to capture structlog output
        import structlog

        structlog.configure(
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

        perf_logger = PerformanceLogger()

        with caplog.at_level(logging.INFO):
            perf_logger.log_memory_usage("test_point")

            # Check that a log message was produced
            # The message will either contain MB (if psutil is installed)
            # or "Memory logging unavailable" (if not)
            assert len(caplog.records) >= 1

    def test_context_manager(self):
        """Test using PerformanceLogger as context manager."""
        perf_logger = PerformanceLogger()

        with perf_logger.timer("test_block"):
            time.sleep(0.01)

        # Timer should have been stopped
        # Trying to stop again should return 0.0
        assert perf_logger.end_timer("test_block") == 0.0


class TestDecorators:
    """Test logging decorators."""

    def test_log_method_calls_success(self, caplog):
        """Test method call logging for successful calls."""

        class TestClass:
            @log_method_calls()
            def test_method(self, arg1, arg2="default"):
                return f"{arg1}-{arg2}"

        obj = TestClass()

        with caplog.at_level(logging.DEBUG):
            result = obj.test_method("value1", arg2="value2")

            assert result == "value1-value2"
            # Check method call was logged
            messages = [r.message for r in caplog.records]
            assert any("test_method" in msg for msg in messages)

    def test_log_method_calls_failure(self, caplog):
        """Test method call logging for failed calls."""

        class TestClass:
            @log_method_calls()
            def failing_method(self):
                raise ValueError("Test error")

        obj = TestClass()

        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                obj.failing_method()

            # Check error was logged
            messages = [r.message for r in caplog.records]
            assert any("failing_method" in msg for msg in messages)


def test_get_logger():
    """Test the global get_logger function."""
    logger = get_logger("test.module")
    # get_logger returns a structlog BoundLogger, not a standard logging.Logger
    assert logger is not None
    # Test that we can log with it
    logger.info("test message")
