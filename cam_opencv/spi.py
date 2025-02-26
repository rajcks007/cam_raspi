from lib import spidev
import time

def spi_init():

    error = [0x24]  # Error code to send if there is an issue with the data ($)
    ok = [0x2A]  # OK code to send if the data is valid (*)

    # We only have SPI bus 0 available to us on the Pi
    bus = 0
    #Device is the chip select pin. Set to 0 or 1, depending on the connections
    device = 1

    # Enable SPI
    global spi
    spi = spidev.SpiDev()

    # Open a connection to a specific bus and device (chip select pin)
    spi.open(bus, device)
    spi.max_speed_hz = 18000000  # Set speed to 18 Mbit/s
    spi.mode = 0  # SPI Mode 0: (CPOL=0, CPHA=0) -> first edge sampling

    return error, ok

def send_message(msg):
    spi.writebytes(msg)