"""
from picamzero import Camera
from time import sleep

cam = Camera()
cam.start_preview()
# Keep the preview window open for 5 seconds
sleep(50)
cam.stop_preview()

"""

from picamera2 import Picamera2, Preview
import time

picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
picam2.configure(video_config)

picam2.start(show_preview=True)

time.sleep(30)

picam2.stop_preview()
picam2.stop()