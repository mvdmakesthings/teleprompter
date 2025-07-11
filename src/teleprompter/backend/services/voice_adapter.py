"""Voice detection service adapter without Qt dependencies."""

import threading
import time
from collections.abc import Callable

import numpy as np
import sounddevice as sd

from ...core import config
from ..api.models.domain import VoiceActivity, VoiceActivityState

try:
    import webrtcvad
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    webrtcvad = None


class VoiceDetectorAdapter:
    """Voice activity detector adapter for API use."""

    def __init__(self, on_voice_activity: Callable[[VoiceActivity], None] | None = None):
        """Initialize the voice detector adapter.
        
        Args:
            on_voice_activity: Callback for voice activity updates
        """
        self.on_voice_activity = on_voice_activity

        # Check if WebRTC VAD is available
        if not WEBRTC_AVAILABLE:
            self.vad = None
            self.use_simple_vad = True
        else:
            self.use_simple_vad = False
            self.vad = webrtcvad.Vad()

        # VAD configuration
        self.sample_rate = config.VAD_SAMPLE_RATE
        self.frame_duration = config.VAD_FRAME_DURATION
        self.sensitivity = config.VAD_SENSITIVITY

        # Audio buffer and processing
        self.audio_buffer = []
        self.is_running = False
        self.is_voice_detected = False
        self._audio_level = 0.0

        # Threading
        self._capture_thread = None
        self._processing_thread = None
        self._stop_event = threading.Event()

        # Voice detection state
        self._voice_start_time = None
        self._voice_stop_time = None
        self._state = VoiceActivityState.IDLE

        # Audio stream
        self._stream = None

    def start(self) -> None:
        """Start voice detection."""
        if self.is_running:
            return

        self.is_running = True
        self._stop_event.clear()
        self._state = VoiceActivityState.LISTENING

        try:
            # Start audio capture thread
            self._capture_thread = threading.Thread(target=self._capture_audio)
            self._capture_thread.daemon = True
            self._capture_thread.start()

            # Start processing thread
            self._processing_thread = threading.Thread(target=self._process_audio)
            self._processing_thread.daemon = True
            self._processing_thread.start()

            self._emit_activity()
        except Exception as e:
            self._state = VoiceActivityState.ERROR
            self._emit_activity(error=str(e))
            self.stop()

    def stop(self) -> None:
        """Stop voice detection."""
        if not self.is_running:
            return

        self.is_running = False
        self._stop_event.set()

        # Close audio stream
        if self._stream:
            self._stream.close()
            self._stream = None

        # Wait for threads to finish
        if self._capture_thread:
            self._capture_thread.join(timeout=1)
        if self._processing_thread:
            self._processing_thread.join(timeout=1)

        self._state = VoiceActivityState.IDLE
        self._emit_activity()

    def set_sensitivity(self, level: int) -> None:
        """Set detection sensitivity (0-3)."""
        if not 0 <= level <= 3:
            raise ValueError("Sensitivity must be between 0 and 3")
        self.sensitivity = level
        if self.vad:
            self.vad.set_mode(level)

    def get_audio_level(self) -> float:
        """Get current audio level (0.0-1.0)."""
        return self._audio_level

    def get_state(self) -> VoiceActivity:
        """Get current voice activity state."""
        return VoiceActivity(
            state=self._state,
            is_speaking=self.is_voice_detected,
            audio_level=self._audio_level,
            sensitivity=self.sensitivity
        )

    def _capture_audio(self) -> None:
        """Capture audio in a separate thread."""
        try:
            # Calculate frame size
            frame_size = int(self.sample_rate * self.frame_duration / 1000)

            # Open audio stream
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=frame_size,
                callback=self._audio_callback
            )

            with self._stream:
                while not self._stop_event.is_set():
                    time.sleep(0.1)

        except Exception as e:
            self._state = VoiceActivityState.ERROR
            self._emit_activity(error=str(e))

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream."""
        if status:
            print(f"Audio stream status: {status}")

        # Add to buffer
        self.audio_buffer.extend(indata[:, 0])

    def _process_audio(self) -> None:
        """Process audio for voice detection."""
        frame_size = int(self.sample_rate * self.frame_duration / 1000)

        while not self._stop_event.is_set():
            if len(self.audio_buffer) >= frame_size:
                # Get frame
                frame_data = self.audio_buffer[:frame_size]
                self.audio_buffer = self.audio_buffer[frame_size:]

                # Convert to numpy array
                audio_frame = np.array(frame_data, dtype=np.float32)

                # Calculate audio level
                self._audio_level = float(np.abs(audio_frame).mean())

                # Detect voice
                if self.use_simple_vad:
                    # Simple threshold-based detection
                    is_speech = self._audio_level > config.SIMPLE_VAD_THRESHOLD
                else:
                    # WebRTC VAD
                    # Convert to int16 for VAD
                    int16_frame = (audio_frame * 32768).astype(np.int16)
                    is_speech = self.vad.is_speech(int16_frame.tobytes(), self.sample_rate)

                # Update voice detection state
                if is_speech != self.is_voice_detected:
                    self.is_voice_detected = is_speech
                    self._state = VoiceActivityState.SPEAKING if is_speech else VoiceActivityState.LISTENING

                    if is_speech:
                        self._voice_start_time = time.time()
                    else:
                        self._voice_stop_time = time.time()

                    self._emit_activity()

            else:
                time.sleep(0.01)

    def _emit_activity(self, error: str | None = None) -> None:
        """Emit voice activity update."""
        if self.on_voice_activity:
            activity = VoiceActivity(
                state=self._state,
                is_speaking=self.is_voice_detected,
                audio_level=self._audio_level,
                sensitivity=self.sensitivity
            )
            self.on_voice_activity(activity)
