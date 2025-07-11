"""Resource path utilities for handling bundled resources in PyInstaller builds."""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller bundle.
    
    Args:
        relative_path: Path relative to the application root
        
    Returns:
        Absolute path to the resource
    """
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    # Development mode - get path relative to this file
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)


def is_bundled() -> bool:
    """Check if we're running in a PyInstaller bundle.
    
    Returns:
        True if running as a bundled application, False otherwise
    """
    return hasattr(sys, '_MEIPASS')
