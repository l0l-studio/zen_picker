try:
    from PyQt6.QtWidgets import QDialog
except:
    from PyQt5.QtWidgets import QDialog


class SettingsDialog(QDialog):
    def __init__(self, color_manager, parent=None):
        super(SettingsDialog, self).__init__(parent)


        #TODO: render settings
        # https://invent.kde.org/graphics/krita/-/blob/master/plugins/python/mixer_slider_docker/ui_mixer_slider_docker.py
        self.color_manager = color_manager

    def accept(self):
        self.color_manager.docker.settings_changed()

        super(SettingsDialog, self).accept()

    def closeEvent(self, event):
        event.accept()
