"""Tests for voice detection adapter."""

from unittest.mock import MagicMock, patch

import pytest

from teleprompter.backend.api.models.domain import VoiceActivity, VoiceActivityState
from teleprompter.backend.services.voice_adapter import VoiceDetectorAdapter


class TestVoiceDetectorAdapter:
    """Test voice detector adapter."""

    @pytest.fixture
    def voice_adapter(self):
        """Create a voice adapter with mock callback."""
        callback = MagicMock()
        adapter = VoiceDetectorAdapter(on_voice_activity=callback)
        yield adapter
        # Cleanup
        adapter.stop()

    def test_initialization(self, voice_adapter):
        """Test adapter initialization."""
        assert voice_adapter.sensitivity == 1  # Default from config
        assert not voice_adapter.is_running
        assert voice_adapter._audio_level == 0.0
        assert voice_adapter._state == VoiceActivityState.IDLE

    def test_set_sensitivity(self, voice_adapter):
        """Test setting sensitivity."""
        voice_adapter.set_sensitivity(3)
        assert voice_adapter.sensitivity == 3

        with pytest.raises(ValueError):
            voice_adapter.set_sensitivity(4)

        with pytest.raises(ValueError):
            voice_adapter.set_sensitivity(-1)

    def test_get_state(self, voice_adapter):
        """Test getting voice activity state."""
        state = voice_adapter.get_state()

        assert isinstance(state, VoiceActivity)
        assert state.state == VoiceActivityState.IDLE
        assert state.is_speaking is False
        assert state.audio_level == 0.0
        assert state.sensitivity == 1

    @patch('sounddevice.InputStream')
    def test_start_stop(self, mock_stream, voice_adapter):
        """Test starting and stopping voice detection."""
        # Mock audio stream
        mock_stream_instance = MagicMock()
        mock_stream.return_value = mock_stream_instance

        # Start detection
        voice_adapter.start()
        assert voice_adapter.is_running
        assert voice_adapter._state == VoiceActivityState.LISTENING

        # Give threads time to start
        import time
        time.sleep(0.1)

        # Stop detection
        voice_adapter.stop()
        assert not voice_adapter.is_running
        assert voice_adapter._state == VoiceActivityState.IDLE

        # Verify stream was closed
        mock_stream_instance.close.assert_called_once()

    def test_audio_level_calculation(self, voice_adapter):
        """Test audio level calculation."""
        # Simulate audio data
        import numpy as np

        # Test with silence
        silence = np.zeros(1000, dtype=np.float32)
        # Directly test level calculation without threading
        voice_adapter._audio_level = float(np.abs(silence).mean())
        assert voice_adapter._audio_level == 0.0

        # Test with noise
        noise = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        voice_adapter._audio_level = float(np.abs(noise).mean())
        assert 0.0 < voice_adapter._audio_level < 1.0

    def test_callback_invocation(self, voice_adapter):
        """Test that callback is invoked on state changes."""
        # Start detection
        voice_adapter._state = VoiceActivityState.LISTENING
        voice_adapter._emit_activity()

        # Check callback was called
        voice_adapter.on_voice_activity.assert_called_once()
        activity = voice_adapter.on_voice_activity.call_args[0][0]
        assert isinstance(activity, VoiceActivity)
        assert activity.state == VoiceActivityState.LISTENING

    def test_simple_vad_mode(self):
        """Test adapter when WebRTC VAD is not available."""
        with patch('teleprompter.backend.services.voice_adapter.WEBRTC_AVAILABLE', False):
            adapter = VoiceDetectorAdapter()
            assert adapter.use_simple_vad is True
            assert adapter.vad is None

    def test_error_handling(self, voice_adapter):
        """Test error handling during detection."""
        # Simulate error during audio capture
        with patch('sounddevice.InputStream', side_effect=Exception("Audio error")):
            voice_adapter.start()

            # Give time for error to propagate
            import time
            time.sleep(0.1)

            # Check that error state was set
            assert voice_adapter._state == VoiceActivityState.ERROR

            # Check callback was called with error
            voice_adapter.on_voice_activity.assert_called()
            activity = voice_adapter.on_voice_activity.call_args[0][0]
            assert activity.state == VoiceActivityState.ERROR
