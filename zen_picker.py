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

from .lib_zen import color_shift
from .slider_row import SliderLine
from .color_slider import ColorSlider
from .nudge_slider import NudgeSlider
from .color_square import ColorManager

# constants
PLUGIN_NAME = "zen picker"
krita_instance = Krita.instance()
notifier = krita_instance.notifier()
notifier.setActive(True)
mid_value = 25
sync_interval = 30


class ZenDocker(DockWidget):
    def __init__(self):
        super().__init__()

        self.setup_ui()

        self.Init_Sync_Timer()

    def canvasChanged(self, canvas):
        pass

    def setup_ui(self):
        current_settings = krita_instance.readSetting(
            "",
            settings("colors"),
            "RGBA,U8,sRGB-elle-V2-srgbtrc.icc,1,0.8,0.4,1|"
            + "RGBA,U8,sRGB-elle-V2-srgbtrc.icc,0,0.8,0.4,1",
        )  # alpha=1 == non-transparent

        self.default_left_color = self.qcolor_to_managedcolor(
            QColor.fromRgbF(0.4, 0.8, 1, 1)
        )
        self.default_right_color = self.qcolor_to_managedcolor(
            QColor.fromRgbF(0, 0, 0, 1)
        )

        self.current_color = self.default_left_color

        self.widget = QWidget()
        self.sliders = []
        self.top_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()

        self.settings_button = QPushButton()
        icon = krita_instance.icon("showColoring")
        self.settings_button.setIcon(icon)
        self.settings_button.setToolTip(i18n("Change settings"))
        self.settings_button.setMaximumSize(30, 30)

        # self.debug_label = QLabel()
        # self.main_layout.addWidget(self.debug_label)

        self.color_manager = ColorManager(
            self, 
            "color_manager"
        )
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.color_manager)
        scroll_area.setWidgetResizable(True)

        self.top_layout.addWidget(scroll_area)

        self.slider_layout = QVBoxLayout()
        self.slider_layout.setSpacing(0)

        self.top_layout.setAlignment(Qt.AlignTop)
        self.top_layout.addLayout(self.main_layout)
        self.main_layout.addLayout(self.slider_layout)
        self.main_layout.addWidget(self.settings_button)

        # for line in current_settings.split(";"):
        #     colors = line.split("|")
        #     if len(colors) < 2:  # discard old configurations
        #         continue
        #     left_color = self.parse_color(colors[0].split(","))
        #     right_color = self.parse_color(colors[1].split(","))
        #     widget = SliderLine(left_color, right_color, self)
        #     self.sliders.append(widget)
        #     self.layout.addWidget(widget)

        color_model = self.current_color.colorModel()
        color_depth = self.current_color.colorDepth()
        color_profile = self.current_color.colorProfile()
        b, g, r, a = self.current_color.components()

        for i in range(3):
            left_color = ManagedColor(color_model, color_depth, color_profile)
            right_color = ManagedColor(color_model, color_depth, color_profile)
            name = ""
            left_comps = [b, g, r, a]
            right_comps = [b, g, r, a]
            if i == 0:
                name = "r_slider"
                left_comps[2] = 0.0
                right_comps[2] = 1.0
            elif i == 1:
                name = "g_slider"
                left_comps[1] = 0.0
                right_comps[1] = 1.0
            else:
                name = "b_slider"
                left_comps[0] = 0.0
                right_comps[0] = 1.0


            left_color.setComponents(left_comps)
            right_color.setComponents(right_comps)

            widget = SliderLine(
                left_color, 
                right_color, 
                self, 
                name,
                ColorSlider(self, name)
            )
            self.sliders.append(widget)
            self.slider_layout.addWidget(widget)

        self.saturation_slider = SliderLine(
                left_color, 
                right_color, 
                self, 
                name,
                NudgeSlider(self, "saturation_slider")
        )

        self.value_slider = SliderLine(
                left_color, 
                right_color, 
                self, 
                name,
                NudgeSlider(self, "value_slider")
        )

        self.slider_layout.addWidget(self.saturation_slider)
        self.slider_layout.addWidget(self.value_slider)

        self.widget.setLayout(self.top_layout)
        self.setWindowTitle(i18n("zen picker"))
        self.setWidget(self.widget)
        [x.show() for x in self.sliders]
        self.saturation_slider.show()
        self.value_slider.show()

    def Connections(self):
        pass

    def Init_Sync_Timer(self):
        self.timer_pulse = QTimer(self)
        self.timer_pulse.timeout.connect(self.Sync)
        self.timer_pulse.start(sync_interval)

    def Sync(self):
        if (self.canvas() is not None) and (self.canvas().view() is not None):
            color_fg = krita_instance.activeWindow().activeView().foregroundColor()
            color_bg = krita_instance.activeWindow().activeView().backgroundColor()

            self.current_color = color_fg
            r_slider, g_slider, b_slider = self.sliders
            r, g, b, a = color_fg.componentsOrdered()

            b_slider.update_color("left", [0.0, g, r, a])
            b_slider.update_color("right", [1.0, g, r, a])

            g_slider.update_color("left", [b, 0.0, r, a])
            g_slider.update_color("right", [b, 1.0, r, a])

            r_slider.update_color("left", [b, g, 0.0, a])
            r_slider.update_color("right", [b, g, 1.0, a])


    def write_settings(self):
        setting = ";".join(
            [
                self.color_to_settings(line.left)
                + "|"
                + self.color_to_settings(line.right)
                for line in self.sliders
            ]
        )

        krita_instance.writeSetting("", settings("colors"), setting)

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

    def parse_color(self, array):
        color = ManagedColor(array[0], array[1], array[2])
        color.setComponents([float(x) for x in array[3:]])
        return color

    def qcolor_to_managedcolor(self, qcolor):
        mc = ManagedColor.fromQColor(qcolor, self.canvas())
        return mc

    def managedcolor_to_qcolor(self, managedcolor):
        return managedcolor.colorForCanvas(self.canvas())


def settings(name: str):
    return PLUGIN_NAME + name


Application.addDockWidgetFactory(
    DockWidgetFactory(
        "zen_picker_docker",
        DockWidgetFactoryBase.DockPosition.DockRight,
        ZenDocker,
    )
)
