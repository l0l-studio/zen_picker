try:
    from PyQt6.QtWidgets import (
        QHBoxLayout, 
        QVBoxLayout,  
        QWidget,
        QScrollArea, 
        QPushButton
    )
    from PyQt6.QtGui import QPixmap, QPainter, QColor
    from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt
except:
    from PyQt5.QtWidgets import (
        QHBoxLayout, 
        QVBoxLayout,  
        QWidget,
        QScrollArea, 
        QPushButton
    )
    from PyQt5.QtGui import QPixmap, QPainter, QColor
    from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

from krita import ManagedColor

from .app import App
from .lib_zen import mix, relative_color_shift
from .utils import q_to_managed_color, managed_to_q_color, delete_layout

modes = {
    "add": 1,
    "remove": -1
}

class ColorBtn(QWidget):
    clicked = pyqtSignal()

    def __init__(self, color: QColor, parent=None):
        super(ColorBtn, self).__init__(parent)
        self.color = color
        self.setFixedHeight(20)

    def set_color(self, qcolor: QColor):
        self.color = qcolor
        self.update()

    def update_color(self):
        color_sq = QPixmap(self.width(), self.height())
        color_sq.fill(self.color)
        image = color_sq.toImage()

        painter = QPainter(self)
        painter.drawImage(0, 0, image)

    def paintEvent(self, event):
        self.update_color()

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

class ColorManager(QWidget):
    def __init__(
        self, app: App, name, parent=None
    ):
        super(ColorManager, self).__init__(parent)

        self.app = app
        self.name = name
        self.mode = modes["add"]

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.local_color_col = QVBoxLayout()
        self.light_color_col = QVBoxLayout()
        self.light_color_top_row = QHBoxLayout()

        self.main_light_color_btn = ColorBtn(
            managed_to_q_color(self.app.canvas, self.app.main_light.color)
        )
        self.ambient_color_btn = ColorBtn(
            managed_to_q_color(self.app.canvas, self.app.ambient_light.color)
        )

        #TODO: replace with icon
        self.add_new_color_btn = QPushButton()
        self.add_new_color_btn.setIcon(self.app.krita_instance.icon("list-add"))
        self.add_new_color_btn.setFixedHeight(20)
        self.add_new_color_btn.clicked.connect(self.slot_add_new_color_btn)

        self.layout.addLayout(self.local_color_col)
        self.layout.addLayout(self.light_color_col)
        self.light_color_col.addLayout(self.light_color_top_row)
        self.light_color_top_row.addWidget(self.main_light_color_btn)
        self.light_color_top_row.addWidget(self.ambient_color_btn)
        self.local_color_col.addWidget(self.add_new_color_btn)

    @pyqtSlot()
    def slot_update_main_light_color(self):
        canvas = self.app.canvas
        if canvas is not None:
            self.main_light_color.set_color(self.dock_widget.canvas().view().foregroundColor())

    @pyqtSlot()
    def slot_update_ambient_color(self):
        if self.dock_widget.canvas() is not None:
            self.ambient_color.set_color(self.dock_widget.canvas().view().foregroundColor())

    @pyqtSlot()
    def slot_add_new_color_btn(self):
        if self.mode == modes["add"]:
            try:
                colors = self.app.try_add_local_color()
                self.render_row(colors)
            except Exception as err:
                pass

    def render_row(self, colors: (ManagedColor, ManagedColor, ManagedColor)):
        local_color, illuminated_color, shadow_color = colors
        q_local_color = managed_to_q_color(self.app.canvas, local_color)
        q_illuminated_color = managed_to_q_color(self.app.canvas, illuminated_color)
        q_shadow_color = managed_to_q_color(self.app.canvas, shadow_color)

        local_color_row = QHBoxLayout()
        color_row = QHBoxLayout()
        light_row = QHBoxLayout()

        color_btns = [
            QPushButton(),
            ColorBtn(q_local_color, self),
            ColorBtn(q_illuminated_color, self),
            ColorBtn(q_illuminated_color, self),
            ColorBtn(q_shadow_color, self),
        ]
        del_row_btn, new_color_btn, new_mixed_color_btn, light_color_btn,shadow_color_btn = color_btns

        del_row_btn.setIcon(self.app.krita_instance.icon("window-close"))
        del_row_btn.setFixedHeight(20)

        def handle_del_row():
            local_color_row.deleteLater()
            color_row.deleteLater()

            for btn in color_btns:
                btn.deleteLater()

            try:
                self.app.try_remove_local_color(local_color)   
            except:
                pass

        def handle_new_color_click():
            self.app.try_set_foreground_color(local_color)

        def handle_light_color_click():
            self.app.try_set_foreground_color(illuminated_color)

        def handle_new_mixed_color_click():
            self.app.try_set_foreground_color(illuminated_color)

        def handle_shadow_color_click():
            self.app.try_set_foreground_color(shadow_color)


        #TODO: mix color light and ambient color by intensity
        # click handlers should behave differently depending on modes
        # edit mode: change light intensity
        # normal mode: use color as foreground color

        del_row_btn.clicked.connect(handle_del_row)
        new_color_btn.clicked.connect(handle_new_color_click)
        light_color_btn.clicked.connect(handle_light_color_click)
        new_mixed_color_btn.clicked.connect(handle_new_mixed_color_click)
        shadow_color_btn.clicked.connect(handle_shadow_color_click)

        self.local_color_col.addLayout(local_color_row)
        self.light_color_col.addLayout(color_row)

        local_color_row.addWidget(del_row_btn)
        local_color_row.addWidget(new_color_btn)

        light_row.addWidget(light_color_btn)
        # light_row.addWidget(new_mixed_color_btn)

        color_row.addLayout(light_row)
        color_row.addWidget(shadow_color_btn)
