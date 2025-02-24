from lib import *
from cam_setup import *
from cam_colour import *

def edage_fn(image, gray):

    # Preprocess the image and and computing an edge map
    blurred = cv2.GaussianBlur(gray, (5, 5), cv2.BORDER_DEFAULT)
    edged = cv2.Canny(blurred, 150, 350, apertureSize = 5, L2gradient = True)

    # find contours in the edge map, then sort them by their size in descending order
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    displayCnt = None

    cv2.waitKey(10)
	
    # loop over the contours
    for c in cnts:                          # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    
        # if the contour has four vertices, then we have found the display
        if len(approx) == 4:
            displayCnt = approx
            break

    cv2.waitKey(10)

    # extract the display, apply a perspective transform to it
    if displayCnt is not None:
        warped = four_point_transform(gray, displayCnt.reshape(4, 2))
        output = four_point_transform(image, displayCnt.reshape(4, 2))

    # Return the edged,output and warped image
    return edged, output, warped