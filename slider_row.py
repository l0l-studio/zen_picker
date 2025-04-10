"""
SPDX-FileCopyrightText: 2019 Tusooa Zhu <tusooa@vista.aero>
SPDX-License-Identifier: GPL-3.0-or-later


This file is based on Krita mixer_slider_docker.
https://invent.kde.org/graphics/krita/-/blob/master/plugins/python/mixer_slider_docker/slider_line.py
"""

try:
    from PyQt6.QtWidgets import QHBoxLayout, QWidget
    from PyQt6.QtGui import QPixmap, QPainter
    from PyQt6.QtCore import pyqtSlot, pyqtSignal
except:
    from PyQt5.QtWidgets import QHBoxLayout, QWidget
    from PyQt5.QtGui import QPixmap, QPainter
    from PyQt5.Qt import pyqtSlot, pyqtSignal

from typing import List

from .color_slider import ColorSlider


class SliderLine(QWidget):
    def __init__(self, left_color, right_color, docker, name, slider, parent=None):
        super(SliderLine, self).__init__(parent)
        self.docker = docker
        self.name = name
        self.slider = slider
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.layout)
        self.layout.addWidget(self.slider)
        self.left = left_color
        self.right = right_color
        self.slider.set_color("left", left_color)
        self.slider.set_color("right", right_color)
        self.slider.setMaximumHeight(30)
        self.slider.setMinimumHeight(20)


    def set_color(self, pos, color):
        if pos == "left":
            self.left = color
        else:
            self.right = color

        self.slider.set_color(pos, color)

    def update_color(self, pos, components: List[float]):
        color = self.left
        if pos == "left":
            self.left.setComponents(components) 
            color = self.left
        else:
            self.right.setComponents(components) 
            color = self.right

        self.slider.set_color(pos, color)

    @pyqtSlot()
    def slot_update_left_color(self):
        if self.docker.canvas() is not None:
            if self.docker.canvas().view() is not None:
                self.set_color("left", self.docker.canvas().view().foregroundColor())
        self.slider.value_x = 0  # set the cursor to the left-most
        self.slider.update()
        self.docker.write_settings()

    @pyqtSlot()
    def slot_update_right_color(self):
        if self.docker.canvas() is not None:
            if self.docker.canvas().view() is not None:
                self.set_color("right", self.docker.canvas().view().foregroundColor())
        self.slider.value_x = self.slider.width() - 1
        self.slider.update()
        self.docker.write_settings()
