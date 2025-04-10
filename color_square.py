try:
    from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout,  QWidget, QScrollArea
    from PyQt6.QtGui import QPixmap, QPainter, QColor
    from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt
except:
    from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QScrollArea
    from PyQt5.QtGui import QPixmap, QPainter, QColor
    from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

from .lib_zen import mix, relative_color_shift

modes = {
    "add": 1,
    "remove": -1
}

class ColorBtn(QWidget):
    clicked = pyqtSignal()

    def __init__(self, docker, color, parent=None):
        super(ColorBtn, self).__init__(parent)
        self.color = color
        self.docker = docker
        self.setFixedHeight(20)
        # self.setFixedWidth(30)

    def set_color(self, qcolor):
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
    light_color = QColor.fromRgb(230, 205, 167)
    ambient_color = QColor.fromRgb(73, 120, 234)

    def __init__(
        self, docker, name, parent=None
    ):
        super(ColorManager, self).__init__(parent)
        self.docker = docker
        self.name = name
        self.mode = modes["add"]

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.local_color_col = QVBoxLayout()
        self.light_color_col = QVBoxLayout()
        self.light_color_top_row = QHBoxLayout()

        self.main_light_color_btn = ColorBtn(docker, self.light_color)
        self.ambient_color_btn = ColorBtn(docker, self.ambient_color)

        #TODO: replace with icon
        self.add_new_color_btn = ColorBtn(docker, self.light_color)
        self.add_new_color_btn.clicked.connect(self.slot_add_new_color_btn)

        self.layout.addLayout(self.local_color_col)
        self.layout.addLayout(self.light_color_col)
        self.light_color_col.addLayout(self.light_color_top_row)
        self.light_color_top_row.addWidget(self.main_light_color_btn)
        self.light_color_top_row.addWidget(self.ambient_color_btn)
        self.local_color_col.addWidget(self.add_new_color_btn)

        #TODO: save per .krita file
        self.saved_colors = []


    @pyqtSlot()
    def slot_update_main_light_color(self):
        if self.docker.canvas() is not None:
            self.main_light_color.set_color(self.docker.canvas().view().foregroundColor())

    @pyqtSlot()
    def slot_update_ambient_color(self):
        if self.docker.canvas() is not None:
            self.ambient_color.set_color(self.docker.canvas().view().foregroundColor())

    @pyqtSlot()
    def slot_add_new_color_btn(self):
        if self.mode == modes["add"] and self.docker.canvas() is not None:
            managed_color = self.docker.canvas().view().foregroundColor()
            q_color = self.docker.managedcolor_to_qcolor(managed_color)
            self.saved_colors.append(q_color)

            color, light_color, shadow_color = self.get_mixed_colors(q_color)


            local_color_row = QHBoxLayout()
            color_row = QHBoxLayout()
            light_row = QHBoxLayout()

            del_row_btn = ColorBtn(self.docker, q_color, self)
            new_color_btn = ColorBtn(self.docker, q_color, self)
            new_mixed_color_btn = ColorBtn(self.docker, color, self)
            light_color_btn = ColorBtn(self.docker, light_color, self)
            shadow_color_btn = ColorBtn(self.docker, shadow_color, self)

            def handle_del_row():
                del_row_btn.deleteLater()
                new_color_btn.deleteLater()
                new_mixed_color_btn.deleteLater()
                local_color_row.deleteLater()
                color_row.deleteLater()
                light_color_btn.deleteLater()
                shadow_color_btn.deleteLater()


            def set_foreground(managed_color):
                if self.docker.canvas().view() is not None:
                    self.docker.canvas().view().setForeGroundColor(managed_color)


            def handle_new_color_click():
                managed_color = self.docker.qcolor_to_managedcolor(q_color)
                set_foreground(managed_color)

            def handle_light_color_click():
                managed_color = self.docker.qcolor_to_managedcolor(light_color)
                set_foreground(managed_color)

            def handle_new_mixed_color_click():
                managed_color = self.docker.qcolor_to_managedcolor(color)
                set_foreground(managed_color)

            def handle_shadow_color_click():
                managed_color = self.docker.qcolor_to_managedcolor(shadow_color)
                set_foreground(managed_color)


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
            light_row.addWidget(new_mixed_color_btn)
            color_row.addLayout(light_row)

            color_row.addWidget(shadow_color_btn)

            ## add new colors mixed with main and ambient color based on light
            #intensity

    # color: QColor because color conversion between QColor and ManagedColor
    # shifts color drastically
    def get_mixed_colors(self, color):
        r, g, b, a = color.getRgbF()
        l_r, l_g, l_b, l_a = self.light_color.getRgbF()
        a_r, a_g, a_b, a_a = self.ambient_color.getRgbF()

        light_intensity = 0.25
        ambient_intensity = 0.1

        #TODO: could assume new_color already influenced by ambient color?

        r, g, b = mix((r, g, b),(a_r, a_g, a_b), ambient_intensity)
        l_r, l_g, l_b = mix((r, g, b),(l_r, l_g, l_b), light_intensity)
        s_r, s_g, s_b = relative_color_shift((r, g, b), 0.0, 0.5)

        color = QColor.fromRgbF(r, g, b, a)
        light_color = QColor.fromRgbF(l_r, l_g, l_b)
        shadow_color = QColor.fromRgbF(s_r, s_g, s_b) 

        return (color, light_color, shadow_color)
