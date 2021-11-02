import cv2
from PIL import Image
import numpy as np


def compressionImage(im, Destination_File):
    im.save(Destination_File, "jpeg")  # , quality=75
    # Adopted Histogram Equalization ////////////////////////////////////////////////
    # /////////////////////////////
    ContrastLimit = 0.5
    Gridsize = 16
    # /////////////////////////////
    # read image
    n = np.fromfile(Destination_File, np.uint8)
    img2 = cv2.imdecode(n, cv2.IMREAD_COLOR)

    # convert
    yuv = cv2.cvtColor(img2, cv2.COLOR_BGR2YUV)
    lab_planes = cv2.split(yuv)
    clahe = cv2.createCLAHE(clipLimit=ContrastLimit, tileGridSize=(Gridsize, Gridsize))
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv2.merge(lab_planes)
    bgr = cv2.cvtColor(lab, cv2.COLOR_YUV2BGR)

    # convert CV to PIL
    adjusted_2 = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    im3 = Image.fromarray(adjusted_2)

    im3.save(Destination_File, "jpeg")
    im3.close()
