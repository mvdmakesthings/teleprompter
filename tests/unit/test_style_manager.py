"""Unit tests for StyleManager."""

import pytest

from src.teleprompter.ui.managers.style_manager import StyleManager


class TestStyleManager:
    """Test the StyleManager class."""

    @pytest.fixture
    def manager(self):
        """Create a StyleManager instance."""
        return StyleManager()

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager._current_theme == "default"
        assert "background_color" in manager._theme_variables
        assert "text_color" in manager._theme_variables
        assert "font_family" in manager._theme_variables
        assert "default_font_size" in manager._theme_variables

    def test_get_application_stylesheet(self, manager):
        """Test getting application stylesheet."""
        stylesheet = manager.get_application_stylesheet()
        assert isinstance(stylesheet, str)
        assert "QMainWindow" in stylesheet
        assert "QToolBar" in stylesheet
        assert "background-color" in stylesheet

    def test_get_stylesheet(self, manager):
        """Test getting component-specific stylesheet."""
        # Test various components that are defined in the component_methods dict
        components = [
            "application",
            "toolbar_group_label",
            "extension_container",
            "voice_button",
            "voice_button_active",
            "voice_button_error",
            "voice_button_loading",
            "progress_bar",
            "main_window_background",
            "web_view_background",
            "mobile_info_overlay",
            "tablet_info_overlay",
            "pause_button",
            "teleprompter_info_overlay",
            "teleprompter_info_labels",
        ]

        for component in components:
            stylesheet = manager.get_stylesheet(component)
            assert isinstance(stylesheet, str)
            # Most stylesheets should contain some styling
            assert len(stylesheet) > 0

        # Test unknown component
        stylesheet = manager.get_stylesheet("unknown_component")
        assert stylesheet == ""

    def test_get_toolbar_group_label_stylesheet(self, manager):
        """Test toolbar group label stylesheet."""
        stylesheet = manager.get_toolbar_group_label_stylesheet()
        assert isinstance(stylesheet, str)
        assert "QPushButton:disabled" in stylesheet
        assert "background: transparent" in stylesheet

    def test_voice_control_stylesheets(self, manager):
        """Test voice control related stylesheets."""
        # Test voice control widget stylesheet
        stylesheet = manager.get_voice_control_stylesheet()
        assert isinstance(stylesheet, str)
        assert "voiceButton" in stylesheet
        assert "sensitivitySlider" in stylesheet
        assert "deviceCombo" in stylesheet

        # Test voice button states
        disabled = manager.get_voice_button_disabled_stylesheet()
        assert "voiceButton" in disabled
        assert "#2a2a2a" in disabled  # Disabled color

        speaking = manager.get_voice_button_speaking_stylesheet()
        assert "voiceButton" in speaking
        assert "#4CAF50" in speaking  # Green for speaking

        listening = manager.get_voice_button_listening_stylesheet()
        assert "voiceButton" in listening
        assert "#0078d4" in listening  # Blue for listening

    def test_get_theme_variables(self, manager):
        """Test getting theme variables."""
        variables = manager.get_theme_variables()
        assert isinstance(variables, dict)
        assert "background_color" in variables
        assert "text_color" in variables
        assert "font_family" in variables
        assert "default_font_size" in variables

    def test_set_theme(self, manager):
        """Test setting theme."""
        # Get original theme
        original_theme = manager._current_theme
        assert original_theme == "default"

        # Set new theme
        manager.set_theme("dark")
        assert manager._current_theme == "dark"

        # Set back to default
        manager.set_theme("default")
        assert manager._current_theme == "default"

    def test_specific_stylesheet_methods(self, manager):
        """Test specific stylesheet getter methods."""
        # Test spinbox button stylesheet
        button_style = manager.get_spinbox_button_stylesheet()
        assert isinstance(button_style, str)
        assert "QPushButton" in button_style
        assert "transparent" in button_style

        # Test progress bar
        progress_style = manager.get_progress_bar_stylesheet()
        assert isinstance(progress_style, str)
        assert "background: transparent" in progress_style

        # Test main window
        main_style = manager.get_main_window_stylesheet()
        assert isinstance(main_style, str)
        assert "background-color:" in main_style

        # Test web view
        web_style = manager.get_web_view_stylesheet()
        assert isinstance(web_style, str)
        assert "background-color:" in web_style

        # Test voice button stylesheets
        voice_style = manager.get_voice_button_stylesheet()
        assert isinstance(voice_style, str)

        # Test extension container
        ext_style = manager.get_extension_container_stylesheet()
        assert isinstance(ext_style, str)


def test_style_manager_instance():
    """Test creating style manager instance."""
    manager = StyleManager()
    assert isinstance(manager, StyleManager)
    assert manager._current_theme == "default"
