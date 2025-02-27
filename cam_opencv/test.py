import os
import cv2
from picamera2 import *
from picamera2 import Picamera2 
from libcamera import controls
import numpy
import imutils
import time
import keyboard
from gpiozero import *
from signal import pause
import spidev

picam2 = Picamera2()

# Configure the button on GPIO pin 17
button = Button(17, pull_up=False, bounce_time=0.2)
Led_1 = LED(27)
Led_2 = LED(22)

# We only have SPI bus 0 available to us on the Pi
bus = 0

#Device is the chip select pin. Set to 0 or 1, depending on the connections
device = 1

# Enable SPI
spi = spidev.SpiDev()

# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)
spi.max_speed_hz = 18000000  # Set speed to 18 Mbit/s
spi.mode = 0  # SPI Mode 0: (CPOL=0, CPHA=0) -> first edge sampling

error = [0x24]  # Error code to send if there is an issue with the data ($)
ok = [0x2A]  # OK code to send if the data is valid (*)

Led_1.on()

# Check if running in a headless environment
if not os.environ.get("DISPLAY"):
    cv2.imshow = lambda *args, **kwargs: None  # Disable imshow

# Callback function when the button is pressed
def on_button_pressed():
    # start camera
    picam2.start(show_preview=False)

    Led_2.on()

    # Set controls
    picam2.set_controls({
        "Contrast": 0.9,       # Contrast range: -1.0 to 1.0
        "Brightness": -0.1,     # Brightness range: -1.0 to 1.0
        "Saturation": -1.8       # Adjust saturation
    })
    # set focus of camera
    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 45.0})
    start_time = time.time()  # Record the start time
    # Dictionary to store data dynamically for each detected digit (based on idx)
    digit_data = {}
    # Define a dictionary to store the symbol data
    symbol_data = {}

    while(1):

        elapsed_time = time.time() - start_time  # Calculate the elapsed time
        if elapsed_time > 10:  # If n seconds have passed
            break  # Exit the loop

        cv2.waitKey(50)

        # capture the array in BGR
        cropped_image = picam2.capture_array()

        # Define the cropping parameters (e.g., crop 50 pixels from each side)
        left_crop = 60    # Number of pixels to crop from the left
        right_crop = 280   # Number of pixels to crop from the right
        top_crop = 60    # Number of pixels to crop from the top
        bottom_crop = 70  # Number of pixels to crop from the bottom

        # Crop the image from all sides (left, right, top, and bottom)
        image = cropped_image[top_crop:-bottom_crop, left_crop:-right_crop] if right_crop > 0 and bottom_crop > 0 else \
                cropped_image[top_crop:, left_crop:-right_crop] if bottom_crop > 0 else \
                cropped_image[top_crop:-bottom_crop, left_crop:] if right_crop > 0 else \
                cropped_image[top_crop:, left_crop:]  # Fallback case where no cropping is done on one or more sides

        # Convert BGR to GRAY
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        # blurred = cv2.GaussianBlur(gray, (5, 5), cv2.BORDER_DEFAULT)

        # threshold the image, then apply a series of morphological operations to cleanup the thresholded image
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
            if (w >= 20 and w <= 150) and (h >= 90 and h <= 230):
                digitCnts.append(c)
                # Draw the bounding box around each digit
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) 

            # If the contour is within the symbol size range
            # (symbols might be smaller or larger than digits, depending on your use case)
            elif (w >= 25 and w <= 100) and (h >= 25 and h <= 80):
                symbolCnts.append(c)
                # Draw the bounding box around each symbol in blue
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)  # Red for symbols

        # Show the image with the bounding boxes drawn
        cv2.imshow("Detected Digits", image)

        # Loop over each of the digits and check the segments
        for idx,c in enumerate(digitCnts):  # 'idx' will give us the digit index
            # Extract the digit ROI
            (x, y, w, h) = cv2.boundingRect(c)
            roi = tr_opene[y:y + h, x:x + w]

            # Compute the width and height of each of the 7 segments
            (roiH, roiW) = roi.shape
            (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
            dHC = int(roiH * 0.05)

            # Define the set of 7 segments in terms of their positions relative to the digit's bounding box
            segments = [
                ((0, 0), (w, dH)),    # top
                ((0, 0), (dW, h // 2)),    # top-left
                ((w - dW, 0), (w, h // 2)),    # top-right
                ((0, (h // 2) - dHC), (w, (h // 2) + dHC)),  # center
                ((0, h // 2), (dW, h)),    # bottom-left
                ((w - dW, h // 2), (w, h)),    # bottom-right
                ((0, h - dH), (w, h))    # bottom
            ]

            # List to track which segments are "on"
            on = [0] * len(segments)

            # Check each segment to see if it's "on" (i.e., if there are white pixels in that segment)
            for i, (start, end) in enumerate(segments):
                (x1, y1) = start
                (x2, y2) = end

                # Crop the segment from the digit's ROI
                segment = roi[y1:y2, x1:x2]

                # Count the number of white pixels (255) in the segment
                white_pixels = numpy.sum(segment == 255)

                # If the number of white pixels is above a certain threshold, we consider this segment "on"
                if white_pixels > 0.5 * segment.size:  # Adjust threshold as needed
                    on[i] = 1  # Segment is "on"

            # Print the status of the segments for each digit
            # print(f"Digit_{idx + 1} at ({x}, {y}): {on}")

            # Dynamically store the data for each digit (using idx as the key)
            digit_data[f"data_{idx + 1}"] = digit_data.get(f"data_{idx + 1}", []) + [on]

            # you can save data after each loop or at set intervals to prevent data loss
            with open('/home/raj/Desktop/cam/cam_opencv/digit_data.py', 'w') as file:
                for idx, on_data in digit_data.items():
                    # Manually format the data to match the desired output
                    file.write(f"{idx} = [\n")

                    # Loop through all but the last element
                    for i, on in enumerate(on_data):
                        if i < len(on_data) - 1:
                            file.write(f"    {on},\n")  # Add a comma after each entry except the last
                        else:
                            file.write(f"    {on}\n")  # No comma after the last element

                    file.write("]\n\n")

        # Loop over each of the symbols
        for idx, c in enumerate(symbolCnts):  # 'idx' will give us the symbol index
            # Extract the symbol ROI
            (x, y, w, h) = cv2.boundingRect(c)
            roi = tr_opene[y:y + h, x:x + w]

            # Count the number of white pixels (255) in the ROI
            white_pixels = numpy.sum(roi == 255)

            # If the number of white pixels exceeds a threshold, consider it a valid symbol
            if white_pixels > 0.1 * roi.size:  # Adjust threshold as needed
                # print(f"Symbol_{idx + 1} at ({x}, {y}) is a valid symbol")
                # Store 1 for valid symbol, append to the list if it exists
                if f"symbol_{idx + 1}" in symbol_data:
                    symbol_data[f"symbol_{idx + 1}"].append(1)
                else:
                    symbol_data[f"symbol_{idx + 1}"] = [1]  # Initialize with 1 if not exists
            else:
                # print(f"Symbol_{idx + 1} at ({x}, {y}) is not valid (too few white pixels)")
                # Store 0 for invalid symbol, append to the list if it exists
                if f"symbol_{idx + 1}" in symbol_data:
                    symbol_data[f"symbol_{idx + 1}"].append(0)
                else:
                    symbol_data[f"symbol_{idx + 1}"] = [0]  # Initialize with 0 if not exists

            # Save the symbol data to a file
            with open('/home/raj/Desktop/cam/cam_opencv/symbol_data.py', 'w') as file:
                for idx, validity in symbol_data.items():
                    # Write the variable assignment and the list using repr()
                    file.write(f"{idx} = {validity}\n\n")

    try:
        from digit_data import data_1, data_2
    except:
        print("Error importing digit_data from the files.")
        spi.writebytes(error)  # Send error code if there is an issue with the data

    try:
        from symbol_data import symbol_1, symbol_2 # Adjust these imports based on the actual variables you need
    except:
        print("Error importing symbol_data from the files.")
        #spi.writebytes(error)  # Send error code if there is an issue with the data

    try:
        print("for data_set 1")
        # Loop through each bit position (from 0 to 6)
        for bit_position in range(7):  # We have 7 bits, so positions 0 to 6
            found_one = False
            # Check each data point to see if the bit at the current position is '1'
            for data_point in data_1:
                if data_point[bit_position] == 1:
                    found_one = True
                    break  # No need to check further if we find at least one '1'
                
            # Print the result for the current bit position
            #   if found_one:
            #       print(f"Bit position {bit_position} has at least one '1'.")
            #   else:
            #       print(f"Bit position {bit_position} has only '0' values.")

            # For bit position 3, we don't care about the result
            if bit_position == 3:
                print(f"Bit position {bit_position}: result ignored.")
                continue
        
            # For other positions, check the result and print accordingly
            if found_one:
                print(f"Bit position {bit_position} has at least one '1'.")
                spi.writebytes(ok)
            else:
                print(f"Error: Bit position {bit_position} does not have any '1' values.")
                spi.writebytes(error)  # Send error code if there is an issue with the data
    except:
        print("Error processing data_set 1.")
        spi.writebytes(error)  # Send error code if there is an issue with the data

    try:
        print("for data_set 2")
        # Loop through each bit position (from 0 to 6)
        for bit_position in range(7):  # We have 7 bits, so positions 0 to 6
            found_one = False
            # Check each data point to see if the bit at the current position is '1'
            for data_point in data_2:
                if data_point[bit_position] == 1:
                    found_one = True
                    break  # No need to check further if we find at least one '1'
                
            # Print the result for the current bit position
            #   if found_one:
            #       print(f"Bit position {bit_position} has at least one '1'.")
            #   else:
            #       print(f"Bit position {bit_position} has only '0' values.")

            # For bit position 3, we don't care about the result
            if bit_position == 3:
                print(f"Bit position {bit_position}: result ignored.")
                continue
        
            # For other positions, check the result and print accordingly
            if found_one:
                print(f"Bit position {bit_position} has at least one '1'.")
                spi.writebytes(ok)  # Send error code if there is an issue with the data
            else:
                print(f"Error: Bit position {bit_position} does not have any '1' values.")
                spi.writebytes(error)  # Send error code if there is an issue with the data
    except:
        print("Error processing data_set 2.")
        spi.writebytes(error)  # Send error code if there is an issue with the data

    # Check the symbol data
    try:
        print("Checking symbol data...")
        for idx in symbol_data.keys():  # We loop through the keys (symbol names)
            symbol = globals().get(idx)  # Access the variable by its name dynamically
            if 1 in symbol:
                print(f"{idx} contains at least one '1'.")
                spi.writebytes(ok)
    except:
        print("Error processing symbol data.")

    # Once processing is complete, clear the file contents
    with open('/home/raj/Desktop/cam/cam_opencv/digit_data.py', 'w') as file:
        file.write('')
    with open('/home/raj/Desktop/cam/cam_opencv/symbol_data.py', 'w') as file:
        file.write('')

    Led_2.off()
    
    # Stop the camera
    picam2.stop_preview()
    picam2.stop()
    cv2.destroyAllWindows()

# Bind the callback to the button's press event
button.when_pressed = on_button_pressed

print("Waiting for button press. Press Ctrl+C to exit.")
pause()  # Keeps the script running
