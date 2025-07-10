"""Unit tests for reading metrics service."""

from unittest.mock import patch

import pytest

from teleprompter.domain.reading import ReadingMetricsService


class TestReadingMetricsService:
    """Test the ReadingMetricsService class."""

    @pytest.fixture
    def service(self):
        """Create a ReadingMetricsService instance."""
        return ReadingMetricsService(base_wpm=150.0)

    def test_initialization(self, service):
        """Test service initialization."""
        assert service._base_wpm == 150.0
        assert service._word_count == 0
        assert service._current_progress == 0.0
        assert service._start_time is None
        assert service._pause_time is None
        assert service._total_pause_duration == 0.0

    def test_set_word_count(self, service):
        """Test setting word count."""
        service.set_word_count(500)
        assert service._word_count == 500

        # Test negative values are corrected
        service.set_word_count(-100)
        assert service._word_count == 0

    def test_set_progress(self, service):
        """Test setting reading progress."""
        service.set_progress(0.5)
        assert service._current_progress == 0.5

        # Test clamping
        service.set_progress(1.5)
        assert service._current_progress == 1.0

        service.set_progress(-0.5)
        assert service._current_progress == 0.0

    def test_calculate_reading_time(self, service):
        """Test reading time calculation."""
        # Normal calculation
        assert service.calculate_reading_time(150, 150) == 60.0  # 1 minute
        assert service.calculate_reading_time(300, 150) == 120.0  # 2 minutes

        # Edge cases
        assert service.calculate_reading_time(0, 150) == 0.0
        assert service.calculate_reading_time(150, 0) == 0.0
        assert service.calculate_reading_time(-100, 150) == 0.0

    def test_calculate_words_per_minute(self, service):
        """Test WPM calculation based on speed."""
        assert service.calculate_words_per_minute(1.0) == 150.0
        assert service.calculate_words_per_minute(2.0) == 300.0
        assert service.calculate_words_per_minute(0.5) == 75.0

    @patch("teleprompter.domain.reading.metrics.time.time")
    def test_reading_session_timing(self, mock_time, service):
        """Test reading session timing functionality."""
        # Start reading at time 100
        mock_time.return_value = 100.0
        service.start_reading()
        assert service._start_time == 100.0
        assert service._pause_time is None
        assert service._total_pause_duration == 0.0

        # Pause at time 110 (10 seconds elapsed)
        mock_time.return_value = 110.0
        service.pause_reading()
        assert service._pause_time == 110.0

        # Resume at time 115 (5 seconds paused)
        mock_time.return_value = 115.0
        service.resume_reading()
        assert service._pause_time is None
        assert service._total_pause_duration == 5.0

        # Get elapsed time at time 120
        mock_time.return_value = 120.0
        elapsed = service.get_elapsed_time()
        # Total time: 20 seconds - 5 seconds pause = 15 seconds
        assert elapsed == 15.0

    def test_get_elapsed_time_not_started(self, service):
        """Test elapsed time when session hasn't started."""
        assert service.get_elapsed_time() == 0.0

    @patch("teleprompter.domain.reading.metrics.time.time")
    def test_get_remaining_time(self, mock_time, service):
        """Test remaining time calculation."""
        # Set up reading session
        service.set_word_count(300)

        # No progress yet
        service.set_progress(0.0)
        remaining = service.get_remaining_time()
        # 300 words at 150 wpm = 2 minutes
        assert remaining == 120.0

        # 50% progress
        service.set_progress(0.5)
        mock_time.return_value = 100.0
        service.start_reading()

        # After 60 seconds (reading 150 words)
        mock_time.return_value = 160.0
        remaining = service.get_remaining_time()
        # 150 words remaining at actual speed
        assert remaining == 60.0

        # 100% progress
        service.set_progress(1.0)
        assert service.get_remaining_time() == 0.0

    def test_get_average_wpm(self, service):
        """Test average WPM calculation."""
        service.set_word_count(300)

        # No reading started
        assert service.get_average_wpm() == 0.0

        # Manually set timing values instead of mocking
        service._start_time = 0.0
        service._current_progress = 0.5

        # Override get_elapsed_time to return a fixed value
        with patch.object(service, "get_elapsed_time", return_value=60.0):
            assert service.get_average_wpm() == 150.0

        # Test with 100% progress
        service._current_progress = 1.0
        with patch.object(service, "get_elapsed_time", return_value=120.0):
            assert service.get_average_wpm() == 150.0

    def test_format_time(self, service):
        """Test time formatting."""
        assert service.format_time(30) == "30s"
        assert service.format_time(60) == "1m"
        assert service.format_time(90) == "1m 30s"
        assert service.format_time(3600) == "1h 0m"
        assert service.format_time(3665) == "1h 1m"
        assert service.format_time(7200) == "2h 0m"

    def test_get_statistics(self, service):
        """Test comprehensive statistics generation."""
        service.set_word_count(300)
        service.set_progress(0.5)

        # Manually set timing values
        service._start_time = 0.0
        service._pause_time = None
        service._total_pause_duration = 0.0

        # Mock get_elapsed_time and get_average_wpm
        with (
            patch.object(service, "get_elapsed_time", return_value=60.0),
            patch.object(service, "get_average_wpm", return_value=150.0),
        ):
            stats = service.get_statistics()

        assert stats["total_words"] == 300
        assert stats["words_read"] == 150
        assert stats["words_remaining"] == 150
        assert stats["progress_percentage"] == 50.0
        assert stats["elapsed_time"] == 60.0
        assert stats["elapsed_time_formatted"] == "1m"
        assert stats["average_wpm"] == 150.0
        assert stats["is_paused"] is False
        assert stats["total_pause_duration"] == 0.0

    def test_stop_reading(self, service):
        """Test stopping a reading session."""
        service._start_time = 100.0
        service._pause_time = 110.0

        service.stop_reading()

        assert service._start_time is None
        assert service._pause_time is None
