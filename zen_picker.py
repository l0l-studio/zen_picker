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

from .docker import Ui_DockWidget


DOCKER_NAME = "zen picker"

instance = Krita.instance()


notifier = instance.notifier()
notifier.setActive(True)

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

        # Settings
        # self.dialog = uic.loadUi( os.path.join( self.directory_plugin, "pigment_o_settings.ui" ), QDialog( self ) )
        # self.dialog.setWindowTitle( "Pigment.O : Settings" )
        # self.dialog.accept() # Hides the Dialog

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
                upper = max(r, g, b)
                lower = min(r, g, b)

                direction = saturation_direction(upper, lower)

                if val != mid_value:
                    if val > mid_value:
                        val = -1 * (val - mid_value)
                    elif val < mid_value:
                        val = 1 * abs(val - mid_value)

                    r = clamp(r - (val * direction(r)))
                    g = clamp(g - (val * direction(g)))
                    b = clamp(b - (val * direction(b)))
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
                    if val > mid_value:
                        val = -1 * (val - mid_value)
                    elif val < mid_value:
                        val = 1 * abs(val - mid_value)

                    r = clamp(r - val)
                    g = clamp(g - val)
                    b = clamp(b - val)
                    color.setRgb(r, g, b, a)

                    getattr(self.ui, "red_label").setText(str(r))
                    getattr(self.ui, "red_slider").setSliderPosition(r)

                    getattr(self.ui, "green_label").setText(str(g))
                    getattr(self.ui, "green_slider").setSliderPosition(g)

                    getattr(self.ui, "blue_label").setText(str(b))
                    getattr(self.ui, "blue_slider").setSliderPosition(b)

            self.setWindowTitle(slider + ":" + str(val))
            getattr(self.ui, slider + "_label").setText(str(val))
            view.setForeGroundColor(ManagedColor.fromQColor(color, view.canvas()))

        return update_rgb

    def slider_to_label(self, slider: str):
        slider_el = getattr(self.ui, slider + "_slider")
        slider_el.valueChanged.connect(self.update_label(slider))

        if slider == "value" or slider == "saturation":
            slider_el.sliderReleased.connect(
                lambda: slider_el.setSliderPosition(mid_value)
            )

    def update_color(self, somedata):
        debug(str(somedata))


def debug(message: str):
    QMessageBox.information(QWidget(), "Warning", message)


def clamp(x: int):
    return max(min(255, x), 0)


def saturation_direction(upper: int, lower: int) -> Callable[[int], int]:
    def direction(color_magnitude: int):
        if color_magnitude == upper:
            return 1
        if color_magnitude == lower:
            return -1
        return 0

    return direction
