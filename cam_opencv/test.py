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

# Set controls
picam2.set_controls({
    "Contrast": 0.8,       # Contrast range: -1.0 to 1.0
    "Brightness": -0.2,     # Brightness range: -1.0 to 1.0
    "Saturation": -1.0       # Adjust saturation
})

# set focus of camera
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 35.0})

while(1):


    cv2.waitKey(50)

    # capture the array in BGR
    cropped_image = picam2.capture_array()

    # Define the cropping parameters (e.g., crop 50 pixels from each side)
    left_crop = 0    # Number of pixels to crop from the left
    right_crop = 250   # Number of pixels to crop from the right
    top_crop = 0    # Number of pixels to crop from the top
    bottom_crop = 30  # Number of pixels to crop from the bottom

    # Crop the image from all sides (left, right, top, and bottom)
    image = cropped_image[top_crop:-bottom_crop, left_crop:-right_crop] if right_crop > 0 and bottom_crop > 0 else \
            cropped_image[top_crop:, left_crop:-right_crop] if bottom_crop > 0 else \
            cropped_image[top_crop:-bottom_crop, left_crop:] if right_crop > 0 else \
            cropped_image[top_crop:, left_crop:]  # Fallback case where no cropping is done on one or more sides

    # Convert BGR to GRAY
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    # blurred = cv2.GaussianBlur(gray, (5, 5), cv2.BORDER_DEFAULT)

    # threshold the warped image, then apply a series of morphological operations to cleanup the thresholded image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 7))
    tr_opene = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)

    cv2.imshow('thresh_img', tr_opene)

    # find contours in the thresholded image, then initialize the digit contours lists
    cnts = cv2.findContours(tr_opene.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    digitCnts = []
    symbolCnts = []
	
    # loop over the digit area candidates
    for c in cnts:
        # compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)
        # if the contour is sufficiently large, it must be a digit
        if (w >= 30 and w <= 150) and (h >= 200 and h <= 240):
            digitCnts.append(c)
            # Draw the bounding box around each digit
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) 
        
        # If the contour is within the symbol size range
        # (symbols might be smaller or larger than digits, depending on your use case)
        elif (w >= 25 and w <= 100) and (h >= 25 and h <= 80):
            symbolCnts.append(c)
            # Draw the bounding box around each symbol in blue
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)  # Blue for symbols

    # Show the image with the bounding boxes drawn
    cv2.imshow("Detected Digits", image)

    # # sort the contours from left-to-right, then initialize the
    # # actual digits themselves
    # digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
    # digits = []

    # # loop over each of the digits
    # for c in digitCnts:
    #     # extract the digit ROI
    #     (x, y, w, h) = cv2.boundingRect(c)
    #     roi = thresh[y:y + h, x:x + w]

    #     # compute the width and height of each of the 7 segments
    #     # we are going to examine
    #     (roiH, roiW) = roi.shape
    #     (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
    #     dHC = int(roiH * 0.05)

    #     # define the set of 7 segments
    #     segments = [
    #         ((0, 0), (w, dH)),    # top
    #         ((0, 0), (dW, h // 2)),    # top-left
    #         ((w - dW, 0), (w, h // 2)),    # top-right
    #         ((0, (h // 2) - dHC), (w, (h // 2) + dHC)), # center
    #         ((0, h // 2), (dW, h)),    # bottom-left
    #         ((w - dW, h // 2), (w, h)),    # bottom-right
    #         ((0, h - dH), (w, h))    # bottom
    #     ]
    #     on = [0] * len(segments)

    cv2.imshow("Detected Digits", image)

    
cv2.waitKey(0)

cv2.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()