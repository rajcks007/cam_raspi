from lib import *
from cam_setup import *
from cam_colour import *

while(1):
     
    cv2.waitKey(50)

    # capture the array in BGR
    cropped_image = picam2.capture_array()

    # Crop the image from the sides
    image = cropped(cropped_image)                                                                                 

    gray = colour_fn(image)                 # call function

    # threshold the warped image, then apply a series of morphological operations to cleanup the thresholded image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 1)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
    tr_opene = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    cv2.imshow('thresh_img', tr_opene)

    # find contours in the thresholded image, then initialize the digit contours lists
    cnts = cv2.findContours(tr_opene.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    digitCnts = []
	
    # loop over the digit area candidates
    for c in cnts:
        # compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)

        # Draw the bounding box around each digit
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle with thickness 2

        # if the contour is sufficiently large, it must be a digit
        if w >= 15 and (h >= 30 and h <= 40):
            digitCnts.append(c)

    # Show the image with the bounding boxes drawn
    cv2.imshow("Detected Digits", image)

    
cv2.waitKey(0)

cv2.destroyAllWindows()
 
picam2.stop_preview()
picam2.stop()
