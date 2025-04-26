try:
    from PyQt6.QtWidgets import (
        QHBoxLayout, 
        QVBoxLayout,  
        QWidget,
        QScrollArea, 
        QPushButton,
        QApplication
    )
    from PyQt6.QtGui import QPixmap, QPainter, QColor
    from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt
except:
    from PyQt5.QtWidgets import (
        QHBoxLayout, 
        QVBoxLayout,  
        QWidget,
        QScrollArea, 
        QPushButton,
        QApplication
    )
    from PyQt5.QtGui import QPixmap, QPainter, QColor
    from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

from krita import ManagedColor

from .app import App
from .lib_zen import mix, relative_color_shift
from .utils import (
    q_to_managed_color, 
    managed_to_q_color, 
    delete_layout,
    get_mixed_colors,
    get_color_idx
)

modes = {
    "add": 1,
    "remove": -1
}

class ColorBtn(QWidget):
    clicked = pyqtSignal()

    def __init__(self, color: QColor, parent=None):
        super(ColorBtn, self).__init__(parent)
        self.__color = color
        self.setFixedHeight(20)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color_comps: list[float]):
        r, g, b, _ = color_comps
        self.__color.setRgbF(r, g, b)
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
        self.color_rows: list[(ManagedColor, ColorBtn, ColorBtn)] = []

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.local_color_col = QVBoxLayout()
        self.light_color_col = QVBoxLayout()
        self.light_color_top_row = QHBoxLayout()

        self.main_light_color_btn = ColorBtn(
            managed_to_q_color(self.app.canvas, self.app.main_light.color)
        )
        self.main_light_color_btn.clicked.connect(self.slot_update_main_light_color)

        self.ambient_light_color_btn = ColorBtn(
            managed_to_q_color(self.app.canvas, self.app.ambient_light.color)
        )
        self.ambient_light_color_btn.clicked.connect(self.slot_update_ambient_color)

        #TODO: replace with icon
        self.add_new_color_btn = QPushButton()
        self.add_new_color_btn.setIcon(self.app.krita_instance.icon("list-add"))
        self.add_new_color_btn.setFixedHeight(20)
        self.add_new_color_btn.clicked.connect(self.slot_add_new_color_btn)

        self.layout.addLayout(self.local_color_col)
        self.layout.addLayout(self.light_color_col)
        self.light_color_col.addLayout(self.light_color_top_row)
        self.light_color_top_row.addWidget(self.main_light_color_btn)
        self.light_color_top_row.addWidget(self.ambient_light_color_btn)
        self.local_color_col.addWidget(self.add_new_color_btn)

    @pyqtSlot()
    def slot_update_main_light_color(self):
        match QApplication.keyboardModifiers():
            case Qt.ControlModifier:
                #TODO: pass qcolor references to update
                new_color = self.app.try_update_main_light()
                self.main_light_color_btn.color = new_color.componentsOrdered()

                for color_btn_row in self.color_rows:
                    local_color, illuminated_btn, shadow_btn = color_btn_row

                    new_illuminated, _ = get_mixed_colors(
                        local_color, 
                        (self.app.main_light, self.app.ambient_light),
                        True,
                        False
                    )

                    illuminated_btn.color = new_illuminated
            case _:
                self.app.try_set_foreground_color(self.app.main_light.color)

    @pyqtSlot()
    def slot_update_ambient_color(self):
        match QApplication.keyboardModifiers():
            case Qt.ControlModifier:
                new_color = self.app.try_update_ambient_light()
                self.ambient_light_color_btn.color = new_color.componentsOrdered()

                for color_btn_row in self.color_rows:
                    local_color, illuminated_btn, shadow_btn = color_btn_row

                    _, new_shadow = get_mixed_colors(
                        local_color, 
                        (self.app.main_light, self.app.ambient_light),
                        True,
                        False
                    )

                    shadow_btn.color = new_shadow
            case _:
                self.app.try_set_foreground_color(self.app.ambient_light.color)

    @pyqtSlot()
    def slot_add_new_color_btn(self):
        if self.mode == modes["add"]:
            managed_colors = self.app.try_add_local_color()

            local_color, illuminated_color, shadow_color = managed_colors
            q_local_color = managed_to_q_color(self.app.canvas, local_color)
            q_illuminated_color = managed_to_q_color(self.app.canvas, illuminated_color)
            q_shadow_color = managed_to_q_color(self.app.canvas, shadow_color)

            q_colors = (q_local_color, q_illuminated_color, q_shadow_color)

            self.color_rows.append(self.render_row(managed_colors, q_colors))

    def remove_row(self, color: ManagedColor):
        self.app.try_remove_local_color(color)

        colors = self.color_rows

        idx = get_color_idx(color, colors)
        if idx == -1:
            raise ValueError("id not found in local_color list")

        if len(colors) > 1:
            colors[idx], colors[-1] = colors[-1], colors[idx]
        colors.pop()


    def render_row(self, m_colors: (ManagedColor,ManagedColor,ManagedColor), q_colors: (QColor, QColor, QColor)) -> (ManagedColor, ColorBtn, ColorBtn):
        local_color, illuminated_color, shadow_color = m_colors
        q_local_color, q_illuminated_color, q_shadow_color = q_colors

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
        del_row_btn, local_color_btn, new_mixed_color_btn, illuminated_color_btn,shadow_color_btn = color_btns

        del_row_btn.setIcon(self.app.krita_instance.icon("window-close"))
        del_row_btn.setFixedHeight(20)

        def handle_del_row():
            local_color_row.deleteLater()
            color_row.deleteLater()

            for btn in color_btns:
                btn.deleteLater()

            self.remove_row(local_color)   

        #TODO: update click handlers? move logic to ColorBtns
        def handle_new_color_click():
            self.app.try_set_foreground_color(
                q_to_managed_color(self.app.canvas, local_color_btn.color)
            )

        def handle_light_color_click():
            self.app.try_set_foreground_color(
                q_to_managed_color(self.app.canvas, illuminated_color_btn.color)
            )

        def handle_new_mixed_color_click():
            self.app.try_set_foreground_color(
                q_to_managed_color(self.app.canvas, illuminated_color_btn.color)
            )

        def handle_shadow_color_click():
            self.app.try_set_foreground_color(
                q_to_managed_color(self.app.canvas, shadow_color_btn.color)
            )


        #TODO: mix color light and ambient color by intensity
        # click handlers should behave differently depending on modes
        # edit mode: change light intensity
        # normal mode: use color as foreground color

        del_row_btn.clicked.connect(handle_del_row)
        local_color_btn.clicked.connect(handle_new_color_click)
        illuminated_color_btn.clicked.connect(handle_light_color_click)
        new_mixed_color_btn.clicked.connect(handle_new_mixed_color_click)
        shadow_color_btn.clicked.connect(handle_shadow_color_click)

        self.local_color_col.addLayout(local_color_row)
        self.light_color_col.addLayout(color_row)

        local_color_row.addWidget(del_row_btn)
        local_color_row.addWidget(local_color_btn)

        light_row.addWidget(illuminated_color_btn)
        # light_row.addWidget(new_mixed_color_btn)

        color_row.addLayout(light_row)
        color_row.addWidget(shadow_color_btn)

        return (local_color, illuminated_color_btn, shadow_color_btn)
