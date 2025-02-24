from lib import *
from cam_colour import *
    
def rectengle_fn(tr_opene, image):

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
        elif (w >= 25 and w <= 100) and (h >= 25 and h <= 80):
            symbolCnts.append(c)
            # Draw the bounding box around each symbol in blue
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red for symbols   

    # Return the processed image and the thresholded image
    return image, digitCnts, symbolCnts

