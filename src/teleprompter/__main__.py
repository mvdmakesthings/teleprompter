#!/usr/bin/env python3
"""Entry point for the teleprompter application."""

import sys
import warnings

from PyQt6.QtWidgets import QApplication

from .core.container import configure_container, get_container
from .utils.logging import setup_logging
from .ui.app import TeleprompterApp

# Suppress pkg_resources deprecation warning from webrtcvad before any imports
warnings.filterwarnings(
    "ignore", message="pkg_resources is deprecated", category=UserWarning
)


def main():
    """Run the teleprompter application."""
    # Set up logging first
    setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("CueBird")

    # Configure dependency injection container
    configure_container()

    # Create and show main window
    container = get_container()
    window = TeleprompterApp(container)
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
