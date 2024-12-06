"""
Log Serial Data for Wind Sensor

Command: poetry run python scripts/serial_log.py
from snode directory
"""

import serial
import time
import os

# Configure serial port parameters
# CHANGE:
serial_port = '/dev/ttyUSB0'  # Change to your serial port
baud_rate = 115200  # Adjust according to your device's baud rate

# Open a file to log data
# CHANGE:
log_file = '/home/pi/smesh/snode/data/logfile_test1.txt'  # Specify your log file path

# Testing on Windows computer:
# serial_port = 'COM3'
# log_file = './data/logfile_test1.txt'

# Open the serial port
ser = serial.Serial(serial_port, baudrate=baud_rate, timeout=1)

# Check if the directory exists; if not, create it
log_dir = os.path.dirname(log_file)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)



with open(log_file, 'a') as file:
    print(f"Logging data from {serial_port} to {log_file}...")
    while True:
        try:
            # Read a line of data from the serial port
            # Ignore errors (UnicodeDecodeError: 'utf-8' codec can't decode byte 0x94 in position 0: invalid start byte)
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                # Write data to file with timestamp
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                file.write(f"{timestamp} - {data}\n")
                file.flush()  # Ensure data is written to file immediately
        except KeyboardInterrupt:
            print("Logging stopped.")
            break

# Close the serial port when done
ser.close()