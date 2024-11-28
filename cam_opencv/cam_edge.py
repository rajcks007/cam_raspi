import cv2 as cv
from picamera2 import Picamera2
from libcamera import controls
import time 
import numpy as np
 
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

    
cv.waitKey(0)

cv.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()
