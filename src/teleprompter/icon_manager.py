"""Modern icon management for the teleprompter application."""

import base64
from pathlib import Path

from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer


class IconManager:
    """Manages SVG icons with modern UI design principles."""

    # Standard icon sizes for different UI contexts
    SIZES = {
        "small": (12, 12),  # Spinbox arrows, small buttons
        "medium": (16, 16),  # Toolbar buttons, standard controls
        "large": (20, 20),  # Main action buttons
        "xlarge": (24, 24),  # Primary actions, headers
    }

    # Modern color palette for different states
    COLORS = {
        "default": "#c0c0c0",  # Default icon color
        "hover": "#ffffff",  # Hover state
        "active": "#0078d4",  # Active/selected state
        "disabled": "#666666",  # Disabled state
        "accent": "#0078d4",  # Accent color (Microsoft blue)
        "success": "#107c10",  # Success state
        "warning": "#ff8c00",  # Warning state
        "error": "#d13438",  # Error state
    }

    def __init__(self):
        """Initialize the icon manager with modern defaults."""
        self.icons_dir = Path(__file__).parent / "icons"
        self._icon_cache = {}

    def get_svg_content(self, icon_name: str) -> str:
        """Get the raw SVG content for an icon.

        Args:
            icon_name: Name of the icon (without .svg extension)

        Returns:
            SVG content as string, or empty string if not found
        """
        svg_path = self.icons_dir / f"{icon_name}.svg"
        if svg_path.exists():
            return svg_path.read_text(encoding="utf-8")
        return ""

    def get_svg_data_url(self, icon_name: str, color: str = "currentColor") -> str:
        """Get a data URL for an SVG icon with optional color replacement.

        Args:
            icon_name: Name of the icon (without .svg extension)
            color: Color to replace 'currentColor' with (default: currentColor)

        Returns:
            Data URL string for use in CSS, or empty string if not found
        """
        svg_content = self.get_svg_content(icon_name)
        if not svg_content:
            return ""

        # Replace currentColor with the specified color
        if color != "currentColor":
            svg_content = svg_content.replace(
                'stroke="currentColor"', f'stroke="{color}"'
            )

        # Encode for data URL
        svg_bytes = svg_content.encode("utf-8")
        svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")

        return f"data:image/svg+xml;base64,{svg_base64}"

    def get_pixmap(
        self,
        icon_name: str,
        size: tuple[int, int] | None = None,
        color: str | None = None,
        size_key: str | None = None,
    ) -> QPixmap:
        """Get a QPixmap for an icon with modern sizing and theming.

        Args:
            icon_name: Name of the icon (without .svg extension)
            size: Tuple of (width, height) for the pixmap (overrides size_key)
            color: Color for the icon (overrides color_key)
            size_key: Predefined size key ('small', 'medium', 'large', 'xlarge')

        Returns:
            QPixmap object, or empty QPixmap if not found
        """
        # Resolve size and color
        if size is None:
            size = self.SIZES.get(size_key or "medium", self.SIZES["medium"])

        if color is None:
            color = self.COLORS["default"]

        cache_key = f"{icon_name}_{size[0]}x{size[1]}_{color}"

        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        svg_content = self.get_svg_content(icon_name)
        if not svg_content:
            return QPixmap()

        # Replace currentColor with the specified color
        svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
        # Also handle fill for icons that use fill instead of stroke
        svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')

        # Create QSvgRenderer and render to QPixmap
        renderer = QSvgRenderer()
        svg_bytes = QByteArray(svg_content.encode("utf-8"))

        if not renderer.load(svg_bytes):
            return QPixmap()

        # Use high DPI scaling for crisp icons
        pixmap = QPixmap(size[0], size[1])
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        renderer.render(painter)
        painter.end()

        self._icon_cache[cache_key] = pixmap
        return pixmap

    def get_themed_pixmap(
        self, icon_name: str, state: str = "default", size_key: str = "medium"
    ) -> QPixmap:
        """Get a pixmap with predefined theming for different UI states.

        Args:
            icon_name: Name of the icon (without .svg extension)
            state: UI state ('default', 'hover', 'active', 'disabled', etc.)
            size_key: Size category ('small', 'medium', 'large', 'xlarge')

        Returns:
            QPixmap object with appropriate theming
        """
        color = self.COLORS.get(state, self.COLORS["default"])
        size = self.SIZES.get(size_key, self.SIZES["medium"])

        return self.get_pixmap(icon_name, size, color)

    def clear_cache(self):
        """Clear the icon cache to free memory."""
        self._icon_cache.clear()


# Global icon manager instance
icon_manager = IconManager()
