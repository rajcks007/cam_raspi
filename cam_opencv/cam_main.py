from lib import *
from cam_setup import *
from cam_colour import *
from cam_rectengle import *
from cam_digit import *
from cam_symbol import *
from data_validate import *
from spi import *

global picam2
picam2 = Picamera2()

# Configure the button on GPIO pin 17
button = Button(17, pull_up=False, bounce_time=0.2)
Led_1 = LED(27)
Led_2 = LED(22)

Led_1.on()

error, ok = spi_init()

# Check if running in a headless environment
if not os.environ.get("DISPLAY"):
    cv2.imshow = lambda *args, **kwargs: None  # Disable imshow

# Callback function when the button is pressed
def on_button_pressed():
    start_time = time.time()  # Record the start time

    picam_2 = cam_init(picam2)

    Led_2.on()

    while(1):

        elapsed_time = time.time() - start_time  # Calculate the elapsed time
        if elapsed_time > 10:  # If 10 seconds have passed
            break  # Exit the loop

        cv2.waitKey(50)

        # capture the array in BGR
        cropped_image = picam_2.capture_array()

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
        cv2.imshow("thresh_img", tr_opene)

        # Show the image with the bounding boxes drawn
        cv2.imshow("Detected Digits", image)

        # # If the 'Esc' key is pressed, close the window
        # if keyboard.is_pressed('esc'):  # ASCII value of 'Esc' is 27
        #     break

    try:
        from digit_data import data_1, data_2
    except:
        print("Error importing digit_data from the files.")
        send_message(error)

    try:
        from symbol_data import symbol_1, symbol_2 # Adjust these imports based on the actual variables you need
    except:
        print("Error importing symbol_data from the files.")
        #send_message(error)

    try:
        print("for data_set 1")
        data_valid(data_1)
    except:
        print("Error validating data_set 1")
        send_message(error)

    try:
        print("for data_set 2")
        data_valid(data_2)
    except: 
        print("Error validating data_set 2")
        send_message(error)

    # Check the symbol data
    try:
        print("Checking symbol data...")
        if 1 in symbol_1:
            print("symbol_1 contains at least one 1")
            spi.writebytes(ok)
        if 1 in symbol_2:
            print("symbol_2 contains at least one 1")
            spi.writebytes(ok)
    except:
        print("Error processing symbol data.")
        #send_message(error) 
    
    # Once processing is complete, clear the file contents
    with open('/home/raj/Desktop/cam/cam_opencv/digit_data.py', 'w') as file:
        file.write('')
    with open('/home/raj/Desktop/cam/cam_opencv/symbol_data.py', 'w') as file:
        file.write('')

    Led_2.off()

    # Stop the camera
    cam_deinit(picam2)
    cv2.destroyAllWindows()

# Bind the callback to the button's press event
button.when_pressed = on_button_pressed

print("Waiting for button press. Press Ctrl+C to exit.")
pause()  # Keeps the script running
