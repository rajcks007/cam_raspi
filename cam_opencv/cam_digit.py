from lib import *
from cam_setup import *
from cam_colour import *

# define the dictionary of digit segments so we can identify each digit on the Display
DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1): 0,
	(0, 0, 1, 0, 0, 1, 0): 1,
	(1, 0, 1, 1, 1, 0, 1): 2,
	(1, 0, 1, 1, 0, 1, 1): 3,
	(0, 1, 1, 1, 0, 1, 0): 4,
	(1, 1, 0, 1, 0, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(1, 0, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9
}
    
def digit_fn(gray, image):
    
    # Threshold the warped image, then apply a series of morphological operations to clean up the thresholded image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 7))
    tr_opene = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours in the thresholded image, then initialize the digit contours lists
    cnts = cv2.findContours(tr_opene.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    digitCnts = []
    symbolCnts = []

    # Loop over the digit area candidates
    for c in cnts:
        # Compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)

        # If the contour is sufficiently large, it must be a digit
        if (w >= 20 and w <= 150) and (h >= 100 and h <= 230):
            digitCnts.append(c)
            # Draw the bounding box around each digit in green
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) # Green for digit
        
        # If the contour is within the symbol size range (symbols might be smaller or larger than digits)
        elif (w >= 15 and w <= 100) and (h >= 50 and h <= 70):
            symbolCnts.append(c)
            # Draw the bounding box around each symbol in blue
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue for symbols
    
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
        print(f"Digit_{idx + 1} at ({x}, {y}): {on}")   

    # Return the processed image and the thresholded image
    return image, tr_opene


