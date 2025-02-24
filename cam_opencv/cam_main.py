from lib import *
from cam_setup import *
from cam_colour import *
from cam_rectengle import *
from cam_digit import *
from cam_symbol import *
from data_validate import *

button = Button(17)
start_time = time.time()  # Record the start time

while(button.when_pressed):
    
    elapsed_time = time.time() - start_time  # Calculate the elapsed time
    if elapsed_time > 10:  # If 10 seconds have passed
        break  # Exit the loop

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

# Release the camera and close the window
picam2.stop_preview()
picam2.stop()
cv2.destroyAllWindows()

from digit_data import *
from symbol_data import *

print("for data_set 1")
data_valid(data_1)
print("for data_set 2")
data_valid(data_2)
