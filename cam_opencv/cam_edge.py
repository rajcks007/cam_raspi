from lib import *
from cam_setup import *
from cam_colour import *

def edage_fn():

    # import function
    from cam_main import image
    
    gray, mask = colour_fn()                             # call function

    # Preprocess the image and and computing an edge map
    blurred = cv2.GaussianBlur(image, (7, 7), cv2.BORDER_DEFAULT)
    edged = cv2.Canny(blurred, 50, 250, apertureSize = 5,  
                                        L2gradient = True)

    # find contours in the edge map, then sort them by their
    # size in descending order
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    displayCnt = None
	
    # loop over the contours
    for c in cnts:                             # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.05 * peri, True)
    
        # if the contour has four vertices, then we have found
        # the thermostat display
        if len(approx) == 4:
            displayCnt = approx
            break

    # extract the display, apply a perspective transform to it
    if displayCnt is not None:
        warped = four_point_transform(gray, displayCnt.reshape(4, 2))
        output = four_point_transform(image, displayCnt.reshape(4, 2))
        # Show the combined image
        # Convert warped image (2D grayscale) to 3 channels
        warped_3channel = cv2.cvtColor(warped, cv2.COLOR_GRAY2BGRA)
        # cv2.imshow("Warped and Output", numpy.hstack((warped_3channel, output)))

    return edged, warped_3channel, output

