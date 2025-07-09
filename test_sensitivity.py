#!/usr/bin/env python3
"""Test script to verify fine-grained sensitivity control."""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from teleprompter.voice_detector import VoiceActivityDetector
from teleprompter.config import VAD_SENSITIVITY

def test_sensitivity():
    """Test floating-point sensitivity values."""
    print("Testing fine-grained sensitivity control...")
    
    # Create voice detector
    detector = VoiceActivityDetector()
    
    # Test various sensitivity values
    test_values = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    
    for sensitivity in test_values:
        print(f"Setting sensitivity to {sensitivity:.1f}")
        detector.set_sensitivity(sensitivity)
        
        # Check that the threshold was updated appropriately
        print(f"  Voice threshold: {detector.voice_threshold:.4f}")
        
        # For WebRTC mode, just confirm it's being used
        if not detector.use_simple_vad and detector.vad:
            print(f"  Using WebRTC VAD with threshold control")
        else:
            print(f"  Using simple threshold-based VAD")
        
        print()
    
    print(f"Default sensitivity from config: {VAD_SENSITIVITY}")
    print("Fine-grained sensitivity control test completed!")

if __name__ == "__main__":
    test_sensitivity()
