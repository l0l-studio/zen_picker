try:
    from PyQt6.QtWidgets import QDialog
except:
    from PyQt5.QtWidgets import QDialog

from .app import App

class Dialog(QDialog):
    def __init__(self, app: App, ui, parent=None):
        super(Dialog, self).__init__(parent)

        self.app = app
        self.__ui = ui

    def accept(self):
        self.__ui.accept()
        super(Dialog, self).accept()

    def closeEvent(self, event):
        event.accept()
