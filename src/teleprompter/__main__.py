#!/usr/bin/env python3
"""Entry point for the teleprompter backend server.

This entry point starts the FastAPI backend server.
The UI is now handled by the Electron application.
"""

import warnings

# Suppress pkg_resources deprecation warning from webrtcvad before any imports
warnings.filterwarnings(
    "ignore", message="pkg_resources is deprecated", category=UserWarning
)

from .backend.main import main


if __name__ == "__main__":
    main()
