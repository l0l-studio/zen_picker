from typing import Literal
try:
    from PyQt6.QtWidgets import QWidget
    from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPolygon
    from PyQt6.QtCore import QPoint, Qt 
except:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPolygon
    from PyQt5.QtCore import QPoint, Qt

from krita import ManagedColor
from .lib_zen import (
    generate_color_gradient, 
    color_shift, 
    value_shift,
    saturation_shift
)
from .app import App
from .utils import UnimplementedError

class RangeSlider(QWidget):
    default_color = ManagedColor("", "", "")

    def __init__(
        self, app: App, 
        name, 
        left_color: ManagedColor = default_color,
        right_color: ManagedColor = default_color, 
        lower_limit = 0, 
        upper_limit = 0, 
        parent = None
    ):
        super(RangeSlider, self).__init__()
        self.app = app
        self.name = name
        self.left_color = left_color
        self.right_color = right_color
        self.slider_pixmap = None
        self.rendered_image = None
        self.cursor_fill_color = QColor.fromRgbF(1, 1, 1, 1)
        self.cursor_outline_color = QColor.fromRgbF(0, 0, 0, 1)
        self.need_redraw = True

        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

        self.editing: None | Literal['lower'] | Literal['upper'] = None

        self.setMaximumHeight(30)
        self.setMinimumHeight(20)
        self.setMaximumWidth(1000)

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

            left_rgba = self.left_color.componentsOrdered()
            right_rgba = self.right_color.componentsOrdered()

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

        if self.lower_limit is not None:
            start_x = int(self.lower_limit)
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

        if self.upper_limit is not None:
            start_x = int(self.upper_limit)
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

        (lower, upper) = self.app.value_range
        self.lower_limit = self.width() * lower
        self.upper_limit = self.width() * upper

        self.need_redraw = True

    def adjust_pos_x_for(self, x: int , limiter: str) -> int:
        lower, upper = 0, self.width()

        if limiter == "lower":
            upper = self.upper_limit - 5
        elif limiter == "upper" :
            lower = self.lower_limit + 5

        if x < lower:
            return lower
        if x >= upper:
            return upper - 1

        return x

    def mouseMoveEvent(self, event):
        pos = event.pos().x()
        width = self.width()

        if self.editing is None:
            distance_lower = abs(self.lower_limit - pos)
            distance_upper = abs(self.upper_limit - pos)

            if distance_lower < distance_upper:
                self.editing = "lower"
            else:
                self.editing = "upper"
        else:
            if self.editing == "lower":
                self.lower_limit = self.adjust_pos_x_for(pos, "lower")
            else:
                self.upper_limit = self.adjust_pos_x_for(pos, "upper")

        (lower, upper) = self.app.value_range
        self.app.value_range = (self.lower_limit / width, self.upper_limit / width)

        self.update()

    def mouseReleaseEvent(self, event):
        self.editing = None
        self.update()

