# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'docker.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(661, 541)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_2.setMaximumSize(QtCore.QSize(25, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.red_slider = QtWidgets.QSlider(self.dockWidgetContents)
        self.red_slider.setMaximum(255)
        self.red_slider.setOrientation(QtCore.Qt.Horizontal)
        self.red_slider.setObjectName("red_slider")
        self.horizontalLayout.addWidget(self.red_slider)
        self.red_label = QtWidgets.QLabel(self.dockWidgetContents)
        self.red_label.setMinimumSize(QtCore.QSize(100, 0))
        self.red_label.setMaximumSize(QtCore.QSize(100, 16777215))
        self.red_label.setAlignment(QtCore.Qt.AlignCenter)
        self.red_label.setObjectName("red_label")
        self.horizontalLayout.addWidget(self.red_label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.green_slider = QtWidgets.QSlider(self.dockWidgetContents)
        self.green_slider.setMaximum(255)
        self.green_slider.setOrientation(QtCore.Qt.Horizontal)
        self.green_slider.setObjectName("green_slider")
        self.horizontalLayout_3.addWidget(self.green_slider)
        self.green_label = QtWidgets.QLabel(self.dockWidgetContents)
        self.green_label.setMinimumSize(QtCore.QSize(25, 0))
        self.green_label.setAlignment(QtCore.Qt.AlignCenter)
        self.green_label.setObjectName("green_label")
        self.horizontalLayout_3.addWidget(self.green_label)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_10 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_4.addWidget(self.label_10)
        self.blue_slider = QtWidgets.QSlider(self.dockWidgetContents)
        self.blue_slider.setMaximum(255)
        self.blue_slider.setOrientation(QtCore.Qt.Horizontal)
        self.blue_slider.setObjectName("blue_slider")
        self.horizontalLayout_4.addWidget(self.blue_slider)
        self.blue_label = QtWidgets.QLabel(self.dockWidgetContents)
        self.blue_label.setMinimumSize(QtCore.QSize(25, 0))
        self.blue_label.setMaximumSize(QtCore.QSize(25, 16777215))
        self.blue_label.setAlignment(QtCore.Qt.AlignCenter)
        self.blue_label.setObjectName("blue_label")
        self.horizontalLayout_4.addWidget(self.blue_label)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_8 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_5.addWidget(self.label_8)
        self.saturation_slider = QtWidgets.QSlider(self.dockWidgetContents)
        self.saturation_slider.setMaximum(255)
        self.saturation_slider.setOrientation(QtCore.Qt.Horizontal)
        self.saturation_slider.setObjectName("saturation_slider")
        self.horizontalLayout_5.addWidget(self.saturation_slider)
        self.saturation_label = QtWidgets.QLabel(self.dockWidgetContents)
        self.saturation_label.setMinimumSize(QtCore.QSize(25, 0))
        self.saturation_label.setMaximumSize(QtCore.QSize(25, 16777215))
        self.saturation_label.setAlignment(QtCore.Qt.AlignCenter)
        self.saturation_label.setObjectName("saturation_label")
        self.horizontalLayout_5.addWidget(self.saturation_label)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_6 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_2.addWidget(self.label_6)
        self.value_slider = QtWidgets.QSlider(self.dockWidgetContents)
        self.value_slider.setMaximum(255)
        self.value_slider.setOrientation(QtCore.Qt.Horizontal)
        self.value_slider.setObjectName("value_slider")
        self.horizontalLayout_2.addWidget(self.value_slider)
        self.value_label = QtWidgets.QLabel(self.dockWidgetContents)
        self.value_label.setMinimumSize(QtCore.QSize(25, 0))
        self.value_label.setMaximumSize(QtCore.QSize(25, 16777215))
        self.value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.value_label.setObjectName("value_label")
        self.horizontalLayout_2.addWidget(self.value_label)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "DockWidget"))
        self.label_2.setText(_translate("DockWidget", "R"))
        self.red_label.setText(_translate("DockWidget", "0"))
        self.label_4.setText(_translate("DockWidget", "G"))
        self.green_label.setText(_translate("DockWidget", "0"))
        self.label_10.setText(_translate("DockWidget", "B"))
        self.blue_label.setText(_translate("DockWidget", "0"))
        self.label_8.setText(_translate("DockWidget", "S"))
        self.saturation_label.setText(_translate("DockWidget", "0"))
        self.label_6.setText(_translate("DockWidget", "V"))
        self.value_label.setText(_translate("DockWidget", "0"))
