try:
    from PyQt6.QtWidgets import QWidget
    from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPolygon
    from PyQt6.QtCore import QPoint, Qt 
except:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPolygon
    from PyQt5.QtCore import QPoint, Qt

from krita import ManagedColor
from .lib_zen import generate_color_gradient, color_shift

class NudgeSlider(QWidget):
    default_color = ManagedColor("", "", "")

    def __init__(
        self, docker, name, left_color=default_color, right_color=default_color, parent=None
    ):
        super(NudgeSlider, self).__init__(parent)
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
            val = self.value_x
            mid_value = self.width() // 2

            comps = color.componentsOrdered()

            if val != mid_value:
                if val < mid_value:
                    val = -1 * abs(val - mid_value)
                elif val > mid_value:
                    val = 1 * abs(val - mid_value)

            # self.docker.debug_label.setText(str(b)+str(g)+str(r)+str(a))
            width = self.width() * 13
            if self.name == "saturation_slider":
                (r, g, b) = color_shift((comps[0], comps[1], comps[2]), float(val / width), 0.0)
                comps[0] = b
                comps[1] = g
                comps[2] = r
            if self.name == "value_slider":
                (r, g, b) = color_shift((comps[0], comps[1], comps[2]), 0.0, float(val / width))
                comps[0] = b
                comps[1] = g
                comps[2] = r

            color.setComponents(comps)
            if self.docker.canvas().view() is not None:
                self.docker.canvas().view().setForeGroundColor(color)

        self.update()

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        self.value_x = self.width() // 2
        self.update()

