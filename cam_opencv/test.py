import cv2
from picamera2 import *
from picamera2 import Picamera2 
from libcamera import controls
import numpy
import imutils
import time
import keyboard

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

start_time = time.time()  # Record the start time

# Dictionary to store data dynamically for each detected digit (based on idx)
digit_data = {}
# Define a dictionary to store the symbol data
symbol_data = {}

while(1):

    elapsed_time = time.time() - start_time  # Calculate the elapsed time
    if elapsed_time > 1000:  # If n seconds have passed
        break  # Exit the loop

    #cv2.waitKey(50)

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
        if (w >= 20 and w <= 160) and (h >= 190 and h <= 250):
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
        with open('digit_data.py', 'w') as file:
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
        with open('symbol_data.py', 'w') as file:
            for idx, validity in symbol_data.items():
                # Write the variable assignment and the list using repr()
                file.write(f"{idx} = {validity}\n\n")
    
    # # If the 'Esc' key is pressed, close the window
    # if keyboard.is_pressed('esc'):  # ASCII value of 'Esc' is 27
    #     break

from digit_data import *
from symbol_data import *

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
    if found_one:
        print(f"Bit position {bit_position} has at least one '1'.")
    else:
        print(f"Bit position {bit_position} has only '0' values.")

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
    if found_one:
        print(f"Bit position {bit_position} has at least one '1'.")
    else:
        print(f"Bit position {bit_position} has only '0' values.")

for idx in symbol_data.keys():  # We loop through the keys (symbol names)
    symbol = globals().get(idx)  # Access the variable by its name dynamically
    if 1 in symbol:
            print(f"{idx} contains at least one '1'.")



picam2.stop_preview()
picam2.stop()
cv2.destroyAllWindows()