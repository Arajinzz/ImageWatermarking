# qt libraries
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QSizePolicy

# import ui of windows
from mainwindow import Ui_MainWindow
from viewer_class import viewerWindow

import cv2
import numpy as np
from new_utils import getPixmap, forwardProcess, image_scramble
from new_algorithms import extract
import os
import shutil

class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # init gui
        self.ui.extract_btn.setEnabled(False)
        self.ui.save_btn.setEnabled(False)

        # dynamic resize
        self.ui.extracted_watermark.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.image_toreverse.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # button events
        self.ui.load_btn.clicked.connect(self.load_image)
        self.ui.save_btn.clicked.connect(self.save_image)
        self.ui.extract_btn.clicked.connect(self.extract)

        # checkbox event
        self.ui.resized_checkbox.clicked.connect(self.something_changed)
        self.ui.force_checkbox.clicked.connect(self.something_changed)
        self.ui.resized_checkbox.clicked.connect(self.something_changed)
        self.ui.inputkey_field.textChanged.connect(self.something_changed)

        # images event
        self.ui.extracted_watermark.clicked.connect(self.open_extracted_watermark_viewer)
        self.ui.image_toreverse.clicked.connect(self.open_image_toreverse_viewer)

        # action events
        self.ui.actionClose.triggered.connect(self.close)

        # image loaded state
        self.image_loaded = False
        self.is_image_reversed = False
        self.auto_update_state = False

        self.key = 7777
        self.real_height, self.real_width = 0, 0

        self.last_path = '.'

        # images
        self.image_toreverse     = []
        self.extracted_watermark = []
        self.recovered_image     = []
        self.extracted_watermark_backup = []

        # viewer window
        self.image_toreverse_viewer = None
        self.extracted_watermark_viewer = None

        self.masks = {}
        self.error_dialog = QtWidgets.QErrorMessage()
        self.error_dialog.setWindowTitle('ERROR')

        self.previous_code = ''



    def something_changed(self):
        if self.auto_update_state:
            self.extract()
        self.update_gui()


    def open_image_toreverse_viewer(self):
        if self.image_toreverse_viewer == None or not self.image_toreverse_viewer.isVisible():
            if self.image_loaded:
                self.image_toreverse_viewer = viewerWindow(window_name='Image Viewer - Original Image', oimage=self.image_recovered)


    def open_extracted_watermark_viewer(self):
        if self.extracted_watermark_viewer == None or not self.extracted_watermark_viewer.isVisible():
            if self.image_loaded and self.is_image_reversed:
                self.extracted_watermark_viewer = viewerWindow(window_name='Image Viewer - Watermarked Image', oimage=self.extracted_watermark)


    # resize event
    def resizeEvent(self, event):
        self.display_images()
        return super(ApplicationWindow, self).resizeEvent(event)


    # close which will close everything
    def closeEvent(self, event):
        import sys
        sys.exit(1)
        return super().closeEvent(event)
                

    # handles image loading
    def load_image(self):
        # open file browser
        image_path = QFileDialog.getOpenFileName(self, 'Open file', self.last_path, "Image files (*.jpg *.png)")[0]
        
        # if image path is valid
        if image_path:
            self.image_name = ((image_path.split('/'))[-1]).split('.')[0]
            self.last_path = (image_path.split('/'))[:-1]
            self.last_path = '/'.join(self.last_path)

            if self.image_toreverse_viewer != None and self.image_toreverse_viewer.isVisible():
                self.image_toreverse_viewer.close()

            if self.extracted_watermark_viewer != None and self.extracted_watermark_viewer.isVisible():
                self.extracted_watermark_viewer.close()

            # reset all variables
            self.reset_all_variables()
            self.ui.inputkey_field.setText('')

            # read the image
            self.image_toreverse = cv2.imread(image_path)
            self.image_recovered = self.image_toreverse.copy()
            
            
            # set image loaded state to true
            self.image_loaded = True

            self.previous_code = ''

            # update gui
            self.update_gui()


    # handles image saving
    def save_image(self):
        image_path = QFileDialog.getSaveFileName(self, 'Save file', self.last_path, "")[0]
        
        if image_path and len(self.recovered_image) != 0:
            # if name is same we want to replace 
            # i think this don't work for now
            if os.path.exists(image_path):
                shutil.rmtree(image_path)

            # make folder
            os.mkdir(image_path)

            # save watermarked image
            cv2.imwrite(image_path+'/image.png', self.recovered_image)
            cv2.imwrite(image_path+'/watermark.png', self.extracted_watermark)


    
    def define_masks(self, h, w):
        if self.image_loaded:
            self.masks = { 
                            'mask0'  : np.ones((h, w), dtype=np.uint8) * 0,
                            'mask15' : np.ones((h, w), dtype=np.uint8) * 15,
                            'mask16' : np.ones((h, w), dtype=np.uint8) * 16,
                            'mask31' : np.ones((h, w), dtype=np.uint8) * 31,
                         }




    # handles watermarking
    def extract(self):
        if self.image_loaded:

            # extracting process start here
            channel_code = {0:'r', 1:'g', 2:'b'}
            mask_code = {0:'mask0', 1:'mask15', 2:'mask16', 3:'mask31'}
            
            #error_dialog.showMessage('Oh no!')
            code = self.ui.inputkey_field.text()
            code = code.replace(' ', '')

            if not code.isdigit():
                self.error_dialog.showMessage("CODE ERROR !!!")
                self.ui.inputkey_field.setText(self.previous_code)
                return

            off1 = code[0:1]

            if off1 == '':
                self.error_dialog.showMessage("CODE ERROR !!!")
                self.ui.inputkey_field.setText(self.previous_code)
                return

            off1 = int(off1)
            off2 = code[off1+1:off1+2]

            if off2 == '':
                self.error_dialog.showMessage("CODE ERROR !!!")
                self.ui.inputkey_field.setText(self.previous_code)
                return

            off2 = int(off2)

            height = code[1:1+off1]
            width = code[2+off1:2+off1+off2]
            channel = code[2+off1+off2:3+off1+off2]
            mask = code[3+off1+off2:4+off1+off2]
            embed_block = code[4+off1+off2 :7+off1+off2]
            t = code[7+off1+off2 : 12+off1+off2]

            if height == '' or width == '' or channel == '' or mask == '' or embed_block == '' or t == '':
                self.error_dialog.showMessage("CODE ERROR !!!")
                self.ui.inputkey_field.setText(self.previous_code)
                return

            height, width = int(height), int(width)
            channel, mask = int(channel), int(mask)
            embed_block = int(embed_block)
            t = float(t)

            if channel < 0 or channel > 2 or mask < 0 or mask > 3 or embed_block < 0 or embed_block > 63:
                self.error_dialog.showMessage("CODE ERROR !!!")
                self.ui.inputkey_field.setText(self.previous_code)
                return

            channel = channel_code[channel]
            mask = mask_code[mask]

            off3 = code[12+off1+off2 : 16+off1+off2]

            if off3 == '':
                self.error_dialog.showMessage("CODE ERROR !!!")
                self.ui.inputkey_field.setText(self.previous_code)
                return

            off3 = int(off3)

            crypted_key = code[16+off1+off2 : 16+off1+off2+off3]
            another_key = code[16+off1+off2+off3 : ]

            if crypted_key == '' or another_key == '':
                self.error_dialog.showMessage("CODE ERROR !!!")
                self.ui.inputkey_field.setText(self.previous_code)
                return

            crypted_key = int(code[16+off1+off2 : 16+off1+off2+off3])
            another_key = int(code[16+off1+off2+off3 : ])

            if self.image_toreverse_viewer != None and self.image_toreverse_viewer.isVisible():
                self.image_toreverse_viewer.close()

            if self.extracted_watermark_viewer != None and self.extracted_watermark_viewer.isVisible():
                self.extracted_watermark_viewer.close()

            self.ui.loadingBar.setValue(20)
            
            image_to_extract_from = self.image_toreverse.copy()
            if self.ui.resized_checkbox.isChecked():
                image_to_extract_from = cv2.resize(image_to_extract_from, (width, height), cv2.INTER_CUBIC)

            
            h, w = image_to_extract_from.shape[:2]

            self.define_masks(h, w)

            decipher_key_from_image = image_to_extract_from.copy() % 2
            decipher_key_from_image = decipher_key_from_image * cv2.flip(decipher_key_from_image, 1)
            decipher_key_from_image = decipher_key_from_image.sum()
            
            if not self.ui.force_checkbox.isChecked():
                another_key = decipher_key_from_image
            
            self.key = crypted_key ^ another_key

            self.setEnabled(False)

            r, g, b = cv2.split(image_to_extract_from)
            channels = {'r':r, 'g':g, 'b':b}
            extracting_channel = channels[channel]
            extracting_channel = extracting_channel.reshape(1, h, w)

            self.ui.loadingBar.setValue(40)

            recovered_channel, ex_mark = extract(embedded_img=extracting_channel, img_psize=8, t=t, b=embed_block, key=self.key, mode='extracting_mode')

            self.ui.loadingBar.setValue(60)

            channels[channel] = recovered_channel.reshape(h, w)
            ex_mark = ex_mark.reshape(ex_mark.shape[1], ex_mark.shape[2])
            recovered_image = cv2.merge((channels['r'], channels['g'], channels['b'])) ^ cv2.merge((self.masks[mask], self.masks[mask], self.masks[mask]))

            self.extracted_watermark = ex_mark.copy()
            self.extracted_watermark_backup = ex_mark.copy()
            self.recovered_image = recovered_image.copy()

            self.real_height, self.real_width = height, width

            self.ui.loadingBar.setValue(100)

            # clear image ui
            self.ui.image_toreverse.clear()
            self.previous_code = code

            # reset some states
            self.is_image_reversed = True
            self.auto_update_state = True
        

        self.setEnabled(True)
        self.update_gui()
    


    # handles gui updates
    def update_gui(self):
        self.ui.extract_btn.setEnabled(self.image_loaded)
        self.ui.save_btn.setEnabled(self.is_image_reversed)
        self.ui.resized_checkbox.setEnabled(self.ui.force_checkbox.isChecked())
        self.ui.resized_checkbox.setChecked(self.ui.resized_checkbox.isChecked() and self.ui.force_checkbox.isChecked())


        self.ui.extract_btn.setText('Extract')
        self.ui.extract_btn.setEnabled(True)
        self.ui.label.setText('<html><head/><body><p align="center"><span style=" font-size:11pt; font-weight:600;">WATERMARKED</span></p></body></html>')

        if self.is_image_reversed:
            self.ui.label.setText('<html><head/><body><p align="center"><span style=" font-size:11pt; font-weight:600;">RECOVERED</span></p></body></html>')
            self.ui.extract_btn.setText('AUTO UPDATE MODE')
            self.ui.extract_btn.setEnabled(False)
            

        self.setWindowTitle('Extracting Program')


        self.display_images()


    def display_images(self):
        if self.image_loaded:
            pixmap = getPixmap(self.image_recovered)
            self.ui.image_toreverse.setPixmap(pixmap.scaled(self.ui.image_toreverse.size()))

        if self.is_image_reversed:
            pixmap = getPixmap(self.extracted_watermark)
            self.ui.extracted_watermark.setPixmap(pixmap.scaled(self.ui.extracted_watermark.size()))
    

    
    ###################################################################
    def reset_all_variables(self):
        self.setWindowTitle('Extracting Program')
        self.is_image_reversed = False
        self.image_loaded = False
        self.auto_update_state = False
        self.image_toreverse = []
        self.recovered_image = []
        self.extracted_watermark = []
        self.ui.image_toreverse.clear()
        self.ui.extracted_watermark.clear()
        self.ui.loadingBar.setValue(0)
        