"""Main application window and logic."""

import contextlib
import os

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from . import config
from .custom_widgets import IconDoubleSpinBox, IconSpinBox
from .icon_manager import icon_manager
from .markdown_parser import MarkdownParser
from .teleprompter import TeleprompterWidget
from .voice_control_widget import VoiceControlWidget


class TeleprompterApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.parser = MarkdownParser()
        self.current_file = None
        self.current_markdown_content = ""

        # Font and theme state tracking
        self.current_font_preset_index = 0
        self.current_theme_index = 0
        self.font_presets = list(config.FONT_PRESETS.keys())
        self.color_themes = list(config.COLOR_THEMES.keys())

        # Initialize settings for persistent preferences
        self.settings = QSettings("Teleprompter", "TeleprompterApp")
        self._load_preferences()

        self._setup_ui()
        self._setup_toolbar()
        self._setup_shortcuts()
        self._setup_button_hover_effects()

    def _load_preferences(self):
        """Load user preferences from settings."""
        # Load font preset
        saved_font_preset = self.settings.value("font_preset", self.font_presets[0])
        if saved_font_preset in self.font_presets:
            self.current_font_preset_index = self.font_presets.index(saved_font_preset)

        # Load theme
        saved_theme = self.settings.value("color_theme", self.color_themes[0])
        if saved_theme in self.color_themes:
            self.current_theme_index = self.color_themes.index(saved_theme)

        # Load window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Load speed setting
        saved_speed = self.settings.value("scroll_speed", config.DEFAULT_SPEED)
        with contextlib.suppress(ValueError, TypeError):
            config.DEFAULT_SPEED = float(saved_speed)

    def _save_preferences(self):
        """Save user preferences to settings."""
        self.settings.setValue(
            "font_preset", self.font_presets[self.current_font_preset_index]
        )
        self.settings.setValue(
            "color_theme", self.color_themes[self.current_theme_index]
        )
        self.settings.setValue("geometry", self.saveGeometry())
        if hasattr(self, "teleprompter") and hasattr(self.teleprompter, "speed"):
            self.settings.setValue("scroll_speed", self.teleprompter.speed)

    def closeEvent(self, event):
        """Handle application close event to save preferences."""
        self._save_preferences()
        super().closeEvent(event)

    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.DEFAULT_WIDTH, config.DEFAULT_HEIGHT)

        # Apply modern dark theme
        self._apply_modern_theme()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Teleprompter widget
        self.teleprompter = TeleprompterWidget()
        self.teleprompter.speed_changed.connect(self._on_speed_changed)
        self.teleprompter.voice_activity_changed.connect(
            self._on_voice_activity_changed
        )
        # Phase 3: Connect progress and reading stats signals
        self.teleprompter.progress_changed.connect(self._on_progress_changed)
        self.teleprompter.reading_stats_changed.connect(self._on_reading_stats_changed)
        layout.addWidget(self.teleprompter)

        # Load initial content
        self._load_welcome_content()

        # Give focus to teleprompter widget
        self.teleprompter.setFocus()

    def _apply_modern_theme(self):
        """Apply Material Design inspired theme with elevation and modern patterns."""
        self.setStyleSheet(f"""
            /* Main window styling */
            QMainWindow {{
                background-color: #0f0f0f;
                color: #e0e0e0;
            }}

            /* Enhanced toolbar with Material Design elevation */
            QToolBar {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(26, 26, 26, 0.95),
                    stop: 0.5 rgba(22, 22, 22, 0.9),
                    stop: 1 rgba(18, 18, 18, 0.95));
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 4px 8px;
                spacing: 8px;
                font-size: 12px;
                font-weight: 500;
                min-height: 48px;
                /* Material Design elevation */
                box-shadow: {config.MATERIAL_SHADOWS["medium"]};
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
                backdrop-filter: blur(5px);
                /* Material elevation */
                box-shadow: {config.MATERIAL_SHADOWS["low"]};
                /* Smooth transitions */
                transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
            }}

            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(52, 52, 52, 0.9),
                    stop: 1 rgba(42, 42, 42, 0.9));
                border-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                /* Elevated hover state */
                box-shadow: {config.MATERIAL_SHADOWS["medium"]};
                transform: translateY(-1px);
            }}

            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(22, 22, 22, 0.9),
                    stop: 1 rgba(32, 32, 32, 0.9));
                border-color: rgba(120, 120, 120, 0.3);
                transform: translateY(0px);
                box-shadow: {config.MATERIAL_SHADOWS["flat"]};
            }}

            QPushButton:disabled {{
                background: rgba(32, 32, 32, 0.3);
                border-color: rgba(255, 255, 255, 0.05);
                color: #666666;
                box-shadow: none;
            }}

            /* Primary action button (Play button) with Material colors */
            QPushButton#playButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.PRIMARY_COLORS["400"]},
                    stop: 1 {config.PRIMARY_COLORS["600"]});
                border-color: {config.PRIMARY_COLORS["700"]};
                color: white;
                min-width: 40px;
                min-height: 40px;
                border-radius: 20px;
                font-weight: 600;
                box-shadow: {config.MATERIAL_SHADOWS["medium"]};
            }}

            QPushButton#playButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.PRIMARY_COLORS["300"]},
                    stop: 1 {config.PRIMARY_COLORS["500"]});
                border-color: {config.PRIMARY_COLORS["600"]};
                box-shadow: {config.MATERIAL_SHADOWS["high"]};
                transform: translateY(-2px) scale(1.05);
            }}

            QPushButton#playButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.PRIMARY_COLORS["600"]},
                    stop: 1 {config.PRIMARY_COLORS["800"]});
                transform: translateY(0px) scale(1.0);
                box-shadow: {config.MATERIAL_SHADOWS["low"]};
            }}

            /* Secondary action buttons with Material styling */
            QPushButton#resetButton, QPushButton#prevSectionButton, QPushButton#nextSectionButton {{
                min-width: 36px;
                min-height: 36px;
                border-radius: 18px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(60, 60, 60, 0.8),
                    stop: 1 rgba(45, 45, 45, 0.8));
                box-shadow: {config.MATERIAL_SHADOWS["low"]};
            }}

            QPushButton#resetButton:hover, QPushButton#prevSectionButton:hover, QPushButton#nextSectionButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(80, 80, 80, 0.9),
                    stop: 1 rgba(65, 65, 65, 0.9));
                box-shadow: {config.MATERIAL_SHADOWS["medium"]};
                transform: translateY(-1px);
            }}

            /* Presentation mode button styling */
            QPushButton#presentationButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.SECONDARY_COLORS["400"]},
                    stop: 1 {config.SECONDARY_COLORS["600"]});
                border-color: {config.SECONDARY_COLORS["700"]};
                color: white;
                border-radius: {config.MATERIAL_BORDER_RADIUS["medium"]}px;
                box-shadow: {config.MATERIAL_SHADOWS["low"]};
            }}

            QPushButton#presentationButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {config.SECONDARY_COLORS["300"]},
                    stop: 1 {config.SECONDARY_COLORS["500"]});
                box-shadow: {config.MATERIAL_SHADOWS["medium"]};
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
                backdrop-filter: blur(3px);
                box-shadow: {config.MATERIAL_SHADOWS["low"]};
            }}

            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: rgba(255, 255, 255, 0.2);
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(42, 42, 42, 0.9),
                    stop: 1 rgba(38, 38, 38, 0.9));
                box-shadow: {config.MATERIAL_SHADOWS["medium"]};
            }}

            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {config.PRIMARY_COLORS["400"]};
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(42, 42, 42, 0.9),
                    stop: 1 rgba(38, 38, 38, 0.9));
                box-shadow: 0 0 0 2px {config.PRIMARY_COLORS["100"]}40;
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
        """)

    def _setup_toolbar(self):
        """Set up the modern grouped toolbar with glassmorphism design."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        # Group 1: File Operations
        self._add_file_controls(toolbar)
        self._add_visual_separator(toolbar, "File")

        # Group 2: Playback Controls
        self._add_playback_controls(toolbar)
        self._add_visual_separator(toolbar, "Playback")

        # Group 3: Speed & Font Controls
        self._add_speed_font_controls(toolbar)
        self._add_visual_separator(toolbar, "Display")

        # Group 4: Theme Controls
        self._add_theme_controls(toolbar)
        self._add_visual_separator(toolbar, "Theme")

        # Group 5: Voice Control
        self._add_voice_controls(toolbar)
        self._add_visual_separator(toolbar, "Voice")

        # Group 6: View Controls
        self._add_view_controls(toolbar)

    def _add_file_controls(self, toolbar):
        """Add file operation controls group."""
        # File section with modern icon
        open_action = QAction("Open", self)
        open_action.setToolTip("Open markdown file (Ctrl+O)")
        open_action.triggered.connect(self.open_file)

        # Set icon for open action
        open_pixmap = icon_manager.get_themed_pixmap("folder-open", "default", "medium")
        if not open_pixmap.isNull():
            open_action.setIcon(QIcon(open_pixmap))
        else:
            open_action.setText("📁 Open")

        toolbar.addAction(open_action)

    def _add_playback_controls(self, toolbar):
        """Add playback controls group with enhanced styling."""
        # Play/Pause button with premium styling
        self.play_button = QPushButton()
        self.play_button.setObjectName("playButton")
        self.play_button.setToolTip("Play/Pause scrolling (Space)")
        self.play_button.clicked.connect(self._toggle_playback)
        self._update_play_button_icon()
        toolbar.addWidget(self.play_button)

        # Reset button with modern design
        reset_button = QPushButton()
        reset_button.setObjectName("resetButton")
        reset_button.setToolTip("Reset to beginning (R)")
        reset_button.clicked.connect(self._reset_and_focus)

        reset_pixmap = icon_manager.get_themed_pixmap("skip-back", "default", "medium")
        if not reset_pixmap.isNull():
            reset_button.setIcon(QIcon(reset_pixmap))
        else:
            reset_button.setText("⏮")

        toolbar.addWidget(reset_button)

        # Section navigation buttons
        toolbar.addSeparator()

        # Previous section button
        prev_section_button = QPushButton("◀")
        prev_section_button.setObjectName("prevSectionButton")
        prev_section_button.setToolTip("Previous section (←)")
        prev_section_button.clicked.connect(self._goto_previous_section)
        toolbar.addWidget(prev_section_button)

        # Next section button
        next_section_button = QPushButton("▶")
        next_section_button.setObjectName("nextSectionButton")
        next_section_button.setToolTip("Next section (→)")
        next_section_button.clicked.connect(self._goto_next_section)
        toolbar.addWidget(next_section_button)

    def _add_speed_font_controls(self, toolbar):
        """Add speed and font controls group."""
        # Speed control section with grouping
        speed_group = self._create_control_group("Speed")
        toolbar.addWidget(speed_group)

        self.speed_spin = IconDoubleSpinBox()
        self.speed_spin.setMinimum(config.MIN_SPEED)
        self.speed_spin.setMaximum(config.MAX_SPEED)
        self.speed_spin.setValue(config.DEFAULT_SPEED)
        self.speed_spin.setSuffix("x")
        self.speed_spin.setDecimals(2)
        self.speed_spin.setSingleStep(config.SPEED_INCREMENT)
        self.speed_spin.setToolTip("Scrolling speed (↑↓ arrows)")
        self.speed_spin.valueChanged.connect(self._on_speed_spinner_changed)
        toolbar.addWidget(self.speed_spin)

        # Add small spacer
        toolbar.addSeparator()

        # Font size control section
        font_group = self._create_control_group("Font")
        toolbar.addWidget(font_group)

        self.font_size_spin = IconSpinBox()
        self.font_size_spin.setMinimum(config.MIN_FONT_SIZE)
        self.font_size_spin.setMaximum(config.MAX_FONT_SIZE)
        self.font_size_spin.setValue(config.DEFAULT_FONT_SIZE)
        self.font_size_spin.setSuffix("px")
        self.font_size_spin.setToolTip("Font size")
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        toolbar.addWidget(self.font_size_spin)

        # Font preset button
        self.font_preset_btn = QPushButton("Auto")
        self.font_preset_btn.setMaximumWidth(50)
        self.font_preset_btn.setToolTip("Font preset for viewing distance")
        self.font_preset_btn.clicked.connect(self._cycle_font_preset)
        toolbar.addWidget(self.font_preset_btn)

    def _add_theme_controls(self, toolbar):
        """Add theme controls group."""
        theme_group = self._create_control_group("Theme")
        toolbar.addWidget(theme_group)

        self.theme_btn = QPushButton("Standard")
        self.theme_btn.setMaximumWidth(80)
        self.theme_btn.setToolTip("Color theme for different contrast needs")
        self.theme_btn.clicked.connect(self._cycle_color_theme)
        toolbar.addWidget(self.theme_btn)

    def _add_voice_controls(self, toolbar):
        """Add voice control group."""
        self.voice_control_widget = VoiceControlWidget()
        self.voice_control_widget.voice_detection_enabled.connect(
            self._on_voice_detection_enabled
        )
        toolbar.addWidget(self.voice_control_widget)

    def _add_view_controls(self, toolbar):
        """Add view controls group."""
        # Presentation mode button
        presentation_button = QPushButton("Present")
        presentation_button.setObjectName("presentationButton")
        presentation_button.setToolTip("Toggle presentation mode (Ctrl+P)")
        presentation_button.clicked.connect(self._toggle_presentation_mode)
        toolbar.addWidget(presentation_button)

        # Fullscreen button
        fullscreen_button = QPushButton("Fullscreen")
        fullscreen_button.setToolTip("Toggle fullscreen mode (F11)")
        fullscreen_button.clicked.connect(self.toggle_fullscreen)
        toolbar.addWidget(fullscreen_button)

    def _create_control_group(self, label: str) -> QPushButton:
        """Create a styled group label for controls."""
        group_label = QPushButton(label)
        group_label.setEnabled(False)
        group_label.setStyleSheet("""
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
        """)
        return group_label

    def _add_visual_separator(self, toolbar, group_name: str):
        """Add a visual separator between control groups."""
        toolbar.addSeparator()

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Space for play/pause
        self.play_action = QAction("Play/Pause", self)
        self.play_action.setShortcut(QKeySequence(Qt.Key.Key_Space))
        self.play_action.triggered.connect(self._toggle_playback)
        self.addAction(self.play_action)

        # R for reset
        self.reset_action = QAction("Reset", self)
        self.reset_action.setShortcut(QKeySequence(Qt.Key.Key_R))
        self.reset_action.triggered.connect(self._reset_and_focus)
        self.addAction(self.reset_action)

        # Up arrow for speed increase
        self.speed_up_action = QAction("Speed Up", self)
        self.speed_up_action.setShortcut(QKeySequence(Qt.Key.Key_Up))
        self.speed_up_action.triggered.connect(self._increase_speed)
        self.addAction(self.speed_up_action)

        # Down arrow for speed decrease
        self.speed_down_action = QAction("Speed Down", self)
        self.speed_down_action.setShortcut(QKeySequence(Qt.Key.Key_Down))
        self.speed_down_action.triggered.connect(self._decrease_speed)
        self.addAction(self.speed_down_action)

        # F11 for fullscreen
        self.fullscreen_action = QAction("Fullscreen", self)
        self.fullscreen_action.setShortcut(QKeySequence(Qt.Key.Key_F11))
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(self.fullscreen_action)

        # Escape to exit fullscreen
        self.exit_fullscreen_action = QAction("Exit Fullscreen", self)
        self.exit_fullscreen_action.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        self.exit_fullscreen_action.triggered.connect(self.exit_fullscreen)
        self.addAction(self.exit_fullscreen_action)

        # Ctrl+O for open file
        self.open_action = QAction("Open File", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_file)
        self.addAction(self.open_action)

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # File shortcuts
        open_action = QAction(self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        self.addAction(open_action)

        # Fullscreen shortcut
        fullscreen_action = QAction(self)
        fullscreen_action.setShortcut(Qt.Key.Key_F11)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(fullscreen_action)

        # Escape to exit fullscreen
        escape_action = QAction(self)
        escape_action.setShortcut(Qt.Key.Key_Escape)
        escape_action.triggered.connect(self.exit_fullscreen)
        self.addAction(escape_action)

    def _load_welcome_content(self):
        """Load welcome/empty state content."""
        empty_state_html = self.parser._generate_empty_state_html()
        self.teleprompter.load_content(empty_state_html)

    def open_file(self):
        """Open a markdown file with loading states and error handling."""
        file_filter = "Markdown files (" + " ".join(config.MARKDOWN_EXTENSIONS) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Markdown File", "", file_filter
        )

        if file_path:
            self._load_file_with_states(file_path)

    def _load_file_with_states(self, file_path: str):
        """Load a file with proper loading and error state management."""
        # Show loading state
        self._show_loading_state()

        try:
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"Cannot read file: {file_path}")

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > config.MAX_FILE_SIZE:
                raise ValueError(
                    f"File too large ({file_size} bytes). Maximum size is {config.MAX_FILE_SIZE} bytes."
                )

            if file_size == 0:
                raise ValueError("File is empty")

            # Read and parse file
            with open(file_path, encoding="utf-8") as f:
                self.current_markdown_content = f.read()

            # Parse content
            html_content = self.parser.parse_file(file_path)

            # Load content successfully
            self.teleprompter.load_content(html_content)
            self.current_file = file_path
            self.setWindowTitle(
                f"{config.WINDOW_TITLE} - {os.path.basename(file_path)}"
            )
            self.teleprompter.reset()
            # Ensure teleprompter widget has focus for keyboard controls
            self.teleprompter.ensure_focus()

        except FileNotFoundError as e:
            self._show_error_state(str(e), "File Not Found")
        except PermissionError as e:
            self._show_error_state(str(e), "Permission Denied")
        except UnicodeDecodeError:
            self._show_error_state(
                "File contains invalid text encoding. Please save the file as UTF-8.",
                "Encoding Error",
            )
        except ValueError as e:
            self._show_error_state(str(e), "File Error")
        except Exception as e:
            self._show_error_state(f"Unexpected error: {str(e)}", "Unknown Error")

    def _show_loading_state(self):
        """Display loading state in the teleprompter."""
        loading_html = self.parser._generate_loading_html()
        self.teleprompter.load_content(loading_html)

    def _show_error_state(self, error_message: str, error_type: str = "Error"):
        """Display error state in the teleprompter with retry options."""
        error_html = self.parser._generate_error_html(error_message, error_type)
        self.teleprompter.load_content(error_html)

        # Show a more user-friendly error dialog as well
        self._show_error_dialog(error_message, error_type)

    def _show_error_dialog(self, error_message: str, error_type: str = "Error"):
        """Show a user-friendly error dialog with helpful suggestions."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(error_type)
        msg.setText(f"<b>{error_type}</b>")

        # Create detailed message with suggestions
        detailed_text = f"{error_message}\n\n"

        if "not found" in error_message.lower():
            detailed_text += "Suggestions:\n• Check that the file path is correct\n• Ensure the file hasn't been moved or deleted\n• Try browsing for the file again"
        elif "permission" in error_message.lower():
            detailed_text += "Suggestions:\n• Check file permissions\n• Try running as administrator\n• Ensure the file is not locked by another program"
        elif "encoding" in error_message.lower():
            detailed_text += "Suggestions:\n• Save the file with UTF-8 encoding\n• Try opening with a text editor first\n• Check for special characters in the file"
        elif "size" in error_message.lower():
            detailed_text += "Suggestions:\n• Split large documents into smaller files\n• Remove unnecessary content\n• Consider using a more powerful text editor"
        else:
            detailed_text += "Suggestions:\n• Try opening a different file\n• Check the file format is supported\n• Restart the application if problems persist"

        msg.setDetailedText(detailed_text)

        # Add retry button
        retry_button = msg.addButton("Try Again", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)

        msg.exec()
        if msg.clickedButton() == retry_button:
            self.open_file()

    def _reset_and_focus(self):
        """Reset teleprompter and ensure focus."""
        self.teleprompter.reset()
        self.teleprompter.ensure_focus()

    def _toggle_playback(self):
        """Toggle play/pause."""
        self.teleprompter.toggle_playback()
        self._update_play_button_icon()
        # Ensure teleprompter widget has focus for keyboard controls
        self.teleprompter.ensure_focus()

    def _update_play_button_icon(self):
        """Update the play button icon based on the current state."""
        if hasattr(self, "teleprompter") and self.teleprompter.is_playing:
            # Show pause icon
            pause_pixmap = icon_manager.get_themed_pixmap("pause", "default", "medium")
            if not pause_pixmap.isNull():
                self.play_button.setIcon(QIcon(pause_pixmap))
                self.play_button.setText("")
            else:
                self.play_button.setText("⏸")  # Fallback to emoji
        else:
            # Show play icon
            play_pixmap = icon_manager.get_themed_pixmap("play", "default", "medium")
            if not play_pixmap.isNull():
                self.play_button.setIcon(QIcon(play_pixmap))
                self.play_button.setText("")
            else:
                self.play_button.setText("▶")  # Fallback to emoji

    def _setup_button_hover_effects(self):
        """Set up hover effects for better visual feedback."""

        # Add hover effects to play button
        def on_play_button_enter():
            if hasattr(self, "teleprompter") and self.teleprompter.is_playing:
                pause_pixmap = icon_manager.get_themed_pixmap(
                    "pause", "hover", "medium"
                )
                if not pause_pixmap.isNull():
                    self.play_button.setIcon(QIcon(pause_pixmap))
            else:
                play_pixmap = icon_manager.get_themed_pixmap("play", "hover", "medium")
                if not play_pixmap.isNull():
                    self.play_button.setIcon(QIcon(play_pixmap))

        def on_play_button_leave():
            self._update_play_button_icon()

        # Install event filters for hover effects
        self.play_button.enterEvent = lambda e: on_play_button_enter()
        self.play_button.leaveEvent = lambda e: on_play_button_leave()

    def _on_speed_spinner_changed(self, speed: float):
        """Handle speed spinner change."""
        self.teleprompter.set_speed(speed)

    def _on_speed_changed(self, speed: float):
        """Handle speed change from teleprompter (keyboard shortcuts)."""
        # Update the speed spinner to reflect the new speed
        if hasattr(self, "speed_spin") and self.speed_spin.value() != speed:
            self.speed_spin.blockSignals(True)
            self.speed_spin.setValue(speed)
            self.speed_spin.blockSignals(False)

    def _on_font_size_changed(self, size: int):
        """Handle font size change."""
        self.teleprompter.set_font_size(size)

    def _cycle_font_preset(self):
        """Cycle through font presets for different viewing distances."""
        self.current_font_preset_index = (self.current_font_preset_index + 1) % len(
            self.font_presets
        )
        preset_name = self.font_presets[self.current_font_preset_index]

        # Update button text to show current preset
        preset_display_names = {
            "close": "Close",
            "medium": "Med",
            "far": "Far",
            "presentation": "Pres",
        }
        display_name = preset_display_names.get(preset_name, preset_name.title())
        self.font_preset_btn.setText(display_name)

        # Apply the preset
        self.teleprompter.set_font_preset(preset_name)

        # Update the font size spinner to reflect the preset size
        preset_size = config.FONT_PRESETS[preset_name]["size"]
        self.font_size_spin.blockSignals(True)
        self.font_size_spin.setValue(preset_size)
        self.font_size_spin.blockSignals(False)

    def _cycle_color_theme(self):
        """Cycle through color themes for different contrast needs."""
        self.current_theme_index = (self.current_theme_index + 1) % len(
            self.color_themes
        )
        theme_name = self.color_themes[self.current_theme_index]

        # Update button text to show current theme
        theme_display_names = {
            "standard": "Std",
            "high_contrast": "High",
            "low_light": "Low",
            "warm": "Warm",
        }
        display_name = theme_display_names.get(theme_name, theme_name.title())
        self.theme_btn.setText(display_name)

        # Apply the theme
        self.teleprompter.set_color_theme(theme_name)

        # Update the parser to use the new theme for future content
        self.parser = MarkdownParser()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()

    def _on_voice_detection_enabled(self, enabled: bool):
        """Handle voice detection enable/disable."""
        if enabled:
            # Connect voice detector to teleprompter
            voice_detector = self.voice_control_widget.get_voice_detector()
            self.teleprompter.set_voice_detector(voice_detector)
        else:
            # Disconnect voice detector
            self.teleprompter.set_voice_detector(None)

        self.teleprompter.enable_voice_control(enabled)

    def _on_voice_activity_changed(self, is_active: bool):
        """Handle voice activity status change."""
        # Update play button icon when voice controls the teleprompter
        self._update_play_button_icon()

    def _on_progress_changed(self, progress: float):
        """Handle progress change from teleprompter."""
        # This could be used to update a progress indicator in the UI
        # For now, we'll just store it for potential future use
        pass

    def _on_reading_stats_changed(self, stats: dict):
        """Handle reading statistics change from teleprompter."""
        # This could be used to display reading information in the status bar
        # For example: word count, estimated time, sections, etc.
        pass

    def _goto_previous_section(self):
        """Navigate to the previous section."""
        self.teleprompter.navigate_to_previous_section()
        self.teleprompter.setFocus()

    def _goto_next_section(self):
        """Navigate to the next section."""
        self.teleprompter.navigate_to_next_section()
        self.teleprompter.setFocus()

    def _toggle_presentation_mode(self):
        """Toggle presentation mode for distraction-free reading."""
        self.teleprompter.toggle_presentation_mode()
        self.teleprompter.setFocus()

    def _increase_speed(self):
        """Increase scrolling speed."""
        self.teleprompter.adjust_speed(config.SPEED_INCREMENT)

    def _decrease_speed(self):
        """Decrease scrolling speed."""
        self.teleprompter.adjust_speed(-config.SPEED_INCREMENT)
