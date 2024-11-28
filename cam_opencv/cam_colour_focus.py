import cv2 as cv
from picamera2 import Picamera2
from libcamera import controls
import time 
import numpy as np
 
picam2 = Picamera2()

picam2.start(show_preview=True)
# picam2.start()
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 30.0})

while(1):
    
    image = picam2.capture_array()
 
    # # Convert BGR to HSV
    # hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # Convert BGR to GRAY
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
 
    # # define range of color in HSV
    # lower_colour = np.array([86,3,25])
    # upper_colour = np.array([255,160,122])
 
    # # Threshold the HSV image to get only colors
    # mask = cv.inRange(hsv, lower_colour, upper_colour)

    # Threshold the GRAY image to get only colors
    mask = cv.inRange(gray, 110, 255)

    # Bitwise-AND mask and original image
    res = cv.bitwise_and(image,image, mask= mask)
 
    # cv.imshow('frame',image)
    # cv.imshow('res',res)
    # cv.imshow('Gray', gray)
    cv.imshow('mask',mask)

cv.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()