# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/extractwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExtractWindow(object):
    def setupUi(self, ExtractWindow):
        ExtractWindow.setObjectName("ExtractWindow")
        ExtractWindow.resize(756, 475)
        self.centralwidget = QtWidgets.QWidget(ExtractWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.recovered_image = clickable_qlable(self.centralwidget)
        self.recovered_image.setText("")
        self.recovered_image.setObjectName("recovered_image")
        self.verticalLayout.addWidget(self.recovered_image)
        self.psnr_recovered = QtWidgets.QLCDNumber(self.centralwidget)
        self.psnr_recovered.setObjectName("psnr_recovered")
        self.verticalLayout.addWidget(self.psnr_recovered)
        self.verticalLayout.setStretch(1, 5)
        self.verticalLayout.setStretch(2, 1)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.extracted_watermark = clickable_qlable(self.centralwidget)
        self.extracted_watermark.setText("")
        self.extracted_watermark.setObjectName("extracted_watermark")
        self.verticalLayout_2.addWidget(self.extracted_watermark)
        self.psnr_watermark = QtWidgets.QLCDNumber(self.centralwidget)
        self.psnr_watermark.setObjectName("psnr_watermark")
        self.verticalLayout_2.addWidget(self.psnr_watermark)
        self.verticalLayout_2.setStretch(1, 5)
        self.verticalLayout_2.setStretch(2, 1)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        ExtractWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ExtractWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 756, 21))
        self.menubar.setObjectName("menubar")
        ExtractWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ExtractWindow)
        self.statusbar.setObjectName("statusbar")
        ExtractWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ExtractWindow)
        QtCore.QMetaObject.connectSlotsByName(ExtractWindow)

    def retranslateUi(self, ExtractWindow):
        _translate = QtCore.QCoreApplication.translate
        ExtractWindow.setWindowTitle(_translate("ExtractWindow", "Extracting Visualizer"))
        self.label.setText(_translate("ExtractWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600;\">Recovered Image</span></p></body></html>"))
        self.label_2.setText(_translate("ExtractWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600;\">Extracted Watermark</span></p></body></html>"))
from clickable_qlable import clickable_qlable
