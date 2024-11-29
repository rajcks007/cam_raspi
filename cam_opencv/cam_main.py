from lib import *
from cam_setup import *
from cam_colour import *
from cam_edge import edage_fn

while(1):
    
    cv2.waitKey(50)

    # capture the array in BGR
    image = picam2.capture_array()

    colour_fn()

    edged, warped_3channel, output = edage_fn ()


    """
    cv2.imshow('Gray', gray)
    cv2.imshow('res', res)
    cv2.imshow('preview', image)

    cv2.imshow("Gaussian Smoothing",numpy.hstack((mask, edged)))
    """

    
    cv2.imshow('edged', edged)
    cv2.imshow("Warped and Output", numpy.hstack((warped_3channel, output)))

    
cv2.waitKey(0)

cv2.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()
