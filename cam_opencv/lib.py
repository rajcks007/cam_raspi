import os
import cv2
from libcamera import *
from picamera2 import * 
import numpy
import imutils
from imutils.perspective import four_point_transform
from imutils import contours
import time
import keyboard
from gpiozero import *
from signal import pause
import spidev
import sys
import importlib