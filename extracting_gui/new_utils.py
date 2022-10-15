import cv2
import numpy as np
from math import ceil
import scipy.fftpack as fft


def extract_patches(img, patch_size):
    h, w = img.shape[:2]

    # calculate new hight and width to pad the image
    nh, nw = ceil(h / patch_size) * patch_size, ceil(w / patch_size) * patch_size

    # pad image to make it devisible by the patch size
    # just a note for the future maybe it will be useful
    # we can re-destribute the new rows and columns in a way that we add half of the new rows in top and the other half in bottom
    # same thing for columns half left, half right
    img = cv2.copyMakeBorder(img, 0, nh-h, 0, nw-w, cv2.BORDER_REPLICATE)

    # split the image into blocks
    patches = np.array(np.hsplit(img, nw / patch_size))
    patches = np.array(np.split(patches, nh / patch_size, axis=1))

    return patches


def fusion_patches(patches, axis=1):
    patches = np.concatenate(patches, axis=1)
    patches = np.concatenate(patches, axis=1)

    return patches


# dct function
def dct(img, ax=2):
    return fft.dct( fft.dct( img, type=2, norm='ortho', axis=ax ), axis=ax+1, norm='ortho', type=2 )


#inverse dct
def idct(dct_values, ax=2):
    return fft.idct( fft.idct( dct_values, type=2, norm='ortho', axis=ax ), axis=ax+1, norm='ortho', type=2 )



# this function will split image into blocks and calculate dct of every block
def forwardProcess(image, patch_size=8, shape=(0, 0)):
    if shape[0] != 0 and shape[1] != 0:
        image = image.reshape(shape[0], shape[1])
    image = np.float64(image)
    image = extract_patches(image, patch_size)
    image = dct(image)
    return image


# this function will calculate inverse dct of every block and fusion them to make regular image
def backwardProcess(image, patch_size=8, shape=(0, 0)):
    if shape[0] != 0 and shape[1] != 0:
        image = image.reshape(shape[0], shape[1], patch_size, patch_size)
    image = idct(image)
    image = np.round(fusion_patches(image))
    image = np.clip(image, 0, 255)

    return image.astype("uint8")


# get pixmap to display image on UI
def getPixmap(img):
    from PyQt5.QtGui import QPixmap, QImage
    # convert img to a good format
    img = img.astype(np.uint8, order='C', casting='unsafe')
    #if len(img.shape) == 3:
        #img = cv2.cvtColor(img, cv2.COLOR_YCrCb2BGR)
    # hyperparametres
    height, width = img.shape[:2]
    bytesPerLine = width
    # assume that the image is a grayscaled image
    image_format = QImage.Format_Grayscale8
    
    # if image is not grayscaled
    if len(img.shape) == 3:
        # change format to RGB
        bytesPerLine *= 3
        image_format = QImage.Format_RGB888

    # create QImage
    image = QImage(img.data, width, height, bytesPerLine, image_format)
    image = image.rgbSwapped()

    # get PIXMAP to display image on the UI
    return QPixmap.fromImage(image)


# function that crypte our image using a key for mersenne twister
def image_scramble(image, key, shape=(0, 0)):
    # set seed to mersenne twister
    np.random.seed(key)
    if shape[0] != 0 and shape[1] != 0:
        image = image.reshape(shape[0], shape[1])

    # get maximum dimenstion to not have any overflow
    max_dimension = max(image.shape[:2])
    min_dimension = min(image.shape[:2])
    
    # generate random set on number with lenght of 16
    key_line = np.random.uniform(-1, 1, 16)
    # repeat this set max_dimension times
    key_line = np.repeat([key_line], max_dimension, axis=0).flatten()
    # replace set 0s and 1s
    key_line = np.where(key_line >= 0, 1, 0)

    # apply XOR operation
    image = image ^ key_line[:len(image[0])]
    # calculate transpose of the image
    image = image.T
    # apply XOR operation
    image = image ^ key_line[:len(image[0])]

    return image.T