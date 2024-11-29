from lib import *
from cam_setup import *

def colour_fn():

    from cam_main import image          # import function

    # # Convert BGR to GRAY
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

    # Threshold the GRAY image to get only colors
    mask = cv2.inRange(gray, 100, 205)

    # Bitwise-AND mask and original image
    # res = cv2.bitwise_and(image,image, mask= mask)

    return gray, mask
