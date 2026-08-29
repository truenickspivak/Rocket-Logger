import board
import busio
import adafruit_sdcard
import digitalio
import storage

import time

from adafruit_bmp5xx import BMP5XX
from adafruit_spa06_003 import SPA06_003
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from adafruit_lsm6ds import AccelRange, GyroRange

SEALEVELPRESSURE_HPA = 1013.25

i2c = board.I2C()  # uses board.SCL and board.SDA
bmp = BMP5XX.over_i2c(i2c)
spa = SPA06_003.over_i2c(i2c)
accel = LSM6DSOX(i2c)

accel.accelerometer_range = AccelRange.RANGE_16G
accel.gyro_range = GyroRange.RANGE_2000_DPS

bmp.sea_level_pressure = SEALEVELPRESSURE_HPA

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
cs = digitalio.DigitalInOut(board.SD_CS)

try:
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
except OSError as e:
    while True:
        led.value = True  # Turn on the LED to indicate an error
        time.sleep(.1)  # Keep the LED on for a moment to indicate the error
        led.value = False  # Turn off the LED after a brief moment
        time.sleep(.1)

last_flush = None
with open("/sd/data.csv", "a") as f:

    f.write("# RunStart accel=16G gyro=2000DPS\n")
    f.write("# Time, BMP_Temperature, BMP_Pressure, BMP_Altitude, SPA_Temperature, SPA_Pressure, Accel_X, Accel_Y, Accel_Z, Gyro_X, Gyro_Y, Gyro_Z\n")

    while True:
        currentTime = time.monotonic_ns() /1e9  # Convert to seconds
        BMP_temp = bmp.temperature
        BMP_pressure = bmp.pressure
        BMP_altitude = bmp.altitude
        SPA_temp = spa.temperature
        SPA_pressure = spa.pressure
        
        accel_x, accel_y, accel_z = accel.acceleration
        gyro_x, gyro_y, gyro_z = accel.gyro

        f.write(f"{currentTime}, {BMP_temp}, {BMP_pressure}, {BMP_altitude}, {SPA_temp}, {SPA_pressure}, {accel_x}, {accel_y}, {accel_z}, {gyro_x}, {gyro_y}, {gyro_z}\n")

        if last_flush is None or (time.monotonic() - last_flush) > 1:  # Flush every second
            f.flush()
            led.value = not led.value  # Toggle LED to indicate flush
            last_flush = time.monotonic()