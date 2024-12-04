from lib import *
from cam_setup import *
from cam_colour import *

# define the dictionary of digit segments so we can identify
# each digit on the thermostat
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

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 9))
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
        if (w >= 30 and w <= 150) and (h >= 100 and h <= 230):
            digitCnts.append(c)
            # Draw the bounding box around each digit in green
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) 
        
        # If the contour is within the symbol size range (symbols might be smaller or larger than digits)
        elif (w >= 15 and w <= 100) and (h >= 50 and h <= 70):
            symbolCnts.append(c)
            # Draw the bounding box around each symbol in blue
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue for symbols

    # Return the processed image and the thresholded image
    return image, tr_opene


