import spidev
import time

global spi

def spi_init():
    # We only have SPI bus 0 available to us on the Pi
    bus = 0
    #Device is the chip select pin. Set to 0 or 1, depending on the connections
    device = 1

    # Enable SPI
    spi = spidev.SpiDev()

    # Open a connection to a specific bus and device (chip select pin)
    spi.open(bus, device)
    spi.max_speed_hz = 18000000  # Set speed to 18 Mbit/s
    spi.mode = 0  # SPI Mode 0: (CPOL=0, CPHA=0) -> first edge sampling
    return spi

def send_message(msg):
    spi.writebytes(msg)

"""
while True:

    spi.writebytes(msg)
    #y = spi.readbytes(1)
    #print("Value tranferred by SPI is", y[0])

    time.sleep(0.1)
"""