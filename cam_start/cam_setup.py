from picamera2 import * 
import time
from libcamera import controls
import cv2

# Initialize the camera
picam2 = Picamera2()

# Define the desired video resolution (width, height)
video_resolution = (640, 480)  # 640x480 resolution

# Configure the camera with the desired resolution
config = picam2.create_video_configuration(main={"size": video_resolution})

# Apply the configuration to the camera
picam2.configure(config)

# Start the camera (without preview window)
picam2.start(show_preview=False)

# Set focus of camera (manual focus)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 40.0})

# Set additional controls: contrast, brightness, exposure
picam2.set_controls({
    "Contrast": 0.9,       # Contrast range: -1.0 to 1.0
    "Brightness": 0.1,     # Brightness range: -1.0 to 1.0
})

while 1:

    image = picam2.capture_array()

    cv2.waitKey (100)

    cv2.imshow ('pi',image)

    cv2.waitKey (100)