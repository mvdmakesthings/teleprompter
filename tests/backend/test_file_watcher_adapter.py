"""Tests for file watcher adapter."""

import contextlib
import os
import tempfile
import time
from unittest.mock import MagicMock

import pytest

from teleprompter.backend.api.models.domain import FileWatchEvent
from teleprompter.backend.services.file_watcher_adapter import FileWatcherAdapter


class TestFileWatcherAdapter:
    """Test file watcher adapter."""

    @pytest.fixture
    def file_watcher(self):
        """Create a file watcher with mock callback."""
        callback = MagicMock()
        watcher = FileWatcherAdapter(on_file_event=callback)
        yield watcher
        # Cleanup
        watcher.stop_watching()

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Initial content")
            temp_path = f.name

        yield temp_path

        # Cleanup
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temp_path)

    def test_initialization(self, file_watcher):
        """Test adapter initialization."""
        assert file_watcher._current_file is None
        assert file_watcher._debounce_delay == 0.5
        assert not file_watcher.is_watching()

    def test_watch_nonexistent_file(self, file_watcher):
        """Test watching a non-existent file."""
        result = file_watcher.watch_file("/non/existent/file.txt")
        assert result is False

        # Check error event was emitted
        file_watcher.on_file_event.assert_called_once()
        event = file_watcher.on_file_event.call_args[0][0]
        assert isinstance(event, FileWatchEvent)
        assert event.event_type == "error"
        assert "File not found" in event.error

    def test_watch_file_success(self, file_watcher, temp_file):
        """Test successfully watching a file."""
        result = file_watcher.watch_file(temp_file)
        assert result is True
        assert file_watcher.is_watching()
        assert file_watcher.get_watched_file() == temp_file

    def test_stop_watching(self, file_watcher, temp_file):
        """Test stopping file watch."""
        # Start watching
        file_watcher.watch_file(temp_file)
        assert file_watcher.is_watching()

        # Stop watching
        file_watcher.stop_watching()
        assert not file_watcher.is_watching()
        assert file_watcher.get_watched_file() is None

    def test_file_change_detection(self, file_watcher, temp_file):
        """Test detecting file changes."""
        # Start watching
        file_watcher.watch_file(temp_file)

        # Directly trigger the event handler
        if file_watcher._event_handler:
            file_watcher._event_handler.on_event(FileWatchEvent(
                event_type="changed",
                file_path=temp_file
            ))

        # Wait for debounce
        time.sleep(0.6)

        # Check change event was emitted
        file_watcher.on_file_event.assert_called()
        event = file_watcher.on_file_event.call_args[0][0]
        assert isinstance(event, FileWatchEvent)
        assert event.event_type == "changed"
        assert event.file_path == temp_file

    def test_file_deletion_detection(self, file_watcher, temp_file):
        """Test detecting file deletion."""
        # Start watching
        file_watcher.watch_file(temp_file)

        # Directly trigger the event handler
        if file_watcher._event_handler:
            file_watcher._event_handler.on_event(FileWatchEvent(
                event_type="removed",
                file_path=temp_file
            ))

        # Wait for debounce
        time.sleep(0.6)

        # Check removal event was emitted
        file_watcher.on_file_event.assert_called()
        event = file_watcher.on_file_event.call_args[0][0]
        assert isinstance(event, FileWatchEvent)
        assert event.event_type == "removed"
        assert event.file_path == temp_file

    def test_debouncing(self, file_watcher, temp_file):
        """Test that rapid changes are debounced."""
        # Start watching
        file_watcher.watch_file(temp_file)

        # Give observer time to start
        time.sleep(0.1)

        # Make multiple rapid changes
        for i in range(5):
            with open(temp_file, 'w') as f:
                f.write(f"Change {i}")
            time.sleep(0.1)  # Less than debounce delay

        # Wait for debounce to complete
        time.sleep(1.0)

        # Should only get one event due to debouncing
        # (May get 2 on some systems due to timing)
        assert file_watcher.on_file_event.call_count <= 2

    def test_set_debounce_delay(self, file_watcher):
        """Test setting debounce delay."""
        file_watcher.set_debounce_delay(1000)
        assert file_watcher._debounce_delay == 1.0

        with pytest.raises(ValueError):
            file_watcher.set_debounce_delay(-100)

    def test_multiple_file_switches(self, file_watcher):
        """Test switching between watching different files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write("File 1")
            file1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write("File 2")
            file2 = f2.name

        try:
            # Watch first file
            assert file_watcher.watch_file(file1)
            assert file_watcher.get_watched_file() == file1

            # Switch to second file
            assert file_watcher.watch_file(file2)
            assert file_watcher.get_watched_file() == file2

            # Verify observer was properly cleaned up
            assert file_watcher._observer.is_alive()

        finally:
            os.unlink(file1)
            os.unlink(file2)

    def test_observer_thread_cleanup(self, file_watcher, temp_file):
        """Test that observer thread is properly cleaned up."""
        # Start watching
        file_watcher.watch_file(temp_file)
        observer = file_watcher._observer

        # Stop watching
        file_watcher.stop_watching()

        # Give thread time to stop
        time.sleep(0.2)

        # Check observer is stopped
        assert not observer.is_alive()
