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

        self.color_saturation = 1
        self.color_value = 0

        # QMessageBox.information(QWidget(), "Warning", str(dir(self.ui)))

        # Settings
        # self.dialog = uic.loadUi( os.path.join( self.directory_plugin, "pigment_o_settings.ui" ), QDialog( self ) )
        # self.dialog.setWindowTitle( "Pigment.O : Settings" )
        # self.dialog.accept() # Hides the Dialog

    def Connections(self):
        pass
        # i = 0
        # for item in dir(self):
        #     i += 1

        # QMessageBox.information(QWidget(), "Warning", str(i))

    def update_label(self, slider: str) -> Callable[[int], None]:
        def update(val: int):
            view = instance.activeWindow().activeView()

            color = QtGui.QColor(
                view.foregroundColor().colorForCanvas(view.canvas()).name()
            )

            if slider == "red":
                color.setRed(val)
                h, s, v, a = color.getHsv()
                color = QtGui.QColor.fromHsv(
                    h, self.color_saturation, self.color_value, a
                )

            elif slider == "green":
                color.setGreen(val)
                h, s, v, a = color.getHsv()
                color = QtGui.QColor.fromHsv(
                    h, self.color_saturation, self.color_value, a
                )

            elif slider == "blue":
                color.setBlue(val)
                h, s, v, a = color.getHsv()
                color = QtGui.QColor.fromHsv(
                    h, self.color_saturation, self.color_value, a
                )

            elif slider == "saturation" or slider == "value":
                h, s, v, a = color.getHsv()

                if slider == "saturation":
                    self.color_saturation = s
                    color = QtGui.QColor.fromHsv(h, val, v, a)
                else:
                    self.color_value = v
                    color = QtGui.QColor.fromHsv(h, s, val, a)

                for rgb_slider in ["red", "green", "blue"]:
                    color_val = getattr(color, rgb_slider)()
                    getattr(self.ui, rgb_slider + "_label").setText(str(color_val))
                    getattr(self.ui, rgb_slider + "_slider").setValue(color_val)

            self.setWindowTitle(slider + ":" + str(getattr(color, slider)()))

            getattr(self.ui, slider + "_label").setText(str(val))

            view.setForeGroundColor(ManagedColor.fromQColor(color, view.canvas()))

        return update

    def slider_to_label(self, slider: str):
        slider_el = getattr(self.ui, slider + "_slider")
        slider_el.valueChanged.connect(self.update_label(slider))


def debug(message: str):
    QMessageBox.information(QWidget(), "Warning", message)
