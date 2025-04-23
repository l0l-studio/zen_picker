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
from .app import App
from .utils import UnimplementedError

class NudgeSlider(QWidget):
    default_color = ManagedColor("", "", "")

    def __init__(
        self, app: App, name, left_color=default_color, right_color=default_color, parent=None
    ):
        super(NudgeSlider, self).__init__(parent)
        self.app = app
        self.name = name
        self.left_color = left_color
        self.right_color = right_color
        self.slider_pixmap = None
        self.value_x = None
        self.cursor_fill_color = QColor.fromRgbF(1, 1, 1, 1)
        self.cursor_outline_color = QColor.fromRgbF(0, 0, 0, 1)
        self.need_redraw = True

        self.setMaximumHeight(30)
        self.setMinimumHeight(20)

        self.update_color()

    def update_color(self):
        r, g, b, a = self.app.current_color.componentsOrdered()
        l_r, l_g, l_b = 0.0, 0.0, 0.0
        r_r, r_g, r_b = 0.0, 0.0, 0.0

        if self.name == "saturation_slider":
            l_r, l_g, l_b = color_shift((r, g, b), -1.0, 0.0)
            r_r, r_g, r_b = color_shift((r, g, b), 1.0, 0.0)
        #TODO: clamp value range
        elif self.name == "value_slider":
            l_r, l_g, l_b = color_shift((r, g, b), 0.0, -1.0)
            r_r, r_g, r_b = color_shift((r, g, b), 0.0, 1.0)
        else:
            raise UnimplementedError("unimplemented update_color behavior for: "+ self.name)

        self.left_color.setComponents([l_b, l_g, l_r, a])
        self.right_color.setComponents([r_b, r_g, r_r, a])

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
        if canvas is not None:
            color = self.app.current_color
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
            view = canvas.view()
            if view is not None:
                view.setForeGroundColor(color)

        self.update()

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        self.value_x = self.width() // 2
        self.update()

