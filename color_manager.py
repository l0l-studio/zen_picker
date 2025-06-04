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
    get_color_idx,
    get_managed_color_comps,
    set_managed_color_comps
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
        self.color_lock = False

        self.local_color_col: QVBoxLayout = None
        self.light_color_col: QVBoxLayout = None
        self.main_light_color_btn: ColorBtn = None
        self.ambient_light_color_btn: ColorBtn = None
        self.color_lock_btn: QPushButton = None

        self.color_btns = [
            ColorBtn(QColor.fromRgbF(1.0, 1.0, 1.0), self),
            ColorBtn(QColor.fromRgbF(1.0, 1.0, 1.0), self),
            ColorBtn(QColor.fromRgbF(1.0, 1.0, 1.0), self),
        ]

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.local_color_col = QVBoxLayout()
        self.light_color_col = QVBoxLayout()

        light_color_top_row = QHBoxLayout()

        self.main_light_color_btn = ColorBtn(
            managed_to_q_color(self.app.canvas, self.app.main_light.color)
        )
        self.main_light_color_btn.clicked.connect(self.slot_update_main_light_color)

        self.ambient_light_color_btn = ColorBtn(
            managed_to_q_color(self.app.canvas, self.app.ambient_light.color)
        )
        self.ambient_light_color_btn.clicked.connect(self.slot_update_ambient_color)

        self.color_lock_btn = QPushButton()
        self.color_lock_btn.setIcon(self.app.krita_instance.icon("docker_lock_a"))
        self.color_lock_btn.setFixedHeight(20)
        self.color_lock_btn.clicked.connect(self.slot_lock_color)

        layout.addLayout(self.local_color_col)
        layout.addLayout(self.light_color_col)

        self.local_color_col.addWidget(self.color_lock_btn)
        self.light_color_col.addLayout(light_color_top_row)

        light_color_top_row.addWidget(self.main_light_color_btn)
        light_color_top_row.addWidget(self.ambient_light_color_btn)

        self.render_row()

    @pyqtSlot()
    def slot_update_main_light_color(self):
        match QApplication.keyboardModifiers():
            case Qt.ControlModifier:
                new_color = self.app.try_update_main_light()
                self.main_light_color_btn.color = get_managed_color_comps(new_color)

                local_color = q_to_managed_color(self.app.canvas, self.color_btns[0].color)

                new_illuminated = get_mixed_colors(
                    local_color, 
                    self.app.main_light,
                    True,
                    False
                )

                self.color_btns[1].color = new_illuminated

            case _:
                self.app.try_set_foreground_color(self.app.main_light.color)

    @pyqtSlot()
    def slot_update_ambient_color(self):
        match QApplication.keyboardModifiers():
            case Qt.ControlModifier:
                new_color = self.app.try_update_ambient_light()
                self.ambient_light_color_btn.color = new_color.componentsOrdered()

                local_color = q_to_managed_color(self.app.canvas, self.color_btns[0].color)

                new_shadow = get_mixed_colors(
                    local_color, 
                    self.app.main_light,
                    True,
                    False
                )

                r, g, b, a = get_managed_color_comps(local_color)
                rgb = relative_color_shift((r, g, b), 0.0, 0.2)

                self.color_btns[2].color = [*rgb, a]

            case _:
                self.app.try_set_foreground_color(self.app.ambient_light.color)

    @pyqtSlot()
    def slot_lock_color(self):
        self.color_lock = not self.color_lock

        if self.color_lock:
            self.color_lock_btn.setIcon(self.app.krita_instance.icon("docker_lock_b"))
        else:
            self.color_lock_btn.setIcon(self.app.krita_instance.icon("docker_lock_a"))


    def update_color_row(self):
        if self.color_lock:
            return

        managed_colors = self.app.current_color_mix
        color_btns = self.color_btns

        for i, btn in enumerate(color_btns):
            btn.color = get_managed_color_comps(managed_colors[i])

    def render_row(self):
        local_color_row = QHBoxLayout()
        color_row = QHBoxLayout()
        light_row = QHBoxLayout()

        local_color_btn, illuminated_color_btn, shadow_color_btn = self.color_btns

        def handle_new_color_click():
            self.app.try_set_foreground_color(
                q_to_managed_color(self.app.canvas, local_color_btn.color)
            )

        def handle_light_color_click():
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

        local_color_btn.clicked.connect(handle_new_color_click)
        illuminated_color_btn.clicked.connect(handle_light_color_click)
        shadow_color_btn.clicked.connect(handle_shadow_color_click)

        self.local_color_col.addLayout(local_color_row)
        self.light_color_col.addLayout(color_row)

        local_color_row.addWidget(local_color_btn)

        light_row.addWidget(illuminated_color_btn)

        color_row.addLayout(light_row)
        color_row.addWidget(shadow_color_btn)
