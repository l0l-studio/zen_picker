"""
SPDX-FileCopyrightText: 2019 Tusooa Zhu <tusooa@vista.aero>
SPDX-License-Identifier: GPL-3.0-or-later

This file is based on Krita mixer_slider_docker.
https://invent.kde.org/graphics/krita/-/blob/master/plugins/python/mixer_slider_docker/slider_line.py
"""

try:
    from PyQt6.QtWidgets import QWidget, QHBoxLayout
    from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPolygon
    from PyQt6.QtCore import QPoint, Qt, qDebug
except:
    from PyQt5.QtWidgets import QWidget, QHBoxLayout
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPolygon
    from PyQt5.QtCore import QPoint, Qt, qDebug

from typing import List, Callable
from krita import ManagedColor
from .lib_zen import generate_color_gradient, clamp, match_value
from .app import App
from .utils import (
    UnimplementedError, 
    copy_managed_color,
    get_managed_color_comps,
    set_managed_color_comps
)

class ColorSlider(QWidget):
    default_left_color = ManagedColor("", "", "")
    default_right_color = ManagedColor("", "", "")

    def __init__(
        self, app: App, 
        update_slider_color: Callable[
            [tuple[float, float, float, float]],
            tuple[list[float], list[float], float]
        ],
        update_krita_color: Callable[
            [list[float], float],
            list[float]
        ],
        left_color=default_left_color,
        right_color=default_right_color,
        luminosity_lock = True,
        parent=None
    ):
        super(ColorSlider, self).__init__()
        self.app = app
        self.left_color = left_color
        self.right_color = right_color
        self.luminosity_lock = luminosity_lock

        self.slider_pixmap = None
        self.value_x: None | int = None
        self.cursor_fill_color = QColor.fromRgbF(1, 1, 1, 1)
        self.cursor_outline_color = QColor.fromRgbF(0, 0, 0, 1)
        self.need_redraw = True
        self.color_to_match: None | ManagedColor = None
        self.update_slider_color = update_slider_color
        self.update_krita_color = update_krita_color 
        self.rendered_image = None
        self.slider_pixmap = None

        self.setMaximumHeight(30)
        self.setMinimumHeight(20)

    def update_color(self):
        rgba = self.app.current_color(True)
        width = self.width()
        left, right, color_comp = self.update_slider_color((*rgba,))

        self.left_color = set_managed_color_comps(
            self.left_color,
            left if not self.luminosity_lock else [*match_value(
                (*rgba[:3],),
                (*left[:3],)
            ), rgba[3]]
        ) 
        self.right_color = set_managed_color_comps(
            self.right_color,
            right if not self.luminosity_lock else [*match_value(
                (*rgba[:3],), 
                (*right[:3],)
            ), rgba[3]]
        ) 
        self.value_x = self.adjust_pos_x(color_comp * width)

        self.need_redraw = True
        self.update()

    def update_slider(self):
        """
        Update the slider to a gradient between the two colors.

        The painting of the slider comes from the program Krita. The original code can be accessed
        at the following URL.
        https://github.com/KDE/krita/blob/master/plugins/dockers/advancedcolorselector/kis_shade_selector_line.cpp
        """

        width = self.width()
        height = self.height()
        if self.need_redraw:
            patch_count = width

            left_rgba = get_managed_color_comps(self.left_color)
            right_rgba = get_managed_color_comps(self.right_color)

            self.slider_pixmap = QPixmap(width, height)
            painter = QPainter(self.slider_pixmap)

            gradient = generate_color_gradient(
                (left_rgba[0],left_rgba[1],left_rgba[2]),
                (right_rgba[0],right_rgba[1],right_rgba[2]),
                patch_count
            )

            for i in range(patch_count):
                r, g, b = gradient[i]
                cur_color = QColor.fromRgbF(r, g, b)
                painter.fillRect(i, 0, 1, height, cur_color)

            painter.end()
            self.need_redraw = False

        widget_painter = QPainter(self)
        if self.slider_pixmap is not None:
            self.rendered_image = self.slider_pixmap.toImage()
        widget_painter.drawImage(0, 0, self.rendered_image)

        if self.value_x is not None:
            start_x = int(self.value_x)
            start_y = int(height / 2)
            delta_x = int(height / 3)
            delta_y = int(height / 3)
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
        canvas = self.app.canvas
        view = canvas.view()

        if canvas is not None and view is not None:
            rgba = get_managed_color_comps(self.app.color_to_match)
            val = self.value_x / self.width()
            val = clamp(val, 0.02, 0.98)

            _rgba = self.update_krita_color(rgba, val)

            if self.luminosity_lock:
                _rgba = match_value((*rgba[:3],), (*_rgba[:3],))

            color = copy_managed_color(self.app.current_color())
            color = set_managed_color_comps(color, [*_rgba[:3], rgba[3]])
            view.setForeGroundColor(color)

        self.update()

    def mousePressEvent(self, event):
        self.app.color_to_match = copy_managed_color(self.app.current_color())
        self.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.app.color_to_match = None
