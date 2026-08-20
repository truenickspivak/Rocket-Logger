import board
import digitalio

import time

from adafruit_bmp5xx import BMP5XX
from adafruit_spa06_003 import SPA06_003
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX


SEALEVELPRESSURE_HPA = 1013.25

i2c = board.I2C()  # uses board.SCL and board.SDA
bmp = BMP5XX.over_i2c(i2c)
spa = SPA06_003.over_i2c(i2c)
accel = LSM6DSOX(i2c)



bmp.sea_level_pressure = SEALEVELPRESSURE_HPA

while True:
    currentTime = time.monotonic_ns()
    if bmp.data_ready:
        print("BMP: "
            f"Elapsed time: {currentTime / 1000000000: .1f} s, \n"
            f"Temperature: {bmp.temperature:.2f} C, \n"
            f"Pressure: {bmp.pressure:.2f} hPa, \n"
            f"Altitude: {bmp.altitude:.2f} m \n"
        )
    if spa.temperature_data_ready and spa.pressure_data_ready:
        print("SPA: ")
        print(f"Temperature: {spa.temperature} °C")
        print(f"Pressure: {spa.pressure}  hPa\n")
        print(f"Altitude: {spa.altitude} m")

    accel_x, accel_y, accel_z = accel.acceleration
    gyro_x, gyro_y, gyro_z = accel.gyro
    print("LSM6DSOX: ")
    print(f"Acceleration (m/s^2): {accel_x: .2f}, {accel_y: .2f}, {accel_z: .2f}")
    print(f"Gyro (rad/s): {gyro_x: .2f}, {gyro_y: .2f}, {gyro_z: .2}")
    time.sleep(1)

    