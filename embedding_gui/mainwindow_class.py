# qt libraries
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QSizePolicy

# import ui of windows
from mainwindow import Ui_MainWindow
from markwindow_class import markWindow
from extractwindow_class import extractWindow
from viewer_class import viewerWindow

# other imports
import cv2
import numpy as np
from new_utils import psnr, getPixmap, find_value_t, forwardProcess, image_scramble
from new_utils import evaluate_mask, evaluate_psnr_mark, evaluate_psnr
from new_algorithms import embed, extract
import os
import shutil

class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # init gui
        self.ui.update_btn.setText('Watermark')
        self.ui.update_btn.setEnabled(False)
        self.ui.actionExtract_Visualizer.setEnabled(False)
        self.ui.save_btn.setEnabled(False)
        self.ui.key_box.setValue(7777)
        self.ui.search_box.setMaximum(64)
        self.ui.search_box.setMinimum(2)
        self.ui.search_box.setValue(64)
        #self.ui.label_2.hide()
        #self.ui.label_3.hide()

        # dynamic resize
        self.ui.original_image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.ui.watermarked_image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # button events
        self.ui.load_btn.clicked.connect(self.load_image)
        self.ui.save_btn.clicked.connect(self.save_image)
        self.ui.update_btn.clicked.connect(self.update)

        # images event
        self.ui.original_image.clicked.connect(self.open_original_image_viewer)
        self.ui.watermarked_image.clicked.connect(self.open_watermarked_image_viewer)

        # action events
        self.ui.actionSet_Watermark.triggered.connect(self.open_mark_window)
        self.ui.actionExtract_Visualizer.triggered.connect(self.open_extract_window)
        self.ui.actionClose.triggered.connect(self.close)

        # listen if values changed
        self.ui.search_box.valueChanged.connect(self.something_changed)
        self.ui.key_box.valueChanged.connect(self.something_changed)

        # image loaded state
        self.image_loaded = False
        # is image watermarked state
        self.is_image_watermarked = False
        # a state to check if we changed parametres
        self.are_parametres_changed = False
        # a state to check if watermark is changed
        self.is_watermark_changed = False
        # a state to check if masks are delared
        self.masks_defined = False
        # a state to check if DCTs are already calculated
        self.dct_calculated = False
        # state to check if embedding position is changed
        self.position_changed_state = False

        # images
        self.original_image    = []
        self.watermarked_image = []
        self.recovered_image   = []
        self.display_watermark = []

        # default watermark is a white image
        self.watermark = np.ones((512, 512), dtype=np.uint8) * 255
        # this will be used to calculate psnr between original watermark and extracted watermark
        self.compare_watermark = self.watermark.copy()
        # this will be used to check if the watermark have been changed to enable update button
        self.current_watermark = self.watermark.copy()

        # additional windows
        self.mark_window = None
        self.extract_window = None
        self.original_image_viewer = None
        self.watermarked_image_viewer = None

        # watermarking variables
        self.tvalue = 2
        self.key = self.ui.key_box.value()
        self.embedding_position = self.ui.search_box.value() - 1
        self.masks = None
        self.r_t, self.g_t, self.b_t = {}, {}, {}
        self.r_dcts, self.g_dcts, self.b_dcts = {}, {}, {}
        self.red_channel, self.green_channel, self.blue_channel = None, None, None
        self.code = ''
        self.image_name = ''

        self.last_path = '.'

        # multipliers to evaluate our PSNR
        # used to give a sense of importance
        # for example extracted image psnr is more important than imperciptibility
        self.recovered_multiplier = 5
        self.mark_multiplier = 3
        self.imper_multiplier = 1
        self.mask_multiplier = 1

        # holders for best extracted parametres
        self.best_channel = 'r'
        self.best_mask = 'mask0'
        self.psnr_watermarked = 0
        self.psnr_recovered = 0
        self.psnr_watermark = 0


    # function that opens original image viewer to inspect the image in its original size
    def open_original_image_viewer(self):
        if self.original_image_viewer == None or not self.original_image_viewer.isVisible():
            if self.image_loaded:
                self.original_image_viewer = viewerWindow(window_name='Image Viewer - Original Image', oimage=self.original_image)


    # function that opens watermarked image viewer to inspect the watermarked in its original size
    def open_watermarked_image_viewer(self):
        if self.watermarked_image_viewer == None or not self.watermarked_image_viewer.isVisible():
            if self.image_loaded and self.is_image_watermarked:
                self.watermarked_image_viewer = viewerWindow(window_name='Image Viewer - Watermarked Image', oimage=self.original_image, wimage=self.watermarked_image)


    # check if something is changed
    # this will update the "UPDATE" button if parametres are changed
    # like embedding position changed or watermark changed
    def something_changed(self):
        if self.ui.update_btn.text() == 'Update':
            self.are_parametres_changed = False
            self.position_changed_state = True
            
            # check if search_box value changed
            if self.ui.search_box.value() - 1 != self.embedding_position:
                self.are_parametres_changed = True
                self.position_changed_state = False

            # check if key_box value changed
            if self.ui.key_box.value() != self.key:
                self.are_parametres_changed = True

            # update UI
            self.update_gui()



    # resize event
    # will resize displayed images when we resize our window
    def resizeEvent(self, event):
        self.display_images()
        return super(ApplicationWindow, self).resizeEvent(event)


    # close which will close everything
    def closeEvent(self, event):
        import sys
        sys.exit(1)
        return super().closeEvent(event)
                
    
    # open the set watermark window
    def open_mark_window(self):
        if self.mark_window == None or not self.mark_window.isVisible(): 
            # create window instance
            self.mark_window = markWindow(self, self.watermark)


    # open extraction window
    def open_extract_window(self):
        if self.extract_window == None or not self.extract_window.isVisible(): 
            # create window instance
            self.extract_window = extractWindow(self.recovered_image, self.psnr_recovered, self.display_watermark, self.psnr_watermark)


    # handles image loading
    def load_image(self):
        # open file browser
        image_path = QFileDialog.getOpenFileName(self, 'Open file', self.last_path, "Image files (*.jpg *.png)")[0]
        
        # if image path is valid
        if image_path:
            self.image_name = ((image_path.split('/'))[-1]).split('.')[0]
            self.last_path = (image_path.split('/'))[:-1]
            self.last_path = '/'.join(self.last_path)

            # image is not used yet
            self.image_name = ((image_path.split('/'))[-1]).split('.')[0]

            # close other windows
            if self.extract_window != None and self.extract_window.isVisible():
                self.extract_window.close()
            
            if self.original_image_viewer != None and self.original_image_viewer.isVisible():
                self.original_image_viewer.close()

            if self.watermarked_image_viewer != None and self.watermarked_image_viewer.isVisible():
                self.watermarked_image_viewer.close()

            # reset all variables
            self.reset_all_variables()

            # read the image
            self.original_image = cv2.imread(image_path)
            
            # set image loaded state to true
            self.image_loaded = True

            # update gui
            self.update_gui()


    # handles image saving
    def save_image(self):
        image_path = QFileDialog.getSaveFileName(self, 'Save file', self.last_path, "")[0]
        
        # if save path is valid and image is watermarked
        if image_path and len(self.watermarked_image) != 0:
            # if name is same we want to replace 
            # i think this don't work for now
            if os.path.exists(image_path):
                shutil.rmtree(image_path)

            # make folder
            os.mkdir(image_path)

            # save watermarked image
            cv2.imwrite(image_path+'/image.png', self.watermarked_image)

            # save extracting code in a text file
            f = open(image_path+'/code.txt', 'w+')
            f.write(self.code)
            f.close()


    # function defines filters (named masks in early stage of developement)
    def define_masks(self):
        if not self.masks_defined:
            if self.image_loaded:
                temporary_h, temporary_w = self.original_image.shape[:2]
                self.masks = { 
                                'mask0'  : np.ones((temporary_h, temporary_w), dtype=np.uint8) * 0,
                                'mask15' : np.ones((temporary_h, temporary_w), dtype=np.uint8) * 15,
                                'mask16' : np.ones((temporary_h, temporary_w), dtype=np.uint8) * 16,
                                'mask31' : np.ones((temporary_h, temporary_w), dtype=np.uint8) * 31,
                             }


    # function that caculate dct and find T values
    def calculate_dcts_and_best_blocks(self):
        if not self.dct_calculated:
            self.red_channel, self.green_channel, self.blue_channel = cv2.split(self.original_image.copy())
            # calculate dct for every mask
            for _id in self.masks:
                self.r_dcts[_id] = forwardProcess(image=self.red_channel.copy()   ^ self.masks[_id], patch_size=8)
                self.g_dcts[_id] = forwardProcess(image=self.green_channel.copy() ^ self.masks[_id], patch_size=8)
                self.b_dcts[_id] = forwardProcess(image=self.blue_channel.copy()  ^ self.masks[_id], patch_size=8)

            self.dct_calculated = True
        

        if not self.position_changed_state and self.dct_calculated:
            all_max = 0
            # find T values for all images dcts calculated
            for _id in self.masks:
                self.r_t[_id] = find_value_t(self.r_dcts[_id], self.tvalue, self.embedding_position)
                self.g_t[_id] = find_value_t(self.g_dcts[_id], self.tvalue, self.embedding_position)
                self.b_t[_id] = find_value_t(self.b_dcts[_id], self.tvalue, self.embedding_position)

                all_max = max(self.r_t[_id][1], self.g_t[_id][1], self.b_t[_id][1], all_max)
            
            # this to get the right shape to make numpy operation easier
            # to avoid using loops
            self.red_channel, self.green_channel, self.blue_channel = cv2.split(self.original_image.copy())
            temporary_h, temporary_w = self.red_channel.shape
            self.red_channel   = self.red_channel.reshape(temporary_h * temporary_w)
            self.green_channel = self.green_channel.reshape(temporary_h * temporary_w)
            self.blue_channel  = self.blue_channel.reshape(temporary_h * temporary_w)

            self.red_channel   = np.repeat([self.red_channel], int(all_max / 10) , axis=0)
            self.green_channel = np.repeat([self.green_channel], int(all_max / 10) , axis=0)
            self.blue_channel  = np.repeat([self.blue_channel], int(all_max / 10) , axis=0)
    


    # extraction process to find best psnr for reversed image
    def extract_process(self, embedded_img, t, embed_position, mask, channel_name):
        lines, height, width, depth = embedded_img.shape
        embedded_img = embedded_img.reshape(lines, height*width, depth)
        red, green, blue = cv2.split(embedded_img)
        channels_dict = {'r':red, 'g':green, 'b':blue}
        
        embedded_channel = channels_dict[channel_name]
        embedded_channel = embedded_channel.reshape(lines, height, width)

        recovered_channel, extracted_watermark = extract(embedded_img=embedded_channel, img_psize=8, t=t, b=embed_position, key=self.key)
        mask = mask.reshape(mask.shape[0] * mask.shape[1])
        mask = np.repeat([mask], recovered_channel.shape[0], axis=0)

        channels_dict[channel_name] = recovered_channel ^ mask
        recovered_image = cv2.merge((channels_dict['r'], channels_dict['g'], channels_dict['b']))
        recovered_image = recovered_image.reshape(lines, height, width, depth)
        return recovered_image, extracted_watermark


    # find the best T that gives the best psnr in watermarked images 
    def best_psnr_different_t(self, images_embedded, images_recovered, marks, rs, mask):
        best_score = 0
        chosen_index = 0
        rs = np.arange(rs, 10, -10)

        for i in range(len(images_embedded)):
            psnr1 = psnr(self.original_image, images_embedded[i])
            psnr2 = psnr(self.original_image, images_recovered[i])
            psnr3 = psnr(self.compare_watermark, marks[i])
            score = evaluate_psnr(psnr1, self.imper_multiplier) + evaluate_psnr(psnr2, self.recovered_multiplier) + evaluate_mask(mask, self.mask_multiplier) + evaluate_psnr_mark(psnr3, self.mark_multiplier)
            if score > best_score:
                chosen_index = i
                best_score = score

        return images_embedded[chosen_index], images_recovered[chosen_index], marks[chosen_index], rs[chosen_index]

    
    # function to get a nice formated strings
    # useful when we construct the extracting code
    def get_formated_number_str(self, number, lenght):
        number = int(number)
        number = str(number)
        if len(number) == lenght:
            return number
        
        while len(number) != lenght:
            number = '0'+number
        
        return number


    # watermarking process
    def start_watermarking_process(self):
        # close other windows
        if self.watermarked_image_viewer != None and self.watermarked_image_viewer.isVisible():
            self.watermarked_image_viewer.close()

        if self.original_image_viewer != None and self.original_image_viewer.isVisible():
            self.original_image_viewer.close()

        if self.extract_window != None and self.extract_window.isVisible():
            self.extract_window.close()

        self.ui.loadingBar.setValue(0)
        
        # those will contain all watermarked images
        r_embedded_images = {}
        g_embedded_images = {}
        b_embedded_images = {}

        # pre process watermark
        # resize watermark to fit embedding space
        embedding_watermark = cv2.resize(self.watermark, (self.r_dcts['mask0'].shape[1], self.r_dcts['mask0'].shape[0]), cv2.INTER_CUBIC)
        # get normalized and scrambled mark
        embedding_watermark = (embedding_watermark / 255).astype(int)
        # set comparaison watermark
        self.compare_watermark = (embedding_watermark * 255).astype('uint8').copy()
        # crypt image
        embedding_watermark = image_scramble(embedding_watermark.astype('uint8'), self.key)
        # set black pixels to -1
        embedding_watermark[embedding_watermark == 0] = -1

        temporary_h, temporary_w = self.original_image.shape[:2]
        
        self.ui.loadingBar.setValue(10)

        # embedding
        for _id in self.masks:
            # embed
            embedded_r = embed(img=self.original_image, img_dct=self.r_dcts[_id], normalized_mark=embedding_watermark, img_psize=8, t=self.r_t[_id][1], b=self.r_t[_id][0])
            if _id == 'mask0':
                embedded_g = embed(img=self.original_image, img_dct=self.g_dcts[_id], normalized_mark=embedding_watermark, img_psize=8, t=self.g_t[_id][1], b=self.g_t[_id][0])
                embedded_b = embed(img=self.original_image, img_dct=self.b_dcts[_id], normalized_mark=embedding_watermark, img_psize=8, t=self.b_t[_id][1], b=self.b_t[_id][0])

            # reconstruct rgb images
            r_embedded_images[_id] = cv2.merge((embedded_r, self.green_channel[:embedded_r.shape[0]], self.blue_channel[:embedded_r.shape[0]])).reshape(embedded_r.shape[0], temporary_h, temporary_w, 3)
            if _id == 'mask0':
                g_embedded_images[_id] = cv2.merge((self.red_channel[:embedded_g.shape[0]], embedded_g, self.blue_channel[:embedded_g.shape[0]])).reshape(embedded_g.shape[0], temporary_h, temporary_w, 3)
                b_embedded_images[_id] = cv2.merge((self.red_channel[:embedded_b.shape[0]], self.green_channel[:embedded_b.shape[0]], embedded_b)).reshape(embedded_b.shape[0], temporary_h, temporary_w, 3)

        self.ui.loadingBar.setValue(25)

        # will contain extracted images and watermarks
        recovered_images_r, ex_marks_r = {}, {}
        recovered_images_g, ex_marks_g = {}, {}
        recovered_images_b, ex_marks_b = {}, {}

        # extract process
        for _id in self.masks:
            recovered_r, ex_mark_r = self.extract_process(r_embedded_images[_id], self.r_t[_id][1], self.r_t[_id][0], self.masks[_id], 'r')
            if _id == 'mask0':
                recovered_g, ex_mark_g = self.extract_process(g_embedded_images[_id], self.g_t[_id][1], self.g_t[_id][0], self.masks[_id], 'g')
                recovered_b, ex_mark_b = self.extract_process(b_embedded_images[_id], self.b_t[_id][1], self.b_t[_id][0], self.masks[_id], 'b')

            recovered_images_r[_id], ex_marks_r[_id] = recovered_r, ex_mark_r
            if _id == 'mask0':
                recovered_images_g[_id], ex_marks_g[_id] = recovered_g, ex_mark_g
                recovered_images_b[_id], ex_marks_b[_id] = recovered_b, ex_mark_b

        self.ui.loadingBar.setValue(50)

        # choose best T in every filter 
        for _id in self.masks:
            r_embedded_images[_id], recovered_images_r[_id], ex_marks_r[_id], self.r_t[_id][1] = self.best_psnr_different_t(r_embedded_images[_id], recovered_images_r[_id], ex_marks_r[_id], self.r_t[_id][1], _id)
            if _id == 'mask0':
                g_embedded_images[_id], recovered_images_g[_id], ex_marks_g[_id], self.g_t[_id][1] = self.best_psnr_different_t(g_embedded_images[_id], recovered_images_g[_id], ex_marks_g[_id], self.g_t[_id][1], _id)
                b_embedded_images[_id], recovered_images_b[_id], ex_marks_b[_id], self.b_t[_id][1] = self.best_psnr_different_t(b_embedded_images[_id], recovered_images_b[_id], ex_marks_b[_id], self.b_t[_id][1], _id)

        self.ui.loadingBar.setValue(60)

        score_mask0_r = 0
        score_mask0_g = 0
        score_mask0_b = 0

        chosen_mask = 'mask0'
        chosen_channel = 'r'
        chosen_psnr_imp = 0
        chosen_psnr_reco = 0
        overall_score = 0

        # evaluate and display psnrs
        # choose best watermarked image
        for _id in self.masks:
            psnr1 = psnr(r_embedded_images[_id], self.original_image)
            psnr4 = psnr(recovered_images_r[_id], self.original_image)

            if _id == 'mask0':
                psnr2 = psnr(g_embedded_images[_id], self.original_image)
                psnr3 = psnr(b_embedded_images[_id], self.original_image)
                psnr5 = psnr(recovered_images_g[_id], self.original_image)
                psnr6 = psnr(recovered_images_b[_id], self.original_image)

                score_mask0_r = evaluate_psnr(psnr1, self.imper_multiplier) + evaluate_psnr(psnr4, self.recovered_multiplier) + evaluate_mask(_id, self.mask_multiplier)
                score_mask0_g = evaluate_psnr(psnr2, self.imper_multiplier) + evaluate_psnr(psnr5, self.recovered_multiplier) + evaluate_mask(_id, self.mask_multiplier)
                score_mask0_b = evaluate_psnr(psnr3, self.imper_multiplier) + evaluate_psnr(psnr6, self.recovered_multiplier) + evaluate_mask(_id, self.mask_multiplier)

                maximum = max(score_mask0_r, score_mask0_b, score_mask0_g)

                if maximum == score_mask0_r:
                    chosen_psnr_imp  = psnr1
                    chosen_psnr_reco = psnr4
                elif maximum == score_mask0_b:
                    chosen_psnr_imp  = psnr3
                    chosen_psnr_reco = psnr6
                    chosen_channel = 'b'
                else:
                    chosen_psnr_imp  = psnr2
                    chosen_psnr_reco = psnr5
                    chosen_channel = 'g'
                
                overall_score = maximum
            else:
                new_score = evaluate_psnr(psnr1, self.imper_multiplier) + evaluate_psnr(psnr4, self.recovered_multiplier) + evaluate_mask(_id, self.mask_multiplier)

                if new_score > overall_score:
                    overall_score = new_score
                    chosen_channel = 'r'
                    chosen_mask = _id
                    chosen_psnr_imp = psnr1
                    chosen_psnr_reco = psnr4


        self.ui.loadingBar.setValue(90)

        #best settings
        self.best_channel = chosen_channel.upper()
        self.best_mask = chosen_mask.upper()
        self.psnr_watermarked = chosen_psnr_imp
        self.psnr_recovered = chosen_psnr_reco

        self.watermarked_image = r_embedded_images[chosen_mask]
        self.recovered_image   = recovered_images_r[chosen_mask]
        self.display_watermark = ex_marks_r[chosen_mask]

        if chosen_channel == 'g':
            self.watermarked_image = g_embedded_images[chosen_mask]
            self.recovered_image   = recovered_images_g[chosen_mask]
            self.display_watermark = ex_marks_g[chosen_mask]
        elif chosen_channel == 'b':
            self.watermarked_image = b_embedded_images[chosen_mask]
            self.recovered_image   = recovered_images_b[chosen_mask]
            self.display_watermark = ex_marks_b[chosen_mask]

        channel_code = {'r':0, 'g':1, 'b':2}
        mask_code = {'mask0':0, 'mask15':1, 'mask16':2, 'mask31':3}
        t_s = {'r':self.r_t, 'g':self.g_t, 'b':self.b_t}

        # construct decryption code from the chosen watermarked image
        # get LSBs
        another_code = self.watermarked_image.copy() % 2
        # multiply by mirrow
        another_code = another_code * cv2.flip(another_code, 1)
        # calculate sum
        another_code = another_code.sum()
        # xor between key and this constructed key
        crypted_key  = int(self.key) ^ int(another_code)

        theight, twidth = self.watermarked_image.shape[:2]
        theight, twidth = str(theight), str(twidth)
        
        # construct extracting code string
        self.code = str(len(theight)) + theight + str(len(twidth)) + twidth + str(channel_code[chosen_channel]) + str(mask_code[chosen_mask]) + self.get_formated_number_str(t_s[chosen_channel][chosen_mask][0], 3)\
                    + self.get_formated_number_str(t_s[chosen_channel][chosen_mask][1], 5) + self.get_formated_number_str(len(str(crypted_key)), 4)\
                    + str(crypted_key) + str(another_code)

        # psnr to display
        self.psnr_watermark = psnr(self.compare_watermark, self.display_watermark)
        self.current_watermark = self.watermark.copy()

        self.ui.loadingBar.setValue(100)



    # handles watermarking when button clicked
    def update(self):
        # if image loaded
        if self.image_loaded:
            # check if image watermarked
            if self.is_image_watermarked:
                # if yes then check if parametres are changed
                if not self.are_parametres_changed and not self.is_watermark_changed:
                    return
            
            # disable UI
            self.setEnabled(False)

            # clear image ui
            self.ui.watermarked_image.clear()

            # get values from gui
            self.key = self.ui.key_box.value()
            self.embedding_position = self.ui.search_box.value() - 1
            
            # watermarking process start here
            self.define_masks()
            self.calculate_dcts_and_best_blocks()
            self.start_watermarking_process()

            # reset some states
            self.is_image_watermarked = True
            self.are_parametres_changed = False
            self.is_watermark_changed = False
        
        self.update_gui()
        self.setEnabled(True)
    

    # update button gui
    def update_button_gui_update(self):
        text = 'Update'
        if not self.is_image_watermarked:
            text = 'Watermark'
        
        self.ui.update_btn.setText(text)


    # handles gui updates
    def update_gui(self):
        # if image loaded enable update button
        if self.image_loaded:
            self.ui.update_btn.setEnabled(True)

        self.ui.save_btn.setEnabled(self.is_image_watermarked)

        self.ui.actionExtract_Visualizer.setEnabled(self.is_image_watermarked)

        # update the GUI for update button
        self.update_button_gui_update()

        self.ui.outputkey_field.setText(self.code)
        
        number_display = self.psnr_watermarked
        if number_display > 1038.0:
            number_display = 999999
        
        self.ui.watermarked_psnr.setText('<html><head/><body><p><span style=" font-size:10pt; font-weight:600; color:#ff0000;">'+str(number_display)+'</span></p></body></html>')

        # if parametres are changed enable update button
        if self.ui.update_btn.text() == 'Update':
            self.ui.update_btn.setEnabled(self.are_parametres_changed or self.is_watermark_changed)

        self.setWindowTitle('Watermarking Program')
        
        if self.image_loaded and self.ui.update_btn.text() == 'Update':
            if self.is_watermark_changed:
                self.setWindowTitle(self.windowTitle() + ' * ' + 'watermark changed')
            
            if self.are_parametres_changed:
                self.setWindowTitle(self.windowTitle() + ' * ' + 'parametres changed')

        self.display_images()


    # display original and watermarked image
    def display_images(self):
        if self.image_loaded:
            pixmap = getPixmap(self.original_image)
            self.ui.original_image.setPixmap(pixmap.scaled(self.ui.original_image.size()))

        if self.is_image_watermarked:
            pixmap = getPixmap(self.watermarked_image)
            self.ui.watermarked_image.setPixmap(pixmap.scaled(self.ui.watermarked_image.size()))
    

    
    ###################################################################
    def reset_all_variables(self):
        self.setWindowTitle('Watermarking Program')
        self.is_image_watermarked = False
        self.are_parametres_changed = False
        self.is_watermark_changed = False
        self.masks_defined = False
        self.dct_calculated = False
        self.position_changed_state = False
        self.watermarked_image = []
        self.original_image = []
        self.image_loaded = []
        self.ui.original_image.clear()
        self.ui.watermarked_image.clear()
        self.best_channel = 'r'
        self.best_mask = 'mask0'
        self.psnr_watermarked = 0
        self.psnr_recovered = 0
        self.psnr_watermark = 0
        self.code = ''
        self.image_name = ''
        self.ui.loadingBar.setValue(0)
        