import cv2
import numpy as np
from math import ceil, log10
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


# calculate mse
def mse(I1, I2):
    N = 1
    for x in I1.shape:
        N *= x
    return ((I1.astype(float) - I2.astype(float)) ** 2 ).sum() / (N)


# calculate psnr
def psnr(I1, I2):
    if I1.shape != I2.shape:
        return 0
    
    _mse = mse(I1, I2) + 0.000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001
    return 10 * log10(65025/_mse)


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

# function to calculate absolute maximum of DCT coefficent across all blocks
def maximum_dct_value(dct_values, b):
    return np.round(np.abs( ( dct_values.reshape(dct_values.shape[0] * dct_values.shape[1], dct_values.shape[2]**2) )[:, b] ).max())

# find value T based on a given DCT index
def find_value_t(dct_values, t, index):
    zigzag_indexes = [
                        0,
                        1, 8,
                        16, 9, 2,
                        3, 10, 17, 24,
                        32, 25, 18, 11, 4,
                        5, 12, 19, 26, 33, 40,
                        48, 41, 34, 27, 20, 13, 6,
                        7, 14, 21, 28, 35, 42, 49, 56,
                        57, 50, 43, 36, 29, 22, 15,
                        23, 30, 37, 44, 51, 58,
                        59, 52, 45, 38, 31,
                        39, 46, 53, 60,
                        61, 54, 47,
                        55, 62,
                        63
                     ]

    index = zigzag_indexes[index]
    maximum_value = maximum_dct_value(dct_values, index)
    maximum_value = max(maximum_value, 11)
    maximum_value += t
    
    return [index, maximum_value]


# REST OF FUNCTION ARE TO EVALUATE PSNR
def evaluate_psnr(psnr_value, multiplier):
    score = 0

    if psnr_value < 20:
        score -= (20 * multiplier)

    if psnr_value >= 20:
        score += ((1 * multiplier) + (int(psnr_value - round(psnr_value / 10)) * multiplier) )
    
    if psnr_value >= 40:
        score += ((2 * multiplier) + (int(psnr_value - round(psnr_value / 10)) * multiplier) )

    if psnr_value >= 50:
        score += ((3 * multiplier) + (int(psnr_value - round(psnr_value / 10)) * multiplier) )

    if psnr_value >= 60:
        score += ((4 * multiplier) + (int(psnr_value - round(psnr_value / 10)) * multiplier) )

    if psnr_value >= 75:
        score += ((5 * multiplier) + (int(psnr_value - round(psnr_value / 10)) * multiplier) )
    
    if psnr_value >= 90:
        score += ((6 * multiplier) + (int(psnr_value - round(psnr_value / 10)) * multiplier) )

    if psnr_value >= 100:
        score += ((7 * multiplier) + (int(psnr_value - round(psnr_value / 10)) * multiplier) )

    return score


def evaluate_mask(mask_string, multiplier):
    n = int(mask_string[4:])
    score = 0

    if n == 0:
        score += (3 * multiplier)
    
    if n > 1:
        score -= (1 * multiplier)
    
    if n >= 8:
        score -= (2 * multiplier)

    if n >= 16:
        score -= (3 * multiplier)

    return score


def evaluate_psnr_mark(psnr_value, multiplier):
    score = 0

    if psnr_value < 5:
        score -= (30 * multiplier)

    if psnr_value < 8:
        score -= (15 * multiplier)

    if psnr_value < 10:
        score -= (10 * multiplier)

    return score