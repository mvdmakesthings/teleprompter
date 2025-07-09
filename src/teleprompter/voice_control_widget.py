"""Voice control widget for teleprompter."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from . import config
from .voice_detector import VoiceActivityDetector


class VoiceControlWidget(QWidget):
    """Widget for voice activity detection controls."""

    # Signals
    voice_detection_enabled = pyqtSignal(bool)
    sensitivity_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize the voice control widget."""
        super().__init__(parent)

        # Voice detector instance
        self.voice_detector = VoiceActivityDetector(self)
        self.voice_detector.voice_level_changed.connect(self._update_level_meter)
        self.voice_detector.error_occurred.connect(self._handle_error)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Enable voice detection checkbox
        self.enable_checkbox = QCheckBox("Enable Voice Detection")
        self.enable_checkbox.setChecked(config.VAD_ENABLED_DEFAULT)
        self.enable_checkbox.toggled.connect(self._on_enable_toggled)
        layout.addWidget(self.enable_checkbox)

        # Sensitivity control
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Sensitivity:"))

        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(0)
        self.sensitivity_slider.setMaximum(3)
        self.sensitivity_slider.setValue(config.VAD_SENSITIVITY)
        self.sensitivity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sensitivity_slider.setTickInterval(1)
        self.sensitivity_slider.valueChanged.connect(self._on_sensitivity_changed)
        sensitivity_layout.addWidget(self.sensitivity_slider)

        self.sensitivity_label = QLabel(str(config.VAD_SENSITIVITY))
        sensitivity_layout.addWidget(self.sensitivity_label)

        layout.addLayout(sensitivity_layout)

        # Audio device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Microphone:"))

        self.device_combo = QComboBox()
        self._populate_audio_devices()
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        device_layout.addWidget(self.device_combo)

        layout.addLayout(device_layout)

        # Audio level meter
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Audio Level:"))

        self.level_meter = QProgressBar()
        self.level_meter.setRange(0, 100)
        self.level_meter.setValue(0)
        self.level_meter.setTextVisible(False)
        level_layout.addWidget(self.level_meter)

        layout.addLayout(level_layout)

        # Status label
        self.status_label = QLabel("Voice detection disabled")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

    def _populate_audio_devices(self):
        """Populate the audio device combo box."""
        devices = self.voice_detector.get_audio_devices()
        self.device_combo.clear()

        if not devices:
            self.device_combo.addItem("No audio devices found")
            self.device_combo.setEnabled(False)
            return

        self.device_combo.setEnabled(True)
        for device in devices:
            self.device_combo.addItem(
                f"{device['name']} ({device['channels']} ch)", device["index"]
            )

    def _on_enable_toggled(self, enabled: bool):
        """Handle voice detection enable/disable."""
        if enabled:
            self.voice_detector.start_detection()
            self.status_label.setText("Voice detection active")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.voice_detector.stop_detection()
            self.status_label.setText("Voice detection disabled")
            self.status_label.setStyleSheet("color: gray;")
            self.level_meter.setValue(0)

        # Enable/disable controls
        self.sensitivity_slider.setEnabled(enabled)
        self.device_combo.setEnabled(enabled and self.device_combo.count() > 0)

        self.voice_detection_enabled.emit(enabled)

    def _on_sensitivity_changed(self, value: int):
        """Handle sensitivity slider change."""
        self.sensitivity_label.setText(str(value))
        self.voice_detector.set_sensitivity(value)
        self.sensitivity_changed.emit(value)

    def _on_device_changed(self, index: int):
        """Handle audio device selection change."""
        if index >= 0:
            device_index = self.device_combo.itemData(index)
            if device_index is not None:
                self.voice_detector.set_audio_device(device_index)

    def _update_level_meter(self, level: float):
        """Update the audio level meter."""
        # Convert level to percentage (0-100)
        percentage = min(100, int(level * 1000))  # Scale up for visibility
        self.level_meter.setValue(percentage)

    def _handle_error(self, error_message: str):
        """Handle voice detector errors."""
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("color: red;")

        # Disable voice detection on error
        self.enable_checkbox.setChecked(False)

    def get_voice_detector(self) -> VoiceActivityDetector:
        """Get the voice detector instance."""
        return self.voice_detector

    def is_voice_detection_enabled(self) -> bool:
        """Check if voice detection is enabled."""
        return self.enable_checkbox.isChecked()

    def set_voice_detection_enabled(self, enabled: bool):
        """Enable or disable voice detection."""
        self.enable_checkbox.setChecked(enabled)

    def get_current_sensitivity(self) -> int:
        """Get current sensitivity setting."""
        return self.sensitivity_slider.value()

    def set_sensitivity(self, sensitivity: int):
        """Set sensitivity value."""
        if 0 <= sensitivity <= 3:
            self.sensitivity_slider.setValue(sensitivity)
