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

from . import config


class VoiceActivityDetector(QObject):
    """Voice activity detector using WebRTC VAD."""

    # Signals for voice activity events
    voice_started = pyqtSignal()
    voice_stopped = pyqtSignal()
    voice_level_changed = pyqtSignal(float)  # Audio level (0.0 to 1.0)
    error_occurred = pyqtSignal(str)

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

        # State tracking
        self.is_running = False
        self.is_speaking = False
        self.last_voice_time = 0
        self.last_silence_time = 0
        self.audio_level = 0.0

        # Threading
        self.audio_thread: threading.Thread | None = None
        self.audio_stream: sd.InputStream | None = None

        # Audio buffer
        self.audio_buffer = np.array([], dtype=np.float32)

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

            # Start processing thread
            self.audio_thread = threading.Thread(
                target=self._process_audio, daemon=True
            )
            self.audio_thread.start()

        except Exception as e:
            self.error_occurred.emit(f"Failed to start voice detection: {str(e)}")
            self.stop_detection()

    def stop_detection(self):
        """Stop voice activity detection."""
        self.is_running = False

        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None

        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
            self.audio_thread = None

        # Reset state
        if self.is_speaking:
            self.is_speaking = False
            self.voice_stopped.emit()

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio input stream."""
        if status:
            print(f"Audio callback status: {status}")

        # Add audio data to buffer
        audio_data = indata[:, 0]  # Get mono channel
        self.audio_buffer = np.append(self.audio_buffer, audio_data)

    def _process_audio(self):
        """Process audio data in a separate thread."""
        while self.is_running:
            try:
                # Check if we have enough data for processing
                if len(self.audio_buffer) >= self.frame_size:
                    # Extract frame for processing
                    frame_data = self.audio_buffer[: self.frame_size]
                    self.audio_buffer = self.audio_buffer[self.frame_size :]

                    # Calculate audio level (RMS)
                    self.audio_level = float(np.sqrt(np.mean(frame_data**2)))
                    self.voice_level_changed.emit(self.audio_level)

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
                            self.voice_started.emit()
                    else:
                        self.last_silence_time = current_time

                        # Check if we should stop speaking
                        if (
                            self.is_speaking
                            and current_time - self.last_voice_time >= self.stop_delay
                        ):
                            self.is_speaking = False
                            self.voice_stopped.emit()
                else:
                    # Not enough data, wait a bit
                    time.sleep(0.01)

            except Exception as e:
                self.error_occurred.emit(f"Audio processing error: {str(e)}")
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
            self.error_occurred.emit(f"Failed to get audio devices: {str(e)}")
            return []

    def set_audio_device(self, device_index: int | None):
        """Set the audio input device."""
        try:
            if device_index is not None:
                sd.default.device[0] = device_index  # Set input device
        except Exception as e:
            self.error_occurred.emit(f"Failed to set audio device: {str(e)}")

    def is_detection_running(self) -> bool:
        """Check if voice detection is currently running."""
        return self.is_running

    def get_current_level(self) -> float:
        """Get current audio level (0.0 to 1.0)."""
        return self.audio_level
