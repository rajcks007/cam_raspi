from lib import *
from cam_setup import *

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = numpy.linalg.norm(br - bl)
    widthB = numpy.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = numpy.linalg.norm(tr - br)
    heightB = numpy.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = numpy.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def order_points(pts):
    rect = numpy.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = numpy.diff(pts, axis=1)
    rect[0] = pts[numpy.argmin(s)]
    rect[2] = pts[numpy.argmax(s)]
    rect[1] = pts[numpy.argmin(diff)]
    rect[3] = pts[numpy.argmax(diff)]
    
    return rect

cv2.waitKey(100)

while(1):
    
    cv2.waitKey(50)

    # capture the array in BGR
    image = picam2.capture_array()

    # Convert BGR to HSV
    # hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Convert BGR to GRAY
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    gray_3channel = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGRA)

    # define range of color in HSV
    lower_colour = numpy.array([86,3,25])
    upper_colour = numpy.array([255,160,122])

    # Threshold the HSV image to get only colors
    # mask = cv2.inRange(hsv, lower_colour, upper_colour)

    # Threshold the GRAY image to get only colors
    mask = cv2.inRange(gray, 110, 255)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(image,image, mask= mask)

    # Preprocess the image and and computing an edge map
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 255)

    # cv2.imshow('Gray', gray)
    # cv2.imshow("preview",numpy.hstack((image, gray_3channel)))
    cv2.imshow("Gaussian Smoothing",numpy.hstack((mask, edged)))

    # find contours in the edge map, then sort them by their
    # size in descending order
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    displayCnt = None
	
    # loop over the contours
    for c in cnts:                             # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    
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
        cv2.imshow("Warped and Output", numpy.hstack((warped_3channel, output)))

    
cv2.waitKey(0)

cv2.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()
