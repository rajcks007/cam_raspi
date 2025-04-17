from lib import *
from libcamera import controls


def cam_init(picam2):

    # start camera
    picam2.start(show_preview=False)

    # set focus of camera
    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 80.0})

    # Set controls
    picam2.set_controls({
        "Contrast"  : 0.9,      # Contrast range: -1.0 to 1.0
        "Brightness": -0.1,     # Brightness range: -1.0 to 1.0
        "Saturation": -2.0      # Adjust saturation
    })

    return picam2

def cropped(cropped_image):

    # Define the cropping parameters (e.g., crop 50 pixels from each side)
    left_crop   = 100         # Number of pixels to crop from the left
    right_crop  = 90       # Number of pixels to crop from the right
    top_crop    = 30         # Number of pixels to crop from the top
    bottom_crop = 1        # Number of pixels to crop from the bottom

    # Crop the image from all sides (left, right, top, and bottom)
    image = cropped_image[top_crop:-bottom_crop, left_crop:-right_crop] if right_crop > 0 and bottom_crop > 0 else \
            cropped_image[top_crop:, left_crop:-right_crop] if bottom_crop > 0 else \
            cropped_image[top_crop:-bottom_crop, left_crop:] if right_crop > 0 else \
            cropped_image[top_crop:, left_crop:]  # Fallback case where no cropping is done on one or more sides
    
    # Return the image with rectangles on it
    return image

# Dictionary to store data dynamically for each detected digit (based on idx)
digit_data = {}
# Define a dictionary to store the symbol data
symbol_data = {}

def cam_deinit(picam2):
    picam2.stop_preview()
    picam2.stop()