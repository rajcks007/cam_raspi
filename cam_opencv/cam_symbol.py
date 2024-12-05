from lib import *
from cam_colour import *

def symbol_fn(tr_opene, symbolCnts):

    # Loop over each of the symbols
    for idx, c in enumerate(symbolCnts):  # 'idx' will give us the symbol index
        # Extract the symbol ROI
        (x, y, w, h) = cv2.boundingRect(c)
        roi = tr_opene[y:y + h, x:x + w]

        # Count the number of white pixels (255) in the ROI
        white_pixels = numpy.sum(roi == 255)

        # If the number of white pixels exceeds a threshold, consider it a valid symbol
        if white_pixels > 0.2 * roi.size:  # Adjust threshold as needed
            print(f"Symbol_{idx + 1} at ({x}, {y}) is a valid symbol")
        else:
            print(f"Symbol_{idx + 1} at ({x}, {y}) is not valid (too few white pixels)")