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
from .lib_zen import (
        color_shift, 
        to_hsv, 
        to_hsluv, 
        value_shift,
        value_shift_uv,
        saturation_shift,
        saturation_shift_uv
)
from .color_slider import ColorSlider
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

        self.timer_pulse = None
        self.widget = QWidget()
        self.sliders = []
        self.color_manager: ColorManager = None

        self.setup_ui()
        self.Init_Sync_Timer()

    def canvasChanged(self, canvas):
        pass

    def setup_ui(self):
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

        self.color_manager = ColorManager(
            self.app, 
            "color_manager"
        )

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.color_manager)
        scroll_area.setWidgetResizable(True)

        current_color = self.app.current_color()

        self.sliders = [
        #red slider
        ColorSlider(
            self.app, 
            lambda rgba: (
                [0.0, rgba[1], rgba[2], rgba[3]], 
                [1.0, rgba[1], rgba[2], rgba[3]], 
                rgba[0]
            ),
            lambda rgba, color_comp: [color_comp, rgba[1], rgba[2], rgba[3]],
            copy_managed_color(current_color),
            copy_managed_color(current_color)
        ),
        #green slider
        ColorSlider(
            self.app, 
            lambda rgba: (
                [rgba[0], 0.0, rgba[2], rgba[3]], 
                [rgba[0], 1.0, rgba[2], rgba[3]],
                rgba[1]
            ),
            lambda rgba, color_comp: [rgba[0], color_comp, rgba[2], rgba[3]],
            copy_managed_color(current_color),
            copy_managed_color(current_color)
        ),
        #blue slider
        ColorSlider(
            self.app, 
            lambda rgba: (
                [rgba[0], rgba[1], 0.0, rgba[3]], 
                [rgba[0], rgba[1], 1.0, rgba[3]],
                rgba[2]
            ),
            lambda rgba, color_comp: [rgba[0], rgba[1], color_comp, rgba[3]],
            copy_managed_color(current_color),
            copy_managed_color(current_color)
        ),
        #saturation slider
        ColorSlider(
            self.app, 
            lambda rgba: (
                [*saturation_shift_uv((rgba[0], rgba[1], rgba[2]), 0.0), rgba[3]], 
                [*saturation_shift_uv((rgba[0], rgba[1], rgba[2]), 1.0), rgba[3]],
                to_hsluv((rgba[0],rgba[1],rgba[2]))[1]
            ),
            lambda rgba, color_comp: [
                *saturation_shift_uv((rgba[0], rgba[1], rgba[2]), color_comp), 
                rgba[3]
            ],
            copy_managed_color(current_color),
            copy_managed_color(current_color),
        ),
        #value slider
        ColorSlider(
            self.app, 
            lambda rgba: (
                [0.0, 0.0, 0.0, rgba[3]], 
                [1.0, 1.0, 1.0, rgba[3]],
                to_hsluv((rgba[0],rgba[1],rgba[2]))[2]
            ),
            lambda rgba, color_comp: [
                *value_shift_uv((rgba[0], rgba[1], rgba[2]), color_comp), 
                rgba[3]
            ],
            copy_managed_color(current_color),
            copy_managed_color(current_color),
            False
        )]

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
        self.color_manager.update_color_row()
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
