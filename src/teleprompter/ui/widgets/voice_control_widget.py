"""Voice control widget for teleprompter."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSlider,
    QWidget,
)

from ...core import config
from ...domain.voice.detector import VoiceActivityDetector
from ..managers.style_manager import StyleManager


class VoiceControlWidget(QWidget):
    """Compact voice control widget for toolbar integration.

    This widget provides voice activity detection controls in a compact format
    suitable for integration into toolbars. It includes a voice detection toggle
    button, sensitivity slider, and microphone selection dropdown.

    The widget provides visual feedback through button color changes:
    - Gray: Voice detection disabled
    - Blue: Listening for speech (voice detection active)
    - Green: Speech currently detected
    - Red: Error state (microphone access failed)

    Signals:
        voice_detection_enabled (bool): Emitted when voice detection is toggled.
        sensitivity_changed (float): Emitted when sensitivity level changes.

    Attributes:
        voice_detector: VoiceActivityDetector instance for audio processing.
        voice_button: Toggle button for enabling/disabling voice detection.
        sensitivity_slider: Slider for adjusting detection sensitivity (0.0-3.0).
        device_combo: ComboBox for selecting audio input device.
    """

    # Signals
    voice_detection_enabled = pyqtSignal(bool)
    sensitivity_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        """Initialize the voice control widget.

        Args:
            parent: Parent widget, typically the main toolbar.

        Note:
            The widget automatically populates available audio devices
            and applies application styling on initialization.
        """
        super().__init__(parent)

        # Voice detector instance
        self.voice_detector = VoiceActivityDetector(self)
        self.voice_detector.voice_level_changed.connect(self._update_voice_level)
        self.voice_detector.speech_detected.connect(self._on_speech_detected)
        self.voice_detector.error_occurred.connect(self._handle_error)
        self.voice_detector.microphone_ready.connect(self._on_microphone_ready)

        # Internal state
        self._current_level = 0.0
        self._is_speaking = False
        self._is_loading = False

        self._setup_ui()

    def _setup_ui(self):
        """Set up the modern, compact user interface.

        Creates and configures the voice control UI components including:
        - Voice detection toggle button with visual state indicators
        - Sensitivity adjustment slider (0.0-3.0 range)
        - Audio device selection dropdown
        - Proper layout and sizing for toolbar integration

        Note:
            All components are styled to match the application theme
            and sized appropriately for compact toolbar display.
        """
        # Use horizontal layout for toolbar integration
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(4)

        self.voice_button = QPushButton("🎤")
        self.voice_button.setCheckable(True)
        self.voice_button.setChecked(config.VAD_ENABLED_DEFAULT)
        self.voice_button.setToolTip(
            "🎤 Voice Detection\n"
            + "• Gray: Disabled\n"
            + "• Blue: Listening for speech\n"
            + "• Green: Speech detected"
        )
        self.voice_button.setObjectName("voiceButton")
        self.voice_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.voice_button.toggled.connect(self._on_voice_toggled)
        layout.addWidget(self.voice_button)

        # Sensitivity slider with modern styling
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(0)
        self.sensitivity_slider.setMaximum(30)  # 0-30 for 0.0-3.0 in 0.1 increments
        self.sensitivity_slider.setValue(
            int(config.VAD_SENSITIVITY * 10)
        )  # Convert float to int
        self.sensitivity_slider.setFixedWidth(60)
        self.sensitivity_slider.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.sensitivity_slider.valueChanged.connect(self._on_sensitivity_changed)
        self.sensitivity_slider.setObjectName("sensitivitySlider")
        self._update_sensitivity_tooltip()
        layout.addWidget(self.sensitivity_slider)

        # Audio device selection with modern styling
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(150)
        self.device_combo.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        self.device_combo.setToolTip("Select microphone")
        self.device_combo.setObjectName("deviceCombo")
        self._populate_audio_devices()
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        layout.addWidget(self.device_combo)

        # Apply modern styling
        self._apply_modern_styling()

        # Initialize state
        self._update_voice_button_style()
        self._on_voice_toggled(self.voice_button.isChecked())

    def _apply_modern_styling(self):
        """Apply minimal flat styling to match the main application theme.

        Applies consistent styling from StyleManager to ensure the voice
        control widget integrates seamlessly with the application's
        visual design language.
        """
        self.setStyleSheet(StyleManager().get_voice_control_stylesheet())

    def _populate_audio_devices(self):
        """Populate the audio device combo box with available microphones.

        Queries the voice detector for available audio input devices and
        populates the dropdown. If no devices are found, displays an
        appropriate message and disables the control.

        Note:
            This method is called during initialization and when the
            device list needs to be refreshed.
        """
        devices = self.voice_detector.get_audio_devices()
        self.device_combo.clear()

        if not devices:
            self.device_combo.addItem("No microphones")
            self.device_combo.setEnabled(False)
            return

        self.device_combo.setEnabled(True)
        for device in devices:
            # Use full device name without truncation
            name = device["name"]
            self.device_combo.addItem(name, device["index"])

    def _on_voice_toggled(self, enabled: bool):
        """Handle voice detection toggle button state changes.

        Args:
            enabled: True if voice detection should be enabled, False to disable.

        Note:
            When enabling, the widget enters a loading state while requesting
            microphone access. Controls are enabled/disabled appropriately
            based on the state and device availability.
        """
        if enabled:
            # Show loading state immediately
            self._is_loading = True
            self._update_voice_button_style()

            # Change button text to indicate loading
            self.voice_button.setText("⏳")
            self.voice_button.setToolTip("Requesting microphone access...")

            self.voice_detector.start_detection()
        else:
            self.voice_detector.stop_detection()
            # Reset speaking state when disabled
            self._is_speaking = False
            self._is_loading = False

        # Enable/disable controls
        self.sensitivity_slider.setEnabled(enabled)
        self.device_combo.setEnabled(self.device_combo.count() > 0)

        if not enabled:
            self._update_voice_button_style()
        self.voice_detection_enabled.emit(enabled)

    def _update_voice_button_style(self):
        """Update the voice button appearance based on state and activity.

        Updates the button's visual appearance to reflect current state:
        - Gray: Voice detection disabled
        - Loading: Hourglass emoji while requesting microphone access
        - Blue: Listening for speech (detection active but no speech)
        - Green: Speech currently detected
        - Red: Error state (microphone access failed)

        The styling provides immediate visual feedback to users about
        the current voice detection status.
        """
        if not self.voice_button.isChecked():
            # Disabled state - darker gray with flat styling
            self.voice_button.setText("🎤")
            self.voice_button.setStyleSheet(
                StyleManager().get_voice_button_disabled_stylesheet()
            )
        elif self._is_loading:
            # Loading state - waiting for microphone access
            self.voice_button.setStyleSheet(
                StyleManager().get_stylesheet("voice_button_loading")
            )
        elif self._is_speaking:
            # Active and speaking - green with flat styling
            self.voice_button.setText("🎤")
            self.voice_button.setStyleSheet(
                StyleManager().get_voice_button_speaking_stylesheet()
            )
        else:
            # Active but listening (no speech) - blue with flat styling
            self.voice_button.setText("🎤")
            self.voice_button.setStyleSheet(
                StyleManager().get_voice_button_listening_stylesheet()
            )

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
            self._update_voice_button_style()  # Update button color based on speech state

    def _handle_error(self, error_message: str):
        """Handle voice detector errors."""
        # Reset loading state
        self._is_loading = False

        # Show error by setting button to red with flat styling and updating tooltip
        self.voice_button.setStyleSheet(
            StyleManager().get_voice_button_error_stylesheet()
        )
        self.voice_button.setToolTip(f"Voice detection error: {error_message}")

        # Disable voice detection on error
        self.voice_button.setChecked(False)

    def _on_microphone_ready(self):
        """Handle microphone ready signal."""
        # Clear loading state
        self._is_loading = False

        # Update button appearance
        self._update_voice_button_style()

        # Update tooltip
        self.voice_button.setToolTip(
            "🎤 Voice Detection\n"
            + "• Gray: Disabled\n"
            + "• Blue: Listening for speech\n"
            + "• Green: Speech detected"
        )

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

    def cleanup(self):
        """Clean up voice detector resources before closing."""
        if self.voice_detector and self.voice_detector.is_detection_running():
            self.voice_detector.stop_detection()
