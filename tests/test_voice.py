#!/usr/bin/env python3
"""Simple test script for voice activity detection."""

import sys
import time

from PyQt6.QtWidgets import QApplication

from src.teleprompter.voice_detector import VoiceActivityDetector


def test_voice_detection():
    """Test the voice activity detector."""
    app = QApplication(sys.argv)

    # Create voice detector
    detector = VoiceActivityDetector()

    # Connect signals
    detector.voice_started.connect(lambda: print("🎤 Voice STARTED"))
    detector.voice_stopped.connect(lambda: print("🔇 Voice STOPPED"))
    detector.voice_level_changed.connect(
        lambda level: print(f"📊 Audio level: {level:.4f}")
    )
    detector.error_occurred.connect(lambda error: print(f"❌ Error: {error}"))

    print("Starting voice detection test...")
    print("Speak into your microphone to test voice activity detection.")
    print("Press Ctrl+C to exit.")

    # Start detection
    detector.start_detection()

    try:
        # Run for a while
        start_time = time.time()
        while time.time() - start_time < 30:  # Run for 30 seconds
            app.processEvents()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping test...")

    # Stop detection
    detector.stop_detection()
    print("Test completed.")


if __name__ == "__main__":
    test_voice_detection()
