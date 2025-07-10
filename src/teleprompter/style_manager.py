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
                padding: 2px 2px;
                spacing: 8px;
                font-size: 12px;
                font-weight: 500;
                border-radius: {config.MATERIAL_BORDER_RADIUS["small"]}px;
            }}

            QToolBar::separator {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.1),
                    stop: 0.5 rgba(255, 255, 255, 0.15),
                    stop: 1 rgba(255, 255, 255, 0.1));
                width: 1px;
                margin: 8px 2px;
                border-radius: 0.5px;
            }}

            /* Enhanced button styling with Material Design patterns */
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(42, 42, 42, 0.8),
                    stop: 1 rgba(32, 32, 32, 0.8));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                color: #e0e0e0;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
                min-height: 25px;
                max-height: 25px;
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
                border-radius: 4px;
                color: white;
                min-width: 20px;
                min-height: 25px;
                max-height: 25px;
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
                min-width: 20px;
                min-height: 25px;
                max-height: 25px;
                border-radius: 4px;
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

            /* Enhanced spinbox styling with Material Design */
            QSpinBox, QDoubleSpinBox {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(32, 32, 32, 0.8),
                    stop: 1 rgba(28, 28, 28, 0.8));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                color: #e0e0e0;
                padding: 0px 0px;
                font-size: 12px;
                min-width: 60px;
                min-height: 25px;
                max-height: 25px;
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
                width: 20px;
                margin: 0px;
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

    @staticmethod
    def get_toolbar_group_label_stylesheet() -> str:
        """Get stylesheet for toolbar group labels.

        Returns:
            CSS stylesheet for group labels
        """
        return """
            QPushButton:disabled {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.6);
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: 2px 6px;
                margin-right: 4px;
            }
        """

    @staticmethod
    def get_spinbox_button_stylesheet() -> str:
        """Get stylesheet for custom spinbox buttons.

        Returns:
            CSS stylesheet for spinbox buttons
        """
        return """
            QPushButton {
                background-color: transparent;
                border: 1px solid #404040;
                color: #c0c0c0;
                padding: 0px;
                margin: 0px;
                min-width: 18px;
                max-width: 18px;
                min-height: 12px;
                max-height: 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #404040;
                border-color: #0078d4;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0078d4;
                border-color: #106ebe;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: transparent;
                border-color: #2a2a2a;
                color: #666666;
            }
        """

    @staticmethod
    def get_voice_control_stylesheet() -> str:
        """Get stylesheet for voice control widget.

        Returns:
            CSS stylesheet for voice control components
        """
        return """
            /* Voice button styling */
            QPushButton#voiceButton {
                background-color: #333333;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                min-width: 25px;
                max-width: 25px;
                min-height: 25px;
                max-height: 25px;
                padding: 6px;
            }

            QPushButton#voiceButton:hover {
                background-color: #404040;
                border-color: #5a5a5a;
            }

            /* Sensitivity slider styling */
            QSlider#sensitivitySlider {
                margin: 4px 0px;
            }

            QSlider#sensitivitySlider::groove:horizontal {
                border: 1px solid #404040;
                height: 4px;
                background-color: #262626;
                border-radius: 2px;
            }

            QSlider#sensitivitySlider::handle:horizontal {
                background-color: #0078d4;
                border: 1px solid #005a9e;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }

            QSlider#sensitivitySlider::handle:horizontal:hover {
                background-color: #106ebe;
                border-color: #0052a0;
            }

            QSlider#sensitivitySlider::sub-page:horizontal {
                background-color: #0078d4;
                border: 1px solid #005a9e;
                border-radius: 2px;
            }

            /* ComboBox styling */
            QComboBox#deviceCombo {
                background-color: #262626;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 6px 8px;
                font-size: 12px;
                min-height: 25px;
                max-height: 25px;
            }

            QComboBox#deviceCombo:hover {
                border-color: #505050;
                background-color: #2e2e2e;
            }

            QComboBox#deviceCombo:focus {
                border-color: #0078d4;
            }

            QComboBox#deviceCombo::drop-down {
                border: none;
                width: 16px;
            }

            QComboBox#deviceCombo::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid #aaaaaa;
                margin-right: 4px;
            }

            QComboBox#deviceCombo QAbstractItemView {
                background-color: #262626;
                border: 1px solid #404040;
                border-radius: 2px;
                color: #e0e0e0;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                padding: 1px;
            }

            QComboBox#deviceCombo QAbstractItemView::item {
                padding: 4px 6px;
                border: none;
                border-radius: 1px;
            }

            QComboBox#deviceCombo QAbstractItemView::item:hover {
                background-color: #333333;
            }

            QComboBox#deviceCombo QAbstractItemView::item:selected {
                background-color: #0078d4;
            }
        """

    @staticmethod
    def get_voice_button_disabled_stylesheet() -> str:
        """Get stylesheet for disabled voice button.

        Returns:
            CSS stylesheet for disabled voice button
        """
        return """
            QPushButton#voiceButton {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #666666;
                font-size: 12px;
                min-width: 25px;
                max-width: 25px;
                min-height: 25px;
                max-height: 25px;
                padding: 6px;
            }
            QPushButton#voiceButton:hover {
                background-color: #333333;
                border-color: #505050;
                color: #888888;
            }
        """

    @staticmethod
    def get_voice_button_speaking_stylesheet() -> str:
        """Get stylesheet for voice button when speaking is detected.

        Returns:
            CSS stylesheet for speaking voice button
        """
        return """
            QPushButton#voiceButton {
                background-color: #4CAF50;
                border: 1px solid #388E3C;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                min-width: 25px;
                max-width: 25px;
                min-height: 25px;
                max-height: 25px;
                padding: 6px;
            }
            QPushButton#voiceButton:hover {
                background-color: #66BB6A;
                border-color: #43A047;
            }
        """

    @staticmethod
    def get_voice_button_listening_stylesheet() -> str:
        """Get stylesheet for voice button when listening (active but no speech).

        Returns:
            CSS stylesheet for listening voice button
        """
        return """
            QPushButton#voiceButton {
                background-color: #0078d4;
                border: 1px solid #005a9e;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                min-width: 25px;
                max-width: 25px;
                min-height: 25px;
                max-height: 25px;
                padding: 6px;
            }
            QPushButton#voiceButton:hover {
                background-color: #106ebe;
                border-color: #0052a0;
            }
        """

    @staticmethod
    def get_voice_button_error_stylesheet() -> str:
        """Get voice button error state stylesheet."""
        return """
            QPushButton {
                background-color: rgba(255, 100, 100, 0.3);
                border: 2px solid rgba(255, 100, 100, 0.6);
                color: #ff6464;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 0.4);
                border-color: rgba(255, 100, 100, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(255, 100, 100, 0.2);
                border-color: rgba(255, 100, 100, 0.4);
            }
        """

    @staticmethod
    def get_progress_bar_stylesheet() -> str:
        """Get progress bar stylesheet."""
        return "background: transparent;"

    @staticmethod
    def get_main_window_stylesheet() -> str:
        """Get main window background stylesheet."""
        return f"background-color: {config.BACKGROUND_COLOR};"

    @staticmethod
    def get_web_view_stylesheet() -> str:
        """Get web view background stylesheet."""
        return f"background-color: {config.BACKGROUND_COLOR};"

    @staticmethod
    def get_mobile_info_overlay_stylesheet() -> str:
        """Get mobile-specific info overlay stylesheet."""
        return """
            QLabel {
                font-size: 14px;
                padding: 12px;
            }
        """

    @staticmethod
    def get_tablet_info_overlay_stylesheet() -> str:
        """Get tablet-specific info overlay stylesheet."""
        return """
            QLabel {
                font-size: 13px;
                padding: 10px;
            }
        """

    @staticmethod
    def get_voice_label_stylesheet() -> str:
        """Get stylesheet for voice control labels.

        Returns:
            CSS stylesheet for voice labels
        """
        return """
            QPushButton:disabled {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 11px;
                font-weight: normal;
                padding: 2px 4px;
            }
        """

    @staticmethod
    def get_teleprompter_info_overlay_stylesheet() -> str:
        """Get stylesheet for teleprompter info overlay."""
        return f"""
            QWidget {{
                background-color: rgba(15, 15, 15, 0.9);
                color: #e0e0e0;
                border-radius: {config.MATERIAL_BORDER_RADIUS["small"]}px;
                padding: 8px;
            }}
        """

    @staticmethod
    def get_teleprompter_info_label_stylesheet() -> str:
        """Get stylesheet for teleprompter info labels."""
        return """
            QLabel {
                background: transparent;
                color: #e0e0e0;
                font-size: 12px;
                font-weight: 400;
                padding: 4px 8px;
                border: none;
            }
        """
