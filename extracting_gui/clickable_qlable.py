from PyQt5 import QtCore, QtGui, QtWidgets

# a code to give displayed image the ability to be double clicked

class clickable_qlable(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)


    def mouseDoubleClickEvent(self, event):
        self.clicked.emit()

