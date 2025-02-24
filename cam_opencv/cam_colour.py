from lib import *
from cam_setup import *

def colour_fn(image):

    # # Convert BGR to GRAY
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

    ## blure image using gaussianblur filter
    # blurred = cv2.GaussianBlur(gray, (5, 5), cv2.BORDER_DEFAULT)

    # # Threshold the GRAY image to get only colors
    # mask = cv2.inRange(gray, 100, 205)

    # Bitwise-AND mask and original image
    # res = cv2.bitwise_and(image,image, mask= mask)
        
    # Threshold the warped image, then apply a series of morphological operations to clean up the thresholded image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 7))
    tr_opene = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Return the gray image
    return gray, tr_opene