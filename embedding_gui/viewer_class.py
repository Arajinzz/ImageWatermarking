# Qt imports
from PyQt5 import QtWidgets

# UI import
from viewerwindow import Ui_ViewerWindow

# other
from new_utils import getPixmap, psnr


# image viewer window
class viewerWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None, window_name='Image Viewer', oimage=[], wimage=[], p=-1):
        super(viewerWindow, self).__init__()
        self.ui = Ui_ViewerWindow()
        self.ui.setupUi(self)

        # set window name title
        self.setWindowTitle(window_name)

        # set parent window
        self.parent = parent

        # psnr variable
        self.psnr = 0

        # if no watermarked image is passed then hide psnr field
        if len(wimage) == 0:
            self.ui.psnr.hide()
        else:
            # else calculate psnr
            self.psnr = psnr(oimage, wimage)

        # if watermarked image is passed then display psnr field
        if p > 0:
            self.ui.psnr.show()
            self.psnr = p

        # images
        self.oimage = oimage
        self.wimage = wimage
        
        # image to display
        self.image = []
        self.image_pixmap = None

        # set image to display
        if len(oimage) != 0:
            self.image = oimage.copy()

        if len(wimage) != 0:
            self.image = wimage.copy()
        

        # zoom multipliers
        self.initial_zoom = 3
        self.zoom_sizes = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75]

        # actions clicked
        self.ui.actionZoom_In_25.triggered.connect(self.zoomin25)
        self.ui.actionZoom_out_25.triggered.connect(self.zoomout25)
        self.ui.actionResetZoom.triggered.connect(self.reset_original_size)
        self.ui.actionClose.triggered.connect(self.close)

        # show window
        self.show()

        # display image and psnr
        self.display(self.image, self.psnr)

    
    # zoom in function
    def zoomin25(self):
        if len(self.image) != 0:
            if self.initial_zoom + 1 < len(self.zoom_sizes):
                self.initial_zoom += 1
            self.ui.displayimage.setPixmap(self.image_pixmap.scaled(self.image_pixmap.size() * self.zoom_sizes[self.initial_zoom]))
    

    # zoom out function
    def zoomout25(self):
        if len(self.image) != 0:
            if self.initial_zoom - 1 > 0:
                self.initial_zoom -= 1
            self.ui.displayimage.setPixmap(self.image_pixmap.scaled(self.image_pixmap.size() * self.zoom_sizes[self.initial_zoom]))

    
    # reset to original (unzoom)
    def reset_original_size(self):
        self.initial_zoom = 3
        self.ui.displayimage.setPixmap(self.image_pixmap.scaled(self.image_pixmap.size() * self.zoom_sizes[self.initial_zoom]))


    # close event
    def closeEvent(self, event):
        # reset zoom
        self.initial_zoom = 3
        return super().closeEvent(event)


    # display information in the UI
    def display(self, img, psnr=None):
        if psnr != None:
            if psnr > 1038.0:
                psnr = 999999
            self.ui.psnr.setText('<b><p style="font-size:12px" style="color:red">'+'PSNR : ' + str(psnr) + '</p></b>')

        if len(img) != 0:
            h, w = img.shape[:2]
            self.resize(w+75, h+75)
            self.image_pixmap = getPixmap(img)
            self.ui.displayimage.setPixmap(self.image_pixmap)

