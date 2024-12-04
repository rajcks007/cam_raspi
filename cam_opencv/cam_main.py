from lib import *
from cam_setup import *
from cam_colour import *
from cam_digit import *

while(1):
     
    cv2.waitKey(50)

    # capture the array in BGR
    cropped_image = picam2.capture_array()

    # Crop the image from the sides
    image = cropped(cropped_image)                                                                                 

    gray = colour_fn(image)                 # call function

    image, tr_opene = digit_fn(gray, image)

    cv2.imshow('thresh_img', tr_opene)

    # Show the image with the bounding boxes drawn
    cv2.imshow("Detected Digits", image)

    
cv2.waitKey(0)

cv2.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()
