import cv2
from picamera2 import *
from picamera2 import Picamera2 
from libcamera import controls
import numpy
import imutils
from imutils.perspective import four_point_transform
from imutils import contours
import time

picam2 = Picamera2()

# start camera
picam2.start(show_preview=False)

# Define the desired video resolution (width, height)
video_resolution = (640, 480)  # 640x480 resolution

# Configure the camera with the desired resolution
config = picam2.create_video_configuration(main={"size": video_resolution})

# Set controls
picam2.set_controls({
    "Contrast": 0.7,       # Contrast range: -1.0 to 1.0
    "Brightness": -0.1,     # Brightness range: -1.0 to 1.0
    "Saturation": -1.0       # Adjust saturation
})

# set focus of camera
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 30.0})

while(1):

    # capture the array in BGR
    image = picam2.capture_array()

    cv2.waitKey(10)

    # Convert BGR to GRAY
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

    # Threshold the GRAY image to get only colors
    # mask = cv2.inRange(gray, 100, 205)                          
    # cv2.waitKey(10)

    # Preprocess the image and and computing an edge map
    blurred = cv2.GaussianBlur(gray, (5, 5), cv2.BORDER_DEFAULT)
    edged = cv2.Canny(blurred, 150, 350, apertureSize = 5,  
                                        L2gradient = True)
    # edged = cv2.Canny(blurred, 50, 250, 255)

    # find contours in the edge map, then sort them by their
    # size in descending order
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    displayCnt = None

    cv2.waitKey(10)
	
    # loop over the contours
    for c in cnts:                             # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    
        # if the contour has four vertices, then we have found
        # the thermostat display
        if len(approx) == 4:
            displayCnt = approx
            break

    cv2.waitKey(10)

    # extract the display, apply a perspective transform to it
    if displayCnt is not None:
        warped = four_point_transform(gray, displayCnt.reshape(4, 2))
        output = four_point_transform(image, displayCnt.reshape(4, 2))

    cv2.waitKey(10)


    """
    cv2.imshow('Gray', gray)
    cv2.imshow('res', res)
    cv2.imshow('preview', image)

    cv2.imshow("Gaussian Smoothing",numpy.hstack((mask, edged)))
    """

    cv2.imshow('edged', edged)

    # threshold the warped image, then apply a series of morphological operations to cleanup the thresholded image
    thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    adaptive_thresh = cv2.adaptiveThreshold(warped, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 1)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
    tr_opene = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    tr_ad_opene = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel)

    cv2.imshow("thresh_img", numpy.hstack((tr_opene, tr_ad_opene)))
	
    cv2.waitKey(10)

    # find contours in the thresholded image, then initialize the digit contours lists
    cnts = cv2.findContours(tr_opene.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    digitCnts = []
	
    # loop over the digit area candidates
    for c in cnts:
        # compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)

        # Draw the bounding box around each digit
        output = cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle with thickness 2

        # if the contour is sufficiently large, it must be a digit
        if w >= 15 and (h >= 30 and h <= 40):
            digitCnts.append(c)

    # Show the image with the bounding boxes drawn
    cv2.imshow("Detected Digits", output)

    # # sort the contours from left-to-right, then initialize the actual digits themselves
    # digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
    # digits = []

    
cv2.waitKey(0)

cv2.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()
