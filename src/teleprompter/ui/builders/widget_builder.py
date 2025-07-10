"""Builder pattern for constructing complex UI widgets."""

from abc import ABC, abstractmethod

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..managers.style_manager import StyleManager
from ..widgets.custom_widgets import IconButton, ModernDoubleSpinBox, ModernSpinBox


class WidgetBuilder(ABC):
    """Abstract base class for widget builders."""

    @abstractmethod
    def build(self) -> QWidget:
        """Build and return the widget."""
        pass


class StatusPanelBuilder(WidgetBuilder):
    """Builder for status panel widgets."""

    def __init__(self):
        self._show_progress = True
        self._show_speed = True
        self._show_time = True
        self._style_manager = StyleManager()

    def with_progress(self, show: bool = True) -> "StatusPanelBuilder":
        """Configure progress display."""
        self._show_progress = show
        return self

    def with_speed(self, show: bool = True) -> "StatusPanelBuilder":
        """Configure speed display."""
        self._show_speed = show
        return self

    def with_time(self, show: bool = True) -> "StatusPanelBuilder":
        """Configure time display."""
        self._show_time = show
        return self

    def build(self) -> QWidget:
        """Build the status panel."""
        panel = QWidget()
        panel.setObjectName("statusPanel")

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        # Status label
        status_label = QLabel("Ready")
        status_label.setObjectName("statusLabel")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)

        layout.addStretch()

        # Speed indicator
        if self._show_speed:
            speed_widget = self._create_speed_widget()
            layout.addWidget(speed_widget)

        # Time indicators
        if self._show_time:
            time_widget = self._create_time_widget()
            layout.addWidget(time_widget)

        # Progress bar
        if self._show_progress:
            progress_widget = self._create_progress_widget()
            layout.addWidget(progress_widget)

        # Apply styling
        panel.setStyleSheet(self._style_manager.get_panel_stylesheet())

        return panel

    def _create_speed_widget(self) -> QWidget:
        """Create speed indicator widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        label = QLabel("Speed:")
        label.setObjectName("speedLabel")
        layout.addWidget(label)

        value_label = QLabel("1.0x")
        value_label.setObjectName("speedValue")
        value_label.setMinimumWidth(50)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)

        return widget

    def _create_time_widget(self) -> QWidget:
        """Create time display widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Elapsed time
        elapsed_label = QLabel("Elapsed:")
        elapsed_label.setObjectName("elapsedLabel")
        layout.addWidget(elapsed_label)

        elapsed_value = QLabel("0:00")
        elapsed_value.setObjectName("elapsedValue")
        elapsed_value.setMinimumWidth(50)
        layout.addWidget(elapsed_value)

        # Remaining time
        remaining_label = QLabel("Remaining:")
        remaining_label.setObjectName("remainingLabel")
        layout.addWidget(remaining_label)

        remaining_value = QLabel("0:00")
        remaining_value.setObjectName("remainingValue")
        remaining_value.setMinimumWidth(50)
        layout.addWidget(remaining_value)

        return widget

    def _create_progress_widget(self) -> QWidget:
        """Create progress bar widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        label = QLabel("Progress:")
        label.setObjectName("progressLabel")
        layout.addWidget(label)

        progress_bar = QProgressBar()
        progress_bar.setObjectName("progressBar")
        progress_bar.setTextVisible(False)
        progress_bar.setMaximum(1000)
        progress_bar.setMinimumWidth(200)
        progress_bar.setMaximumWidth(300)
        layout.addWidget(progress_bar)

        return widget


class ControlPanelBuilder(WidgetBuilder):
    """Builder for control panel widgets."""

    def __init__(self):
        self._buttons = []
        self._sliders = []
        self._spinboxes = []
        self._orientation = Qt.Orientation.Horizontal
        self._style_manager = StyleManager()

    def with_button(
        self,
        text: str,
        icon: str | None = None,
        tooltip: str | None = None,
        object_name: str | None = None,
    ) -> "ControlPanelBuilder":
        """Add a button to the panel."""
        self._buttons.append(
            {"text": text, "icon": icon, "tooltip": tooltip, "object_name": object_name}
        )
        return self

    def with_slider(
        self,
        min_value: int,
        max_value: int,
        default_value: int,
        object_name: str | None = None,
    ) -> "ControlPanelBuilder":
        """Add a slider to the panel."""
        self._sliders.append(
            {
                "min": min_value,
                "max": max_value,
                "default": default_value,
                "object_name": object_name,
            }
        )
        return self

    def with_spinbox(
        self,
        min_value: float,
        max_value: float,
        default_value: float,
        step: float = 1.0,
        is_double: bool = False,
        object_name: str | None = None,
    ) -> "ControlPanelBuilder":
        """Add a spinbox to the panel."""
        self._spinboxes.append(
            {
                "min": min_value,
                "max": max_value,
                "default": default_value,
                "step": step,
                "is_double": is_double,
                "object_name": object_name,
            }
        )
        return self

    def with_orientation(self, orientation: Qt.Orientation) -> "ControlPanelBuilder":
        """Set panel orientation."""
        self._orientation = orientation
        return self

    def build(self) -> QWidget:
        """Build the control panel."""
        panel = QWidget()
        panel.setObjectName("controlPanel")

        if self._orientation == Qt.Orientation.Horizontal:
            layout = QHBoxLayout(panel)
        else:
            layout = QVBoxLayout(panel)

        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Add buttons
        for button_config in self._buttons:
            button = self._create_button(button_config)
            layout.addWidget(button)

        # Add separators between different control types
        if self._buttons and (self._sliders or self._spinboxes):
            layout.addSpacing(20)

        # Add sliders
        for slider_config in self._sliders:
            slider = self._create_slider(slider_config)
            layout.addWidget(slider)

        # Add spinboxes
        for spinbox_config in self._spinboxes:
            spinbox = self._create_spinbox(spinbox_config)
            layout.addWidget(spinbox)

        # Apply styling
        panel.setStyleSheet(self._style_manager.get_control_panel_stylesheet())

        return panel

    def _create_button(self, config: dict) -> QPushButton:
        """Create a button from configuration."""
        if config.get("icon"):
            button = IconButton(config["icon"], config.get("text", ""))
        else:
            button = QPushButton(config["text"])

        if config.get("tooltip"):
            button.setToolTip(config["tooltip"])

        if config.get("object_name"):
            button.setObjectName(config["object_name"])

        return button

    def _create_slider(self, config: dict) -> QSlider:
        """Create a slider from configuration."""
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(config["min"])
        slider.setMaximum(config["max"])
        slider.setValue(config["default"])

        if config.get("object_name"):
            slider.setObjectName(config["object_name"])

        return slider

    def _create_spinbox(self, config: dict) -> QSpinBox:
        """Create a spinbox from configuration."""
        if config["is_double"]:
            spinbox = ModernDoubleSpinBox()
            spinbox.setDecimals(1)
            spinbox.setSingleStep(config["step"])
        else:
            spinbox = ModernSpinBox()
            spinbox.setSingleStep(int(config["step"]))

        spinbox.setMinimum(config["min"])
        spinbox.setMaximum(config["max"])
        spinbox.setValue(config["default"])

        if config.get("object_name"):
            spinbox.setObjectName(config["object_name"])

        return spinbox


class DialogBuilder(WidgetBuilder):
    """Builder for dialog layouts."""

    def __init__(self):
        self._title = ""
        self._sections = []
        self._buttons = []
        self._style_manager = StyleManager()

    def with_title(self, title: str) -> "DialogBuilder":
        """Set dialog title."""
        self._title = title
        return self

    def with_section(
        self, title: str, widgets: list, collapsible: bool = False
    ) -> "DialogBuilder":
        """Add a section to the dialog."""
        self._sections.append(
            {"title": title, "widgets": widgets, "collapsible": collapsible}
        )
        return self

    def with_button_bar(self, buttons: list) -> "DialogBuilder":
        """Add a button bar to the dialog."""
        self._buttons = buttons
        return self

    def build(self) -> QWidget:
        """Build the dialog layout."""
        widget = QWidget()
        widget.setObjectName("dialogWidget")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        if self._title:
            title_label = QLabel(self._title)
            title_label.setObjectName("dialogTitle")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            layout.addSpacing(10)

        # Sections
        for section_config in self._sections:
            section_widget = self._create_section(section_config)
            layout.addWidget(section_widget)

        # Button bar
        if self._buttons:
            layout.addStretch()
            button_bar = self._create_button_bar()
            layout.addWidget(button_bar)

        # Apply styling
        widget.setStyleSheet(self._style_manager.get_dialog_stylesheet())

        return widget

    def _create_section(self, config: dict) -> QWidget:
        """Create a section widget."""
        section = QWidget()
        section.setObjectName("dialogSection")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Section title
        if config["title"]:
            title = QLabel(config["title"])
            title.setObjectName("sectionTitle")
            layout.addWidget(title)

        # Section content
        for widget in config["widgets"]:
            layout.addWidget(widget)

        return section

    def _create_button_bar(self) -> QWidget:
        """Create a button bar."""
        bar = QWidget()
        bar.setObjectName("buttonBar")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addStretch()

        for button in self._buttons:
            layout.addWidget(button)

        return bar
