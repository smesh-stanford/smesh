# Connect Pi's ground to GND and DIR pins
# Connect Pi's 3.3 volts to VCC on AS5600
# Connect Pi's I2c SCL (pin 5) to AS5600 SCL pin
# Connect Pi's I2c SDA (pin 5) to AS5600 SDA pin

import pigpio
import time
import smbus
import csv
import pathlib
from datetime import datetime, timedelta

# =================== # Code to read AS5600 (Wind Vane) # ================= #
DEVICE_AS5600 = 0x36  # Default device I2C address
bus = smbus.SMBus(1)

def ReadRawAngle():  # Read angle (0-360 represented as 0-4096)
    read_bytes = bus.read_i2c_block_data(DEVICE_AS5600, 0x0C, 2)
    return (read_bytes[0] << 8) | read_bytes[1]

def ReadMagnitude():  # Read magnetism magnitude
    read_bytes = bus.read_i2c_block_data(DEVICE_AS5600, 0x1B, 2)
    return (read_bytes[0] << 8) | read_bytes[1]

# =================== # Code to read SS451A (Anemometer) # =============== #

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("pi not connected :(")

HALL_SENSOR_PIN = 16  # Define GPIO pin where sensor is connected

# Set GPIO mode
pi.set_mode(HALL_SENSOR_PIN, pigpio.INPUT)

# Set up the pin as input with pull-up resistor
pi.set_pull_up_down(HALL_SENSOR_PIN, pigpio.PUD_UP)

# Variables to keep track of how much rotations
anemometer_count = 0
curr_mag_state = pi.read(HALL_SENSOR_PIN) 
start_time = datetime.now()

# Call back function for each wind sensor reading
def cb(gpio, level, tick):
    global anemometer_count
    #if level == pigpio.RISING:
    anemometer_count += 1

# Register the call back for pin interrupts
pi.callback(HALL_SENSOR_PIN, pigpio.RISING_EDGE, cb)

def calc_wind_speed(anemometer_count, dt_seconds):
    # Wind speed calibration
    CAL_Factor = 2.64  # (3.14/1.19)
    SENSOR_NUM = 2
    R = 0.079
    SCALE = CAL_Factor * (2 * 3.14156 * R) / (SENSOR_NUM)  # wind speed in m/s

    return anemometer_count * SCALE / dt_seconds

# ====================================================================== #
data_folder = pathlib.Path("../../wind_data")
data_folder.mkdir(parents=True, exist_ok=True)
anemometer_filename = data_folder / pathlib.Path("anemometer.csv")
wind_vane_filename = data_folder / pathlib.Path("wind_vane.csv")
print("Anemometer file path: ")
print(anemometer_filename)
print("Wind vane file path: ")
print(wind_vane_filename)

def write_data(filename, data_row):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data_row)

# ====================================================================== #

start_time = datetime.now()

try:
    print("Reading sensors")
    while True:
        curr_time = datetime.now()
        dt = curr_time - start_time

        # Wind vane
        if dt > timedelta(seconds=20):
            raw_angle = ReadRawAngle()
            magnitude = ReadMagnitude()
            deg = raw_angle * 360.0 / 4096
            print("Raw angle: %4d" % (raw_angle), "m=%4d" % (magnitude), "%6.2f deg  " % (deg))
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            write_data(wind_vane_filename, [timestamp, raw_angle, magnitude, deg])

        # Anemometer
        if dt > timedelta(seconds=20):
            dt_seconds = dt.total_seconds()
            wind_speed = calc_wind_speed(anemometer_count, dt_seconds)
            write_data(anemometer_filename, [timestamp, wind_speed, anemometer_count, dt_seconds])
            print(f"in {dt_seconds} seconds, {anemometer_count} count, {wind_speed} m/s")
            # resetting
            anemometer_count = 0
            start_time = datetime.now()
            
        else:
            new_mag_state = pi.read(HALL_SENSOR_PIN)
            if (new_mag_state == 0):
                print("Magnet detected")
                if (new_mag_state != curr_mag_state):
                    print("Magnet edge falling")
            curr_mag_state = new_mag_state

        time.sleep(20)  # one measurement every 0.1 seconds

except KeyboardInterrupt:
    print("Exiting...")

finally:
    pi.stop()
