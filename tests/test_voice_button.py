#!/usr/bin/env python3
"""Test script to demonstrate consolidated voice button functionality."""

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
            if is_speech:
                print("🟢 SPEECH DETECTED - Button should be GREEN")
            else:
                print("🟠 LISTENING - Button should be ORANGE")


def test_voice_button_states():
    """Test the consolidated voice button states."""
    print("Testing consolidated voice button functionality...")
    print("Button color states:")
    print("  🔘 Gray: Voice detection disabled")
    print("  🟠 Orange: Voice detection enabled, listening")
    print("  🟢 Green: Voice detection enabled, speech detected")
    print("  🔴 Red: Voice detection error")
    print("\nPress Ctrl+C to exit.\n")

    # Create voice detector
    detector = VoiceActivityDetector()

    # Create test listener
    listener = TestListener()

    # Connect signals
    detector.speech_detected.connect(listener.on_speech_detected)

    try:
        # Start detection
        detector.start_detection()
        print(f"🟠 Voice detection started - Button should be ORANGE")
        print(f"Sensitivity: {detector.sensitivity:.1f}")
        print(f"Voice threshold: {detector.voice_threshold:.4f}")
        print("Speak to see the button change to GREEN...\n")

        # Keep running
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🔘 Stopping voice detection - Button should turn GRAY")
        detector.stop_detection()
        print("Test completed!")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    test_voice_button_states()
