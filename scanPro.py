import numpy as np
import cv2

def adaptive_threshold(fname):
    imgfile = fname
    img = cv2.imread(imgfile, cv2.IMREAD_GRAYSCALE)

    r = 600.0 / img.shape[0]
    dim = (int(img.shape[1] * r), 600)
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    blur = cv2.GaussianBlur(img, (5,5), 0)
    result_with_blur = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_RHRESH_MEAN_C, cv2.THRESH_BINARY, 21, 10)
    result_with_blur.save('%s_gray.jpg'%fname)