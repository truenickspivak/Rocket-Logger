# Rocket-Logger

Flight computer for a LOC IV-X2 flying Tripoli L1 and L2 at METRA, September 2026. Logs barometric altitude and six-axis motion to a microSD card at about 50 Hz.

Written in CircuitPython for the Adafruit Feather RP2040 Adalogger.

## Hardware

| Part | Interface | What it gives |
|---|---|---|
| Adafruit Feather RP2040 Adalogger | | RP2040, onboard microSD holder |
| BMP581 | I2C | Pressure, temperature, altitude |
| SPA06-003 | I2C | Second pressure and temperature channel |
| LSM6DSOX | I2C | 3-axis accelerometer, 3-axis gyro |
| microSD card | SPI | Storage, mounted at `/sd` |

Sensor ranges are set explicitly at startup rather than left at library defaults.

| Sensor | Range | Why |
|---|---|---|
| Accelerometer | `RANGE_16G` | Boost is about 9 g. A 2 g or 4 g default clips the burn flat while still writing rows |
| Gyro | `RANGE_2000_DPS` | The library default is 250 dps. Hand rotation on the bench hit 1,430 dps |

## Output

The firmware appends to `/sd/data.csv`. Two comment lines are written once per boot, both prefixed with `#` so they never break the twelve-field row format.

```
# RunStart accel=16G gyro=2000DPS
# Time, BMP_Temperature, BMP_Pressure, BMP_Altitude, SPA_Temperature, SPA_Pressure, Accel_X, Accel_Y, Accel_Z, Gyro_X, Gyro_Y, Gyro_Z
```

| Column | Unit |
|---|---|
| Time | s, from `time.monotonic_ns()` |
| BMP_Temperature | C |
| BMP_Pressure | hPa |
| BMP_Altitude | m, referenced to 1013.25 hPa |
| SPA_Temperature | C |
| SPA_Pressure | hPa |
| Accel_X, Accel_Y, Accel_Z | m/s^2 |
| Gyro_X, Gyro_Y, Gyro_Z | rad/s |

The `RunStart` marker exists because a code save is a soft reload. `time.monotonic()` keeps counting across it, so without a marker two firmware versions in one file look like one run.

The file is opened once and flushed every second rather than opened and closed per row.

## Status LED

There is no serial connection on the pad, so a board that has stopped logging looks the same as one that is working. The onboard LED carries the state.

| LED | Meaning |
|---|---|
| Slow pulse, about 1 s per state | Mounted, logging, flushes landing |
| Fast blink, 0.1 s | Card chain failed. Not seated, or unreadable |
| Dark | No power, or died before the mount |

The pulse is a toggle inside the flush block, so it only changes state if the loop is running and writes are still reaching the card. The card chain is wrapped from `SDCard()` through `mount()`, because construction is the call that throws on an unseated card.

## Measured performance

Bench and battery runs, not datasheet figures.

| Configuration | Rate |
|---|---|
| Prints on, `sleep(1)` | 1.1 s period. Period is work plus sleep |
| Prints off, 2-decimal formatting | 66.3 Hz |
| Prints off, full float precision | 53.3 Hz |
| Battery, stairwell run | 54.8 Hz |

Two-decimal timestamps quantise the time axis to 10 ms, which is coarser than the loop period. Timestamps are written at full precision for that reason.

## Ground test

Run on 2026-08-28, on battery, card pulled and read on a laptop afterward.

| | |
|---|---|
| Stationary | 250.06 m |
| Downstairs | 247.69 m |
| Back upstairs | 250.36 m |
| Return error | 0.28 m over 29.8 s |
| Noise floor | 0.278 m standard deviation while stationary |

A 2.4 m descent resolved as a ramp down, a flat bottom, and a ramp back up. `GROUND TEST DATA.csv` in this repo is that run.

## Running it

CircuitPython 10.2.1. Libraries are installed with `circup` and `lib/` is gitignored.

```
circup install adafruit_bmp5xx adafruit_spa06_003 adafruit_lsm6ds adafruit_sdcard
```

Copy `code.py` to the CIRCUITPY drive. Seat a FAT-formatted microSD card before power-up.
