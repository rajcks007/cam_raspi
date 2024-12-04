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

    # Return the gray image
    return gray