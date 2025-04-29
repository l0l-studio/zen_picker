from typing import Callable

try:
    from PyQt6.QtGui import QColor
    from PyQt6.QtWidgets import (
        QWidget, 
        QVBoxLayout, 
        QHBoxLayout, 
        QPushButton,
        QLabel, 
        QScrollArea
    )
    from PyQt6.QtCore import QSysInfo, Qt, QTimer
except:
    from PyQt5.QtGui import QColor
    from PyQt5.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QApplication,
        QMessageBox,
        QLabel,
        QScrollArea
    )
    from PyQt5.QtCore import QSysInfo, Qt, QTimer

from krita import (
    Krita,
    DockWidget,
    ManagedColor,
    DockWidgetFactory,
    DockWidgetFactoryBase,
)

from .app import App
from .lib_zen import color_shift
from .color_slider import ColorSlider
from .nudge_slider import NudgeSlider
from .color_manager import ColorManager
from .app_settings import AppSettingsUI
from .utils import q_to_managed_color, managed_to_q_color, copy_managed_color

# constants
PLUGIN_NAME = "zen picker"
sync_interval = 30

class ZenDocker(DockWidget):
    def __init__(self):
        super().__init__()

        self.app = App(self)
        self.setup_ui()
        self.Init_Sync_Timer()

    def canvasChanged(self, canvas):
        pass

    def setup_ui(self):
        self.widget = QWidget()
        self.sliders = []

        top_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        slider_layout = QVBoxLayout()
        slider_layout.setSpacing(2)
        slider_layout.setContentsMargins(2, 2, 2, 2)

        settings_button = QPushButton()
        icon = self.app.krita_instance.icon("showColoring")
        settings_button.setIcon(icon)
        settings_button.setToolTip(i18n("Change settings"))
        settings_button.setMaximumSize(30, 30)

        settings_button.clicked.connect(self.render_settings_ui)

        self.debug_label = QLabel()
        main_layout.addWidget(self.debug_label)

        color_manager = ColorManager(
            self.app, 
            "color_manager"
        )

        scroll_area = QScrollArea()
        scroll_area.setWidget(color_manager)
        scroll_area.setWidgetResizable(True)

        current_color = self.app.current_color()

        # instantiate sliders
        for i in range(5):
            name = ""
            match i:
                case 0:
                    name = "r_slider"
                case 1:
                    name = "g_slider"
                case 2:
                    name = "b_slider"
                case 3:
                    name = "saturation_slider"
                case 4:
                    name = "value_slider"

            slider = ColorSlider(
                self.app, 
                name, 
                copy_managed_color(current_color),
                copy_managed_color(current_color)
            ) if i < 3 else NudgeSlider(
                self.app, 
                name, 
                copy_managed_color(current_color),
                copy_managed_color(current_color)
            ) 
            self.sliders.append(slider)

        # compose elements
        for slider in self.sliders:
            slider_layout.addWidget(slider)

        top_layout.addWidget(scroll_area)
        top_layout.setAlignment(Qt.AlignTop)
        top_layout.addLayout(main_layout)
        main_layout.addWidget(settings_button)
        main_layout.addLayout(slider_layout)

        self.widget.setLayout(top_layout)
        self.setWindowTitle(i18n(PLUGIN_NAME))
        self.setWidget(self.widget)
        [x.show() for x in self.sliders]

    def Init_Sync_Timer(self):
        self.timer_pulse = QTimer(self)
        self.timer_pulse.timeout.connect(self.Sync)
        self.timer_pulse.start(sync_interval)


    def Sync(self):
        self.app.sync()
        for slider in self.sliders:
            slider.update_color()

    def write_settings(self):
        setting = ";".join(
            [
                self.color_to_settings(line.left)
                + "|"
                + self.color_to_settings(line.right)
                for line in self.sliders
            ]
        )

        self.app.krita_instance.writeSetting("", settings("colors"), setting)

    # TODO: temp
    def color_to_settings(self, managedcolor):
        return ",".join(
            [
                managedcolor.colorModel(),
                managedcolor.colorDepth(),
                managedcolor.colorProfile(),
            ]
            + [str(c) for c in managedcolor.components()]
        )

    def render_settings_ui(self):
        ui = AppSettingsUI(self.app)
        ui.initialize()


def settings(name: str):
    return PLUGIN_NAME + name


Application.addDockWidgetFactory(
    DockWidgetFactory(
        "zen_picker_docker",
        DockWidgetFactoryBase.DockPosition.DockRight,
        ZenDocker,
    )
)
