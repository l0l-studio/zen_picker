try:
    from PyQt6.QtWidgets import QDialogButtonBox, QLabel, QVBoxLayout, QHBoxLayout, QSpinBox
    from PyQt6.QtGui import QIntValidator
    from PyQt6.QtCore import Qt
except:
    from PyQt5.QtWidgets import QDialogButtonBox, QLabel, QVBoxLayout, QHBoxLayout, QSpinBox
    from PyQt5.QtGui import QIntValidator
    from PyQt5.QtCore import Qt
import krita

from .app import App
from .dialog import Dialog
from .range_slider import RangeSlider
from .lib_zen import saturation_shift
from .utils import copy_managed_color

class AppSettingsUI(object):
    def __init__(self, app: App):
        self.app = app
        self.main_dialog = Dialog(app, self, app.krita_instance.activeWindow().qwindow())

        self.button_box = QDialogButtonBox(self.main_dialog)
        self.vbox = QVBoxLayout(self.main_dialog)
        self.hbox = QHBoxLayout(self.main_dialog)
        self.line_edit = None

        self.button_box.accepted.connect(self.main_dialog.accept)
        self.button_box.rejected.connect(self.main_dialog.reject)

        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

    def accept(_):
        pass

    def initialize(self):
        self.vbox.addLayout(self.hbox)
        self.hbox.addWidget(QLabel(i18n('image value range:')))
        self.line_edit = QSpinBox()

        left = copy_managed_color(self.app.current_color())
        left.setComponents([0.0, 0.0, 0.0, 1.0])

        right = copy_managed_color(self.app.current_color())
        right.setComponents([1.0, 1.0, 1.0, 1.0])

        (lower, upper) = self.app.value_range

        value_slider = RangeSlider(
            self.app, 
            "value_slider",
            left,
            right, 
            lower,
            upper
        )
        # upper_slider = RangeSlider(
        #     self.app, 
        #     "upper_value_limit", 
        #     left,
        #     right, 
        #     lower,
        #     upper
        # )

        self.vbox.addWidget(value_slider)
        value_slider.show()

        self.vbox.addWidget(self.button_box)

        self.main_dialog.show()
        self.main_dialog.activateWindow()
        self.main_dialog.exec()
