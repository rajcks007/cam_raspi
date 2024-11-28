from picamera2 import Picamera2
from libcamera import controls
import time

picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
picam2.configure(video_config)

picam2.start(show_preview=True)

picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 50.0})                            # Manual Focus
#   picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})        # Auto Focus FAST
#   picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})                                              # Auto Focus


time.sleep(30)

picam2.stop_preview()
picam2.stop()