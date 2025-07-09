#!/usr/bin/env python3
"""Test script to demonstrate improved speech detection indicator."""

import os
import sys
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PyQt6.QtCore import QObject

from teleprompter.voice_detector import VoiceActivityDetector


class TestListener(QObject):
    """Test listener for voice detector signals."""

    def __init__(self):
        super().__init__()
        self.speech_state = False

    def on_speech_detected(self, is_speech):
        """Handle speech detection state changes."""
        if is_speech != self.speech_state:
            self.speech_state = is_speech
            status = "SPEECH DETECTED" if is_speech else "SILENCE"
            print(f"🔊 {status}")

    def on_voice_level(self, level):
        """Handle voice level updates."""
        # Only print level updates occasionally to reduce spam
        pass


def test_speech_detection():
    """Test improved speech detection."""
    print("Testing improved speech detection...")
    print(
        "The indicator should now only change when actual speech threshold is reached."
    )
    print("Background noise should NOT trigger the speech indicator.")
    print("Press Ctrl+C to exit.\n")

    # Create voice detector
    detector = VoiceActivityDetector()

    # Create test listener
    listener = TestListener()

    # Connect signals
    detector.speech_detected.connect(listener.on_speech_detected)
    detector.voice_level_changed.connect(listener.on_voice_level)

    try:
        # Start detection
        detector.start_detection()
        print(f"Voice detection started with sensitivity: {detector.sensitivity:.1f}")
        print(f"Voice threshold: {detector.voice_threshold:.4f}")
        print("Listening... (speak to test)\n")

        # Keep running
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping voice detection...")
        detector.stop_detection()
        print("Test completed!")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    test_speech_detection()
