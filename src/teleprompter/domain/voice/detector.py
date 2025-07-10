"""Voice activity detection for teleprompter control."""

import threading
import time

import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import webrtcvad

    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    webrtcvad = None

from ...core import config


class VoiceActivityDetector(QObject):
    """Voice activity detector using WebRTC VAD."""

    # Signals for voice activity events
    voice_started = pyqtSignal()
    voice_stopped = pyqtSignal()
    voice_level_changed = pyqtSignal(float)  # Audio level (0.0 to 1.0)
    speech_detected = pyqtSignal(
        bool
    )  # True when speech is detected, False when silent
    error_occurred = pyqtSignal(str)
    microphone_ready = (
        pyqtSignal()
    )  # Emitted when microphone is successfully initialized

    def __init__(self, parent=None):
        """Initialize the voice activity detector."""
        super().__init__(parent)

        # Check if WebRTC VAD is available
        if not WEBRTC_AVAILABLE:
            self.vad = None
            self.use_simple_vad = True
        else:
            self.use_simple_vad = False

        # VAD configuration
        self.sample_rate = config.VAD_SAMPLE_RATE
        self.frame_duration = config.VAD_FRAME_DURATION
        self.sensitivity = config.VAD_SENSITIVITY
        self.start_delay = config.VAD_START_DELAY
        self.stop_delay = config.VAD_STOP_DELAY

        # Calculate frame size in samples
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)

        # Initialize WebRTC VAD if available
        if not self.use_simple_vad:
            # For WebRTC VAD, use integer part of sensitivity as initial mode
            webrtc_mode = min(3, int(self.sensitivity))
            self.vad = webrtcvad.Vad(webrtc_mode)

        # Initialize threshold based on sensitivity (for both VAD types)
        self.voice_threshold = 0.01  # Default, will be updated by set_sensitivity
        self.set_sensitivity(self.sensitivity)  # Apply initial sensitivity settings

        # State tracking (thread-safe access required)
        self._state_lock = threading.RLock()
        self._is_running = False
        self._is_speaking = False
        self._is_speech_detected = False  # Current speech detection state
        self._last_voice_time = 0.0
        self._last_silence_time = 0.0
        self._audio_level = 0.0

        # Threading
        self.audio_thread: threading.Thread | None = None
        self.audio_stream: sd.InputStream | None = None

        # Audio buffer with thread-safe access
        self._buffer_lock = threading.Lock()
        self._audio_buffer = np.array([], dtype=np.float32)

        # Signal emission queue for thread safety
        self._signal_lock = threading.Lock()
        self._pending_signals = []

    # Thread-safe property accessors
    @property
    def is_running(self) -> bool:
        """Get running state (thread-safe)."""
        with self._state_lock:
            return self._is_running

    @is_running.setter
    def is_running(self, value: bool):
        """Set running state (thread-safe)."""
        with self._state_lock:
            self._is_running = value

    @property
    def is_speaking(self) -> bool:
        """Get speaking state (thread-safe)."""
        with self._state_lock:
            return self._is_speaking

    @is_speaking.setter
    def is_speaking(self, value: bool):
        """Set speaking state (thread-safe)."""
        with self._state_lock:
            self._is_speaking = value

    @property
    def is_speech_detected(self) -> bool:
        """Get speech detection state (thread-safe)."""
        with self._state_lock:
            return self._is_speech_detected

    @is_speech_detected.setter
    def is_speech_detected(self, value: bool):
        """Set speech detection state (thread-safe)."""
        with self._state_lock:
            self._is_speech_detected = value

    @property
    def audio_level(self) -> float:
        """Get audio level (thread-safe)."""
        with self._state_lock:
            return self._audio_level

    @audio_level.setter
    def audio_level(self, value: float):
        """Set audio level (thread-safe)."""
        with self._state_lock:
            self._audio_level = value

    @property
    def last_voice_time(self) -> float:
        """Get last voice time (thread-safe)."""
        with self._state_lock:
            return self._last_voice_time

    @last_voice_time.setter
    def last_voice_time(self, value: float):
        """Set last voice time (thread-safe)."""
        with self._state_lock:
            self._last_voice_time = value

    @property
    def last_silence_time(self) -> float:
        """Get last silence time (thread-safe)."""
        with self._state_lock:
            return self._last_silence_time

    @last_silence_time.setter
    def last_silence_time(self, value: float):
        """Set last silence time (thread-safe)."""
        with self._state_lock:
            self._last_silence_time = value

    def _emit_signal_safely(self, signal_name: str, *args):
        """Emit a signal safely from any thread.

        This ensures signals are emitted from the main thread to avoid
        Qt threading issues.
        """
        # For simplicity, we'll emit directly since PyQt6 handles cross-thread signals
        # In a more complex scenario, you might queue signals for the main thread
        try:
            # Check if we're still running to avoid emitting after cleanup
            if not self.is_running and signal_name != "error_occurred":
                return

            signal = getattr(self, signal_name, None)
            if signal:
                signal.emit(*args)
        except RuntimeError:
            # Object has been deleted, ignore the signal
            pass

    def set_sensitivity(self, sensitivity: float):
        """Set VAD sensitivity (0.0-3.0, higher = more sensitive)."""
        if 0.0 <= sensitivity <= 3.0:
            self.sensitivity = sensitivity

            # For WebRTC VAD, use the integer part as the mode
            if not self.use_simple_vad and self.vad:
                webrtc_mode = min(3, int(sensitivity))
                self.vad.set_mode(webrtc_mode)

            # Set threshold based on floating-point sensitivity
            # Higher sensitivity = lower threshold (more sensitive to quiet sounds)
            # Map 0.0-3.0 to 0.025-0.005 threshold range
            max_threshold = 0.025
            min_threshold = 0.005
            threshold_range = max_threshold - min_threshold

            # Invert sensitivity so higher values = lower thresholds
            normalized_sensitivity = sensitivity / 3.0
            self.voice_threshold = max_threshold - (
                normalized_sensitivity * threshold_range
            )

    def set_timing(self, start_delay: float, stop_delay: float):
        """Set voice start/stop timing delays."""
        self.start_delay = start_delay
        self.stop_delay = stop_delay

    def start_detection(self):
        """Start voice activity detection."""
        if self.is_running:
            return

        try:
            self.is_running = True
            self.is_speaking = False
            self.last_voice_time = 0
            self.last_silence_time = time.time()

            # Start audio stream
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.frame_size,
                callback=self._audio_callback,
            )
            self.audio_stream.start()

            # Emit signal to indicate microphone is ready
            self._emit_signal_safely("microphone_ready")

            # Start processing thread
            self.audio_thread = threading.Thread(
                target=self._process_audio, daemon=True
            )
            self.audio_thread.start()

        except Exception as e:
            self._emit_signal_safely(
                "error_occurred", f"Failed to start voice detection: {str(e)}"
            )
            self.stop_detection()

    def stop_detection(self):
        """Stop voice activity detection (thread-safe)."""
        # Set running to False to signal threads to stop
        self.is_running = False

        # Stop audio stream first to prevent new audio callbacks
        if self.audio_stream:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
            except Exception:
                pass  # Ignore errors during cleanup
            self.audio_stream = None

        # Clear audio buffer to unblock processing thread
        with self._buffer_lock:
            self._audio_buffer = np.array([], dtype=np.float32)

        # Wait for thread to finish with a longer timeout
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)
            if self.audio_thread.is_alive():
                # Thread didn't stop cleanly, but since it's a daemon thread
                # it will be forcefully terminated when the process exits
                import logging

                logging.warning("Audio processing thread did not stop cleanly")
            self.audio_thread = None

        # Reset state (thread-safe)
        with self._state_lock:
            was_speaking = self._is_speaking
            was_speech_detected = self._is_speech_detected
            self._is_speaking = False
            self._is_speech_detected = False

        # Emit final signals if needed
        if was_speaking:
            self._emit_signal_safely("voice_stopped")
        if was_speech_detected:
            self._emit_signal_safely("speech_detected", False)

        # Clear audio buffer
        with self._buffer_lock:
            self._audio_buffer = np.array([], dtype=np.float32)

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio input stream."""
        if status:
            print(f"Audio callback status: {status}")

        # Add audio data to buffer (thread-safe)
        audio_data = indata[:, 0]  # Get mono channel
        with self._buffer_lock:
            self._audio_buffer = np.append(self._audio_buffer, audio_data)

    def _process_audio(self):
        """Process audio data in a separate thread."""
        while self.is_running:
            try:
                # Check if we have enough data for processing (thread-safe)
                with self._buffer_lock:
                    buffer_length = len(self._audio_buffer)

                if buffer_length >= self.frame_size:
                    # Extract frame for processing (thread-safe)
                    with self._buffer_lock:
                        frame_data = self._audio_buffer[: self.frame_size].copy()
                        self._audio_buffer = self._audio_buffer[self.frame_size :]

                    # Calculate audio level (RMS)
                    self.audio_level = float(np.sqrt(np.mean(frame_data**2)))
                    self._emit_signal_safely("voice_level_changed", self.audio_level)

                    # Determine if speech is detected using hybrid approach
                    if self.use_simple_vad:
                        # Pure threshold-based detection
                        is_speech = self.audio_level > self.voice_threshold
                    else:
                        # Combined WebRTC VAD + threshold for fine-grained control
                        pcm_data = (frame_data * 32767).astype(np.int16)
                        webrtc_speech = self.vad.is_speech(
                            pcm_data.tobytes(), self.sample_rate
                        )
                        threshold_speech = self.audio_level > self.voice_threshold

                        # Speech detected if BOTH WebRTC and threshold agree
                        # This provides more accurate detection with fine-grained control
                        is_speech = webrtc_speech and threshold_speech

                    # Emit speech detection signal if state changed
                    if is_speech != self.is_speech_detected:
                        self.is_speech_detected = is_speech
                        self._emit_signal_safely("speech_detected", is_speech)

                    current_time = time.time()

                    if is_speech:
                        self.last_voice_time = current_time

                        # Check if we should start speaking
                        if (
                            not self.is_speaking
                            and current_time - self.last_silence_time
                            >= self.start_delay
                        ):
                            self.is_speaking = True
                            self._emit_signal_safely("voice_started")
                    else:
                        self.last_silence_time = current_time

                        # Check if we should stop speaking
                        if (
                            self.is_speaking
                            and current_time - self.last_voice_time >= self.stop_delay
                        ):
                            self.is_speaking = False
                            self._emit_signal_safely("voice_stopped")
                else:
                    # Not enough data, wait a bit
                    time.sleep(0.01)

            except Exception as e:
                self._emit_signal_safely(
                    "error_occurred", f"Audio processing error: {str(e)}"
                )
                break

    def get_audio_devices(self):
        """Get list of available audio input devices."""
        try:
            devices = sd.query_devices()
            input_devices = []
            for i, device in enumerate(devices):
                if device["max_input_channels"] > 0:
                    input_devices.append(
                        {
                            "index": i,
                            "name": device["name"],
                            "channels": device["max_input_channels"],
                            "default_samplerate": device["default_samplerate"],
                        }
                    )
            return input_devices
        except Exception as e:
            self._emit_signal_safely(
                "error_occurred", f"Failed to get audio devices: {str(e)}"
            )
            return []

    def set_audio_device(self, device_index: int | None):
        """Set the audio input device."""
        try:
            if device_index is not None:
                sd.default.device[0] = device_index  # Set input device
        except Exception as e:
            self._emit_signal_safely(
                "error_occurred", f"Failed to set audio device: {str(e)}"
            )

    def is_detection_running(self) -> bool:
        """Check if voice detection is currently running."""
        return self.is_running

    def get_current_level(self) -> float:
        """Get current audio level (0.0 to 1.0)."""
        return self.audio_level
