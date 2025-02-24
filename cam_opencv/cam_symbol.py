from lib import *
from cam_setup import *

def symbol_fn(tr_opene, symbolCnts):

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