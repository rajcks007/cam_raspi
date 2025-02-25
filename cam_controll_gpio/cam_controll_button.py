from picamera2 import Picamera2, Preview
import time
from datetime import datetime
from gpiozero import Button
import RPi.GPIO as GPIO
from signal import pause

picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
picam2.configure(camera_config)


# Configure the button on GPIO pin 17
button = Button(17, pull_up=False, bounce_time=0.2)

# Callback function when the button is pressed
def on_button_pressed():
    picam2.start_preview(Preview.QTGL)
    timestamp = datetime.now().isoformat()
    picam2.start()
    time.sleep(2)
    picam2.stop_preview()
    picam2.stop()
    print("button pressed")

# Bind the callback to the button's press event
button.when_pressed = on_button_pressed

print("Waiting for button press. Press Ctrl+C to exit.")
pause()  # Keeps the script running

