import numpy as np
import new_utils

# function will handle extract process
def extract(embedded_img, img_psize=8, t=10, b=10, key=3994, mode='embedding_mode'):
    c, h, w = embedded_img.shape
    img_h, img_w = h, w
    embedded_img = embedded_img.reshape(c, h*w)

    # extract dct
    embedded_img_dct = np.apply_along_axis(new_utils.forwardProcess, 1, embedded_img, shape=(h, w))

    # Calculate auto mark size
    mark_w = embedded_img_dct.shape[2]
    mark_h = embedded_img_dct.shape[1]

    c, h, w, d, _ = embedded_img_dct.shape
    embedded_img_dct = embedded_img_dct.reshape(c, h*w, d*d)

    # extracting
    extracted_mark = embedded_img_dct[:, :, b]
    extracted_mark = np.float32(np.where(extracted_mark < 0, -1, 1))

    t = int(t)
    # in embedding mode we need to get all possible T values
    # to test best reversed image
    T = np.arange(t, 10, -10)
    # however in extracting mode we need 1 T value provided by extracting code by user
    if mode == 'extracting_mode':
        T = np.array([float(t)])    

    # get the right shape to perform operation correctly
    T = np.float32(np.repeat(T, len(extracted_mark[0])).reshape(T.shape[0], len(extracted_mark[0])))
    extracted_mark *= T

    # reverse to original state
    embedded_img_dct[:, :, b] -= extracted_mark
    
    # reconstruct extracted watermark and extracted original image
    extracted_mark /= T
    extracted_mark[extracted_mark == -1] = 0
    extracted_mark = extracted_mark.reshape(T.shape[0], mark_h * mark_w)
    extracted_mark = extracted_mark.astype('uint8')
    extracted_mark = np.apply_along_axis(new_utils.image_scramble, 1, extracted_mark, key=key, shape=(mark_h, mark_w))
    extracted_mark = extracted_mark * 255
    extracted_mark = extracted_mark.reshape(T.shape[0], mark_h, mark_w)
    extracted_mark = extracted_mark.astype('uint8')

    embedded_img_dct = embedded_img_dct.reshape(c, h*w*d*d)
    extracted_original = np.apply_along_axis(new_utils.backwardProcess, 1, embedded_img_dct, shape=(h, w))
    extracted_original = extracted_original[:, :img_h, :img_w]

    return extracted_original.reshape(extracted_original.shape[0], extracted_original.shape[1]*extracted_original.shape[2]), extracted_mark.reshape(c, mark_h, mark_w)