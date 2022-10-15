# Qt imports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QSizePolicy

# UI import
from markwindow import Ui_MarkWindow

# other
from new_utils import getPixmap
import cv2
import numpy as np

# image viewer window
class markWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None, display_image=[]):
        super(markWindow, self).__init__(parent)
        self.ui = Ui_MarkWindow()
        self.ui.setupUi(self)

        # connect buttons (click trigger action)
        self.ui.loadImage.clicked.connect(self.loadImage)
        self.ui.SetMark.clicked.connect(self.setMark)
        self.ui.cancelMark.clicked.connect(self.cancel)

        # to make images resize dynamically when we resize the window
        # it has nothing to do with the algorithm it's just to display images in the UI
        self.ui.oMark.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.bMark.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # this will hold loaded watermark
        self.original_image = []
        # this will hold the converted watermark (to binary)
        self.binary_image = []

        # pixmaps to display images in the UI
        self.original_image_pixmap = None
        self.binary_image_pixmap = None

        # state to detect if user has confirmed the set of the watermark
        self.set_mark = False

        # display window
        self.show()

        # display current watermark
        pixmap = getPixmap(display_image)
        self.ui.oMark.setPixmap(pixmap.scaled(self.ui.oMark.size()))
        self.ui.bMark.setPixmap(pixmap.scaled(self.ui.bMark.size()))


    
    # function that will load an image when the load button gets clicked
    def loadImage(self):
        # open file dialog
        image_path = QFileDialog.getOpenFileName(self, 'Open file','.', "Image files (*.jpg *.png)")[0]
        
        # if we get a valid path
        if image_path:
            # clear UI previous displayed images
            self.ui.oMark.clear()
            self.ui.bMark.clear()

            # read image
            self.original_image = cv2.imread(image_path, 0)

            # display image
            self.original_image_pixmap = getPixmap(self.original_image)
            self.ui.oMark.setPixmap(self.original_image_pixmap.scaled(self.ui.oMark.size()))

            # convert watermark to binary
            _, self.binary_image = cv2.threshold(self.original_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # display converted watermark
            self.binary_image_pixmap = getPixmap(self.binary_image)
            self.ui.bMark.setPixmap(self.binary_image_pixmap.scaled(self.ui.bMark.size()))


    # if user confirmed that this watermark will be set then change the state
    # and close the window
    def setMark(self):
        if len(self.binary_image) != 0:
            self.set_mark = True
        self.close()
    

    # cancel (close window)
    def cancel(self):
        self.close()

    
    # close event
    # a function called automatically when window is closed
    def closeEvent(self, event):
        # if user has confirmed that this watermark will be set then
        if self.set_mark:
            # try to update the main window
            # give the infomation if this new watermark is not the same as the previous one
            self.parent().is_watermark_changed = False
            # if this watermark is not similar to the previous one then give signal to main window
            # to enable update button
            if not np.array_equal(self.parent().current_watermark, self.binary_image):
                self.parent().is_watermark_changed = True
            
            # update mainwindow fui
            self.parent().update_gui()
            # set watermark to this new watermark
            self.parent().watermark = self.binary_image
            
        
        # reset variables
        self.binary_image = []
        self.original_image = []
        self.set_mark = False

        return super().closeEvent(event)
