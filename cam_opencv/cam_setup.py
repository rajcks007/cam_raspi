from lib import *
from libcamera import controls

picam2 = Picamera2()

# start camera
picam2.start(show_preview=False)

# Define the desired video resolution (width, height)
video_resolution = (640, 480)  # 640x480 resolution

# Configure the camera with the desired resolution
config = picam2.create_video_configuration(main={"size": video_resolution})

# set focus of camera
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 30.0})