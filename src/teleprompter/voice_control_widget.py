"""Voice control widget for teleprompter."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QWidget,
)

from . import config
from .voice_detector import VoiceActivityDetector


class VoiceControlWidget(QWidget):
    """Compact voice control widget for toolbar integration."""

    # Signals
    voice_detection_enabled = pyqtSignal(bool)
    sensitivity_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        """Initialize the voice control widget."""
        super().__init__(parent)

        # Voice detector instance
        self.voice_detector = VoiceActivityDetector(self)
        self.voice_detector.voice_level_changed.connect(self._update_voice_level)
        self.voice_detector.speech_detected.connect(self._on_speech_detected)
        self.voice_detector.error_occurred.connect(self._handle_error)

        # Internal state
        self._current_level = 0.0
        self._is_speaking = False

        self._setup_ui()

    def _setup_ui(self):
        """Set up the compact user interface."""
        # Use horizontal layout for toolbar integration
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(8)

        # Voice detection toggle button with indicator
        self.voice_button = QPushButton("🎤")
        self.voice_button.setCheckable(True)
        self.voice_button.setChecked(config.VAD_ENABLED_DEFAULT)
        self.voice_button.setToolTip("Toggle voice detection")
        self.voice_button.setFixedSize(30, 26)
        self.voice_button.toggled.connect(self._on_voice_toggled)
        layout.addWidget(self.voice_button)

        # Compact sensitivity control
        layout.addWidget(QLabel("Sens:"))
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(0)
        self.sensitivity_slider.setMaximum(30)  # 0-30 for 0.0-3.0 in 0.1 increments
        self.sensitivity_slider.setValue(
            int(config.VAD_SENSITIVITY * 10)
        )  # Convert float to int
        self.sensitivity_slider.setFixedWidth(60)
        self.sensitivity_slider.valueChanged.connect(self._on_sensitivity_changed)
        self._update_sensitivity_tooltip()
        layout.addWidget(self.sensitivity_slider)

        # Audio device selection (compact)
        self.device_combo = QComboBox()
        self.device_combo.setFixedWidth(120)
        self.device_combo.setToolTip("Select microphone")
        self._populate_audio_devices()
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        layout.addWidget(self.device_combo)

        # Visual voice activity indicator
        self.activity_indicator = QLabel("●")
        self.activity_indicator.setFixedSize(20, 26)
        self.activity_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.activity_indicator.setStyleSheet("color: gray; font-size: 12px;")
        self.activity_indicator.setToolTip("Voice activity indicator")
        layout.addWidget(self.activity_indicator)

        # Initialize state
        self._update_voice_button_style()
        self._on_voice_toggled(self.voice_button.isChecked())

    def _populate_audio_devices(self):
        """Populate the audio device combo box."""
        devices = self.voice_detector.get_audio_devices()
        self.device_combo.clear()

        if not devices:
            self.device_combo.addItem("No microphones")
            self.device_combo.setEnabled(False)
            return

        self.device_combo.setEnabled(True)
        for device in devices:
            # Truncate long device names for compact display
            name = device["name"]
            if len(name) > 15:
                name = name[:12] + "..."
            self.device_combo.addItem(name, device["index"])

    def _on_voice_toggled(self, enabled: bool):
        """Handle voice detection toggle."""
        if enabled:
            self.voice_detector.start_detection()
        else:
            self.voice_detector.stop_detection()
            self._update_activity_indicator(False)

        # Enable/disable controls
        self.sensitivity_slider.setEnabled(enabled)
        self.device_combo.setEnabled(enabled and self.device_combo.count() > 0)

        self._update_voice_button_style()
        self.voice_detection_enabled.emit(enabled)

    def _update_voice_button_style(self):
        """Update the voice button appearance based on state."""
        if self.voice_button.isChecked():
            # Active state - green background
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: 1px solid #45a049;
                    border-radius: 4px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
        else:
            # Inactive state - default appearance
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)

    def _on_sensitivity_changed(self, value: int):
        """Handle sensitivity slider change."""
        # Convert integer slider value to float (0-30 -> 0.0-3.0)
        sensitivity = value / 10.0
        self.voice_detector.set_sensitivity(sensitivity)
        self._update_sensitivity_tooltip()
        self.sensitivity_changed.emit(sensitivity)

    def _update_sensitivity_tooltip(self):
        """Update the sensitivity slider tooltip with current value."""
        current_value = self.sensitivity_slider.value() / 10.0
        self.sensitivity_slider.setToolTip(
            f"Voice detection sensitivity: {current_value:.1f}"
        )

    def _on_device_changed(self, index: int):
        """Handle audio device selection change."""
        if index >= 0:
            device_index = self.device_combo.itemData(index)
            if device_index is not None:
                self.voice_detector.set_audio_device(device_index)

    def _update_voice_level(self, level: float):
        """Update voice level (for potential future use)."""
        self._current_level = level

    def _on_speech_detected(self, is_speech: bool):
        """Handle speech detection state changes from the voice detector."""
        if is_speech != self._is_speaking:
            self._is_speaking = is_speech
            self._update_activity_indicator(is_speech)

    def _update_activity_indicator(self, is_active: bool):
        """Update the visual activity indicator."""
        if not self.voice_button.isChecked():
            # Voice detection disabled
            self.activity_indicator.setStyleSheet("color: gray; font-size: 12px;")
            return

        if is_active:
            # Speaking detected
            self.activity_indicator.setStyleSheet(
                "color: #4CAF50; font-size: 12px; font-weight: bold;"
            )
        else:
            # Silent
            self.activity_indicator.setStyleSheet("color: #FFA500; font-size: 12px;")

    def _handle_error(self, error_message: str):
        """Handle voice detector errors."""
        # Show error state in activity indicator
        self.activity_indicator.setStyleSheet("color: red; font-size: 12px;")
        self.activity_indicator.setToolTip(f"Error: {error_message}")

        # Disable voice detection on error
        self.voice_button.setChecked(False)

    # Public interface methods
    def get_voice_detector(self) -> VoiceActivityDetector:
        """Get the voice detector instance."""
        return self.voice_detector

    def is_voice_detection_enabled(self) -> bool:
        """Check if voice detection is enabled."""
        return self.voice_button.isChecked()

    def set_voice_detection_enabled(self, enabled: bool):
        """Enable or disable voice detection."""
        self.voice_button.setChecked(enabled)

    def get_current_sensitivity(self) -> float:
        """Get current sensitivity setting."""
        return self.sensitivity_slider.value() / 10.0

    def set_sensitivity(self, sensitivity: float):
        """Set sensitivity value."""
        if 0.0 <= sensitivity <= 3.0:
            self.sensitivity_slider.setValue(int(sensitivity * 10))
