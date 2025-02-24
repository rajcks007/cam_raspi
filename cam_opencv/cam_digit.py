from lib import *
from cam_setup import *

# define the dictionary of digit segments so we can identify each digit on the Display
DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1): 0,
	(0, 0, 1, 0, 0, 1, 0): 1,
	(1, 0, 1, 1, 1, 0, 1): 2,
	(1, 0, 1, 1, 0, 1, 1): 3,
	(0, 1, 1, 1, 0, 1, 0): 4,
	(1, 1, 0, 1, 0, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(1, 1, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9
}

def digit_fn(tr_opene, digitCnts):

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