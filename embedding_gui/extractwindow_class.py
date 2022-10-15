# Qt imports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy

# UI import
from extractwindow import Ui_ExtractWindow

from viewer_class import viewerWindow

# other
from new_utils import getPixmap

# image viewer window
class extractWindow(QtWidgets.QMainWindow):

    def __init__(self, recovered_image, psnr_recovered, extracted_watermark, psnr_watermark):
        super(extractWindow, self).__init__()
        self.ui = Ui_ExtractWindow()
        self.ui.setupUi(self)

        # to make images resize dynamically when we resize the window
        # it has nothing to do with the algorithm it's just to display images in the UI
        self.ui.recovered_image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.extracted_watermark.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.ui.psnr_recovered.setDigitCount(6)
        self.ui.psnr_watermark.setDigitCount(6)

        # image to display and its psnr
        self.recovered_image = recovered_image
        self.psnr_recovered = psnr_recovered

        # watermark to display and its psnr
        self.extracted_watermark = extracted_watermark
        self.psnr_watermark = psnr_watermark

        # add to double click signal to displayed images
        self.ui.recovered_image.clicked.connect(self.open_recovered_image_viewer)
        self.ui.extracted_watermark.clicked.connect(self.open_extracted_watermark_viewer)

        # viewer windows
        # viewer windows are windows to display images in original size
        self.image_recovered_viewer = None
        self.extracted_watermark_viewer = None

        # display extract windows
        self.show()
        
        # update gui to display images
        self.display_images()


    
    # close event
    # a function called automatically when window is closed
    # it will make sure to close viewer windows before closing extract window
    def closeEvent(self, event):
        if self.image_recovered_viewer != None and self.image_recovered_viewer.isVisible():
            self.image_recovered_viewer.close()

        if self.extracted_watermark_viewer != None and self.extracted_watermark_viewer.isVisible():
            self.extracted_watermark_viewer.close()

        return super().closeEvent(event)


    # open recovered image viewer
    def open_recovered_image_viewer(self):
        if self.image_recovered_viewer == None or not self.image_recovered_viewer.isVisible():
            self.image_recovered_viewer = viewerWindow(window_name='Image Viewer - Recovered Image', oimage=self.recovered_image, p=self.psnr_recovered)

    
    # open recovered image viewer
    def open_extracted_watermark_viewer(self):
        if self.extracted_watermark_viewer == None or not self.extracted_watermark_viewer.isVisible():
            self.extracted_watermark_viewer = viewerWindow(window_name='Image Viewer - Extracted Watermark', oimage=self.extracted_watermark, p=self.psnr_watermark)


    # resize event
    # a function called automatically when the window get resized
    def resizeEvent(self, event):
        # redisplay images
        # will give dynamic size
        self.display_images()
        return super(extractWindow, self).resizeEvent(event)


    # function that displays informations images and psnrs
    def display_images(self):
        # display recovered image
        pixmap = getPixmap(self.recovered_image)
        self.ui.recovered_image.setPixmap(pixmap.scaled(self.ui.recovered_image.size()))

        # display extracted watermark
        pixmap = getPixmap(self.extracted_watermark)
        self.ui.extracted_watermark.setPixmap(pixmap.scaled(self.ui.extracted_watermark.size()))

        n_display1 = self.psnr_recovered
        n_display2 = self.psnr_watermark

        if n_display1 > 1038.0:
            n_display1 = 999999
        
        if n_display2 > 1038.0:
            n_display2 = 999999

        # display watermarks
        self.ui.psnr_recovered.display(n_display1)
        self.ui.psnr_watermark.display(n_display2)