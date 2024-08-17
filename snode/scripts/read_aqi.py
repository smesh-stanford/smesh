import time
import sys
import os
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from pubsub import pub
from meshtastic.serial_interface import SerialInterface
from meshtastic import portnums_pb2

def log_to_csv(filename, data):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def on_receive(packet, interface):
    """
    Callback reads BME688 and PMSA003I data packets over the e.g. serial interface.
    """
    try:
        if packet['decoded']['portnum'] == 'TELEMETRY_APP':
            telemetry_data = packet['decoded']['telemetry']
            if 'environmentMetrics' in telemetry_data:
                print("\nBME688 " + str(datetime.now()))
                metrics = telemetry_data['environmentMetrics']
                if metrics:
                    row = [str(datetime.now()), metrics['temperature'], metrics['relativeHumidity'], metrics['barometricPressure'], metrics['gasResistance'], metrics['iaq']]
                    print(row)
                else:
                    print("all 0s")
            if 'airQualityMetrics' in telemetry_data:
                print("\nPMSA003I " + str(datetime.now()))
                metrics = telemetry_data['airQualityMetrics']
                if metrics:
                    row = [str(datetime.now()), metrics['pm10Standard'], metrics['pm25Standard'], metrics['pm100Standard'], metrics['pm10Environmental'], metrics['pm25Environmental'], metrics['pm100Environmental']]
                    print(row)
                    
    except KeyError:
        pass  # Ignore KeyError silently
    except UnicodeDecodeError:
        pass  # Ignore UnicodeDecodeError silently

if __name__ == "__main__":
    # Choose the serial port to listen to
    if len(sys.argv) < 2:
        print("Error: No serial port path provided.")
        exit()

    serial_port = sys.argv[1]

    if os.path.exists(serial_port):
        print(f"Serial port set to: {serial_port}")
    else:
        print(f"Error: The path '{serial_port}' does not exist.")

    local = SerialInterface(serial_port)
    print("SerialInterface setup for listening.")

    # Subscribe to the data topic
    pub.subscribe(on_receive, "meshtastic.receive")
    print("Subscribed to meshtastic.receive")

    # Keep the script running to listen for messages
    try:
        while True:
            sys.stdout.flush()
            time.sleep(1)  # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        print("Script terminated by user")
        local.close()