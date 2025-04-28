import RPi.GPIO as GPIO
import time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Define GPIO pin where sensor is connected
HALL_SENSOR_PIN = 16

# Set up the pin as input with pull-up resistor (if external not used, this helps)
GPIO.setup(HALL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("Monitoring Hall sensor. Press Ctrl+C to exit.")
    while True:
        if GPIO.input(HALL_SENSOR_PIN) == GPIO.LOW:
            print("Magnet detected!")
        else:
            print("No magnet.")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()

