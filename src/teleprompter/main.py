#!/usr/bin/env python3
"""Entry point for the teleprompter application."""

import sys
import warnings

# Suppress pkg_resources deprecation warning from webrtcvad before any imports
warnings.filterwarnings(
    "ignore", message="pkg_resources is deprecated", category=UserWarning
)

from PyQt6.QtWidgets import QApplication

from .app import TeleprompterApp


def main():
    """Run the teleprompter application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Teleprompter")

    # Create and show main window
    window = TeleprompterApp()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
