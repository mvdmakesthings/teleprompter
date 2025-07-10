"""Style management for the teleprompter application."""

from . import config


class StyleManager:
    """Manages application styling and themes."""

    @staticmethod
    def get_application_stylesheet() -> str:
        """Get the complete application stylesheet.

        Returns:
            CSS stylesheet as string
        """
        return f"""
            /* Main window styling */
            QMainWindow {{
                background-color: #0f0f0f;
                color: #e0e0e0;
            }}

            /* Enhanced toolbar with Material Design styling */
            QToolBar {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(26, 26, 26, 0.95),
                    stop: 0.5 rgba(22, 22, 22, 0.9),
                    stop: 1 rgba(18, 18, 18, 0.95));
                border: none;
                border-bottom: 2px solid rgba(255, 255, 255, 0.15);
                padding: 4px 8px;
                spacing: 8px;
                font-size: 12px;
                font-weight: 500;
                min-height: 48px;
                border-radius: {config.MATERIAL_BORDER_RADIUS["small"]}px;
            }}

            QToolBar::separator {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.1),
                    stop: 0.5 rgba(255, 255, 255, 0.15),
                    stop: 1 rgba(255, 255, 255, 0.1));
                width: 1px;
                margin: 8px 6px;
                border-radius: 0.5px;
            }}

            /* Enhanced button styling with Material Design patterns */
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(42, 42, 42, 0.8),
                    stop: 1 rgba(32, 32, 32, 0.8));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {config.MATERIAL_BORDER_RADIUS["medium"]}px;
                color: #e0e0e0;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
                min-height: 32px;
            }}

            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(52, 52, 52, 0.9),
                    stop: 1 rgba(42, 42, 42, 0.9));
                border-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                border-width: 2px;
            }}

            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(22, 22, 22, 0.9),
                    stop: 1 rgba(32, 32, 32, 0.9));
                border-color: rgba(120, 120, 120, 0.3);
                border-width: 1px;
            }}

            QPushButton:disabled {{
                background: rgba(32, 32, 32, 0.3);
                border-color: rgba(255, 255, 255, 0.05);
                color: #666666;
            }}

            /* Primary action button (Play button) with Material colors */
            QPushButton#playButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.PRIMARY_COLORS["400"]},
                    stop: 1 {config.PRIMARY_COLORS["600"]});
                border: 2px solid {config.PRIMARY_COLORS["700"]};
                color: white;
                min-width: 40px;
                min-height: 40px;
                border-radius: 20px;
                font-weight: 600;
            }}

            QPushButton#playButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.PRIMARY_COLORS["300"]},
                    stop: 1 {config.PRIMARY_COLORS["500"]});
                border: 3px solid {config.PRIMARY_COLORS["600"]};
            }}

            QPushButton#playButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.PRIMARY_COLORS["600"]},
                    stop: 1 {config.PRIMARY_COLORS["800"]});
                border: 1px solid {config.PRIMARY_COLORS["700"]};
            }}

            /* Secondary action buttons with Material styling */
            QPushButton#resetButton, QPushButton#prevSectionButton, QPushButton#nextSectionButton {{
                min-width: 36px;
                min-height: 36px;
                border-radius: 18px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(60, 60, 60, 0.8),
                    stop: 1 rgba(45, 45, 45, 0.8));
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            QPushButton#resetButton:hover, QPushButton#prevSectionButton:hover, QPushButton#nextSectionButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(80, 80, 80, 0.9),
                    stop: 1 rgba(65, 65, 65, 0.9));
                border: 2px solid rgba(255, 255, 255, 0.2);
            }}

            /* Presentation mode button styling */
            QPushButton#presentationButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.SECONDARY_COLORS["400"]},
                    stop: 1 {config.SECONDARY_COLORS["600"]});
                border: 2px solid {config.SECONDARY_COLORS["700"]};
                color: white;
                border-radius: {config.MATERIAL_BORDER_RADIUS["medium"]}px;
            }}

            QPushButton#presentationButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.SECONDARY_COLORS["300"]},
                    stop: 1 {config.SECONDARY_COLORS["500"]});
                border: 3px solid {config.SECONDARY_COLORS["600"]};
            }}

            /* Enhanced spinbox styling with Material Design */
            QSpinBox, QDoubleSpinBox {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(32, 32, 32, 0.8),
                    stop: 1 rgba(28, 28, 28, 0.8));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {config.MATERIAL_BORDER_RADIUS["medium"]}px;
                color: #e0e0e0;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
                min-height: 32px;
            }}

            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: rgba(255, 255, 255, 0.2);
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(42, 42, 42, 0.9),
                    stop: 1 rgba(38, 38, 38, 0.9));
                border-width: 2px;
            }}

            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {config.PRIMARY_COLORS["400"]};
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(42, 42, 42, 0.9),
                    stop: 1 rgba(38, 38, 38, 0.9));
            }}

            /* Spinbox button styling with Material patterns */
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background: rgba(60, 60, 60, 0.6);
                border: none;
                border-radius: {config.MATERIAL_BORDER_RADIUS["small"]}px;
                width: 20px;
                margin: 2px;
            }}

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background: rgba(80, 80, 80, 0.8);
            }}

            QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed,
            QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {{
                background: rgba(40, 40, 40, 0.8);
            }}
        """
