"""
SPDX-FileCopyrightText: 2019 Tusooa Zhu <tusooa@vista.aero>
SPDX-License-Identifier: GPL-3.0-or-later

This file is based on Krita mixer_slider_docker.
https://invent.kde.org/graphics/krita/-/blob/master/plugins/python/mixer_slider_docker/slider_line.py
"""

try:
    from PyQt6.QtWidgets import QWidget
    from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPolygon
    from PyQt6.QtCore import QPoint, Qt, qDebug
except:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPolygon
    from PyQt5.QtCore import QPoint, Qt, qDebug

from typing import List
from krita import ManagedColor
from .lib_zen import generate_color_gradient

class ColorSlider(QWidget):
    default_color = ManagedColor("", "", "")

    def __init__(
        self, docker, name, left_color=default_color, right_color=default_color, parent=None
    ):
        super(ColorSlider, self).__init__(parent)
        self.docker = docker
        self.name = name
        self.left_color = left_color
        self.right_color = right_color
        self.slider_pixmap = None
        self.value_x = None
        self.cursor_fill_color = QColor.fromRgbF(1, 1, 1, 1)
        self.cursor_outline_color = QColor.fromRgbF(0, 0, 0, 1)
        self.need_redraw = True

    def set_color(self, pos, color):
        if pos == "left":
            self.left_color = color
        else:
            self.right_color = color

        self.need_redraw = True

        r, g, b, a = self.docker.current_color.componentsOrdered()

        if self.name == "r_slider":
            left = self.left_color.componentsOrdered()
            right = self.right_color.componentsOrdered()
            current = self.docker.current_color.componentsOrdered()

        width = self.width()
        if self.name == "r_slider":
            self.value_x = self.adjust_pos_x(r * width)
        elif self.name == "g_slider":
            self.value_x = self.adjust_pos_x(g * width)
        elif self.name == "b_slider":
            self.value_x = self.adjust_pos_x(b * width)

        self.update()

    def update_slider(self):
        """
        Update the slider to a gradient between the two colors.

        The painting of the slider comes from the program Krita. The original code can be accessed
        at the following URL.
        https://github.com/KDE/krita/blob/master/plugins/dockers/advancedcolorselector/kis_shade_selector_line.cpp
        """
        if self.need_redraw:
            patch_count = self.width()

            left_rgba = self.left_color.componentsOrdered()
            right_rgba = self.right_color.componentsOrdered()

            self.slider_pixmap = QPixmap(self.width(), self.height())
            painter = QPainter(self.slider_pixmap)

            gradient = generate_color_gradient(
                (left_rgba[0],left_rgba[1],left_rgba[2]),
                (right_rgba[0],right_rgba[1],right_rgba[2]),
                patch_count
            )

            for i in range(patch_count):
                r, g, b = gradient[i]
                cur_color = QColor.fromRgbF(r, g, b)
                painter.fillRect(i, 0, 1, self.height(), cur_color)

            painter.end()
            self.need_redraw = False

        widget_painter = QPainter(self)
        self.rendered_image = self.slider_pixmap.toImage()
        widget_painter.drawImage(0, 0, self.rendered_image)

        if self.value_x is not None:
            start_x = int(self.value_x)
            start_y = int(self.height() / 2)
            delta_x = int(self.height() / 3)
            delta_y = int(self.height() / 3)
            points = [
                QPoint(start_x, start_y),
                QPoint(start_x - delta_x, start_y + delta_y),
                QPoint(start_x + delta_x, start_y + delta_y),
            ]
            widget_painter.setBrush(QBrush(self.cursor_fill_color))
            widget_painter.setPen(self.cursor_outline_color)
            widget_painter.drawPolygon(QPolygon(points))

    def paintEvent(self, event):
        self.update_slider()

    def resizeEvent(
        self, event
    ):  # after resizing the widget, force-redraw the underlying slider
        self.need_redraw = True

    def adjust_pos_x(self, x):  # adjust the x to make it in the range of [0, width - 1]
        if x < 0:
            return 0
        if x >= self.width():
            return self.width() - 1
        return x

    def mouseMoveEvent(self, event):
        pos = event.pos()
        self.value_x = self.adjust_pos_x(pos.x())
        y = int(self.height() / 2)
        if self.docker.canvas() is not None:
            color = self.docker.current_color
            comps = color.components()
            val = self.value_x / self.width()

            m = max(*comps, val)
            mn = min(*comps, val)

            if self.name == "b_slider":
                comps[0] = val
            if self.name == "g_slider":
                comps[1] = val
            if self.name == "r_slider":
                comps[2] = val

            b, g, r, a = comps

            color.setComponents(comps)
            if self.docker.canvas().view() is not None:
                self.docker.canvas().view().setForeGroundColor(color)

        self.update()

    def mousePressEvent(self, event):
        self.mouseMoveEvent(event)

