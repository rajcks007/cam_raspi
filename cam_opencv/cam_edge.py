import cv2 as cv
from libcamera import controls
from picamera2 import Picamera2
import time 
import numpy as np
import imutils

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect
 
picam2 = Picamera2()

# Define the desired video resolution (width, height)
video_resolution = (640, 480)  # For example, 640x480 resolution

# Configure the camera with the desired resolution
config = picam2.create_video_configuration(main={"size": video_resolution})

picam2.start(show_preview=False)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 30.0})

cv.waitKey(100)

while(1):
    
    cv.waitKey(50)

    image = picam2.capture_array()

    # Convert BGR to GRAY
    gray = cv.cvtColor(image, cv.COLOR_BGRA2GRAY)
    gray_3channel = cv.cvtColor(gray, cv.COLOR_GRAY2BGRA)

    # Preprocess the image and and computing an edge map
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    edged = cv.Canny(blurred, 50, 200, 255)

    # Threshold the GRAY image to get only colors
    mask = cv.inRange(gray, 110, 255)

    # Bitwise-AND mask and original image
    res = cv.bitwise_and(image,image, mask= mask)

    # cv.imshow('Gray', gray)
    # cv.imshow("preview",np.hstack((image, gray_3channel)))
    cv.imshow("Gaussian Smoothing",np.hstack((mask, edged)))

    # find contours in the edge map, then sort them by their
    # size in descending order
    cnts = cv.findContours(edged.copy(), cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv.contourArea, reverse=True)
    displayCnt = None
	
    # loop over the contours
    for c in cnts:                             # approximate the contour
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.02 * peri, True)
    
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
        warped_3channel = cv.cvtColor(warped, cv.COLOR_GRAY2BGRA)
        cv.imshow("Warped and Output", np.hstack((warped_3channel, output)))

    
cv.waitKey(0)

cv.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()
