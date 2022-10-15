# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/markwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MarkWindow(object):
    def setupUi(self, MarkWindow):
        MarkWindow.setObjectName("MarkWindow")
        MarkWindow.resize(700, 400)
        MarkWindow.setMinimumSize(QtCore.QSize(700, 400))
        MarkWindow.setMaximumSize(QtCore.QSize(700, 400))
        self.centralwidget = QtWidgets.QWidget(MarkWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.mainLayout.addLayout(self.horizontalLayout)
        self.imageLayout = QtWidgets.QHBoxLayout()
        self.imageLayout.setObjectName("imageLayout")
        self.oMark = clickable_qlable(self.centralwidget)
        self.oMark.setText("")
        self.oMark.setObjectName("oMark")
        self.imageLayout.addWidget(self.oMark)
        self.bMark = clickable_qlable(self.centralwidget)
        self.bMark.setText("")
        self.bMark.setObjectName("bMark")
        self.imageLayout.addWidget(self.bMark)
        self.mainLayout.addLayout(self.imageLayout)
        self.buttonMainLayout = QtWidgets.QVBoxLayout()
        self.buttonMainLayout.setObjectName("buttonMainLayout")
        self.buttonSubLayout1 = QtWidgets.QHBoxLayout()
        self.buttonSubLayout1.setObjectName("buttonSubLayout1")
        self.loadImage = QtWidgets.QPushButton(self.centralwidget)
        self.loadImage.setObjectName("loadImage")
        self.buttonSubLayout1.addWidget(self.loadImage)
        self.buttonMainLayout.addLayout(self.buttonSubLayout1)
        self.buttonSubLayout2 = QtWidgets.QHBoxLayout()
        self.buttonSubLayout2.setObjectName("buttonSubLayout2")
        self.SetMark = QtWidgets.QPushButton(self.centralwidget)
        self.SetMark.setObjectName("SetMark")
        self.buttonSubLayout2.addWidget(self.SetMark)
        self.cancelMark = QtWidgets.QPushButton(self.centralwidget)
        self.cancelMark.setObjectName("cancelMark")
        self.buttonSubLayout2.addWidget(self.cancelMark)
        self.buttonMainLayout.addLayout(self.buttonSubLayout2)
        self.mainLayout.addLayout(self.buttonMainLayout)
        self.mainLayout.setStretch(1, 2)
        self.verticalLayout_4.addLayout(self.mainLayout)
        MarkWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MarkWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 700, 21))
        self.menubar.setObjectName("menubar")
        MarkWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MarkWindow)
        self.statusbar.setObjectName("statusbar")
        MarkWindow.setStatusBar(self.statusbar)
        self.actionSet_Watermark = QtWidgets.QAction(MarkWindow)
        self.actionSet_Watermark.setObjectName("actionSet_Watermark")
        self.actionClose = QtWidgets.QAction(MarkWindow)
        self.actionClose.setObjectName("actionClose")

        self.retranslateUi(MarkWindow)
        QtCore.QMetaObject.connectSlotsByName(MarkWindow)

    def retranslateUi(self, MarkWindow):
        _translate = QtCore.QCoreApplication.translate
        MarkWindow.setWindowTitle(_translate("MarkWindow", "Set Watermark"))
        self.label.setText(_translate("MarkWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600;\">Original</span></p></body></html>"))
        self.label_2.setText(_translate("MarkWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600;\">Binary</span></p></body></html>"))
        self.loadImage.setText(_translate("MarkWindow", "Load Image"))
        self.SetMark.setText(_translate("MarkWindow", "Set Watermark"))
        self.cancelMark.setText(_translate("MarkWindow", "Cancel"))
        self.actionSet_Watermark.setText(_translate("MarkWindow", "Set Watermark"))
        self.actionClose.setText(_translate("MarkWindow", "Close"))
from clickable_qlable import clickable_qlable
