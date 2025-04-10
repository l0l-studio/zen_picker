from typing import Callable

from PyQt5.uic.properties import QtWidgets
from krita import DockWidget
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import QSysInfo, Qt
from PyQt5.QtWidgets import (
    QLabel,
    QMessageBox,
    QWidget,
    QDialog,
    QFrame,
    QApplication,
    QSlider,
)
import os
from krita import ManagedColor
from .lib_zen import sum_as_string

from .lib_zen import clamp, color_shift
from .docker import Ui_DockWidget


DOCKER_NAME = "zen picker"
instance = Krita.instance()


notifier = instance.notifier()
notifier.setActive(True)

# constants
mid_value = 25


class ZenDocker(DockWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle(DOCKER_TITLE)
        self.SetupUI()
        self.Connections()

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass

    def SetupUI(self):
        # Operating System
        self.OS = str(QSysInfo.kernelType())  # WINDOWS=winnt & LINUX=linux
        if self.OS == "winnt":  # Unlocks icons in Krita for Menu Mode
            QApplication.setAttribute(Qt.AA_DontShowIconsInMenus, False)

        # Path Name
        self.plugin_dir = str(os.path.dirname(os.path.realpath(__file__)))

        # Widget Docker
        docker_ui = Ui_DockWidget()
        docker_ui.setupUi(self)
        self.ui = docker_ui

        # Window
        self.setWindowTitle(DOCKER_NAME)

        self.slider_to_label("red")
        self.slider_to_label("green")
        self.slider_to_label("blue")
        self.slider_to_label("saturation")
        self.slider_to_label("value")

        self.color_saturation = 50
        self.color_value = 50

        # QMessageBox.information(QWidget(), "Warning", str(dir(self.ui)))

    def Connections(self):
        pass

    def update_label(self, slider: str) -> Callable[[int], None]:
        def update_rgb(val: int):
            view = instance.activeWindow().activeView()

            color = QtGui.QColor(
                view.foregroundColor().colorForCanvas(view.canvas()).name()
            )

            if slider == "red":
                color.setRed(val)

            elif slider == "green":
                color.setGreen(val)

            elif slider == "blue":
                color.setBlue(val)

            elif slider == "saturation":
                r, g, b, a = color.getRgb()

                if val != mid_value:
                    if val < mid_value:
                        val = -1 * abs(val - mid_value)
                    elif val > mid_value:
                        val = 1 * abs(val - mid_value)

                    (r, g, b) = color_shift((r, g, b), float(val / 255), 0.0)
                    color.setRgb(r, g, b, a)

                    getattr(self.ui, "red_label").setText(str(r))
                    getattr(self.ui, "red_slider").setSliderPosition(r)

                    getattr(self.ui, "green_label").setText(str(g))
                    getattr(self.ui, "green_slider").setSliderPosition(g)

                    getattr(self.ui, "blue_label").setText(str(b))
                    getattr(self.ui, "blue_slider").setSliderPosition(b)

            elif slider == "value":
                r, g, b, a = color.getRgb()

                if val != mid_value:
                    if val < mid_value:
                        val = -1 * abs(val - mid_value)
                    elif val > mid_value:
                        val = 1 * abs(val - mid_value)

                    (r, g, b) = color_shift((r, g, b), 0.0, float(val / 500))
                    color.setRgb(r, g, b, a)

                    getattr(self.ui, "red_label").setText(str(r))
                    getattr(self.ui, "red_slider").setSliderPosition(r)

                    getattr(self.ui, "green_label").setText(str(g))
                    getattr(self.ui, "green_slider").setSliderPosition(g)

                    getattr(self.ui, "blue_label").setText(str(b))
                    getattr(self.ui, "blue_slider").setSliderPosition(b)

            # self.setWindowTitle(slider + ":" + str(val))
            getattr(self.ui, slider + "_label").setText(str(val))
            view.setForeGroundColor(ManagedColor.fromQColor(color, view.canvas()))

        return update_rgb

    def slider_to_label(self, slider_prefix: str):
        slider = getattr(self.ui, slider_prefix + "_slider")

        if slider_prefix == "value" or slider_prefix == "saturation":
            slider.setPageStep(0)

        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
                border-radius: 3px;
            }
        """)

        slider.valueChanged.connect(self.update_label(slider_prefix))

        if slider_prefix == "value" or slider_prefix == "saturation":
            slider.sliderReleased.connect(lambda: slider.setSliderPosition(mid_value))

    def update_color(self, somedata):
        debug(str(somedata))


def debug(message: str):
    QMessageBox.information(QWidget(), "Warning", message)
