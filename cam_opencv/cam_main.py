from lib import *
from cam_setup import *
from cam_colour import *
from cam_rectengle import *
from cam_digit import *
from cam_symbol import *

while(1):
     
    cv2.waitKey(50)

    # capture the array in BGR
    cropped_image = picam2.capture_array()

    # Crop the image from the sides
    image = cropped(cropped_image)                                                                                 

    # gray and threshold image
    gray, tr_opene = colour_fn(image)

    # extract digit and symbol from image and indicate with rectangle
    image, digitCnts, symbolCnts = rectengle_fn(tr_opene, image)

    # recive segment buffer
    digit_fn(tr_opene, digitCnts)

    symbol_fn(tr_opene, symbolCnts)
    
    # Show the threshold image
    cv2.imshow('thresh_img', tr_opene)

    # Show the image with the bounding boxes drawn
    cv2.imshow("Detected Digits", image)

    # # If the 'Esc' key is pressed, close the window
    # if keyboard.is_pressed('esc'):  # ASCII value of 'Esc' is 27
    #     break

cv2.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()
