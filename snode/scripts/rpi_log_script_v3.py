"""
Updated Raspberry Pi 4 Logging Script

Changes post-Henry Coe Deployment:
- Start new log file (with datetime appended) every time and every 1 hour this script is run.
-- Purpose: 1) Detect RPi 4 crashes, 2) Prevent wearing out directory when writing to disk

New changes in v2:
- Error with `git pull` when file names have colons, so replaced underscores. So ':' becomes '_'
- Added headers in CSV data
- Print out (stdout) both from and fromId from packets (should be same)

Issues to address in v3:
- Place all data and log files into separate folders for better readibility
- Handle LARK Wind data

Authors: Lisa, Kirby, Rohan, Pete, Daniel
Previous Authors: Joshua
Last Updated: 12/17/2024
"""

import time
import sys
import os
import csv
import threading
from datetime import datetime, timedelta
from pubsub import pub
from meshtastic.serial_interface import SerialInterface
# from meshtastic import portnums_pb2

# Global variable for unique datetime identifier in log file name
# Creates new log file every time script is run and once every 1 hour
ON_RECEIVE_DT = datetime.now()

# Global variable for file lock to ensure thread safety
# in the file writing operations when multiple packets arrive
# at similar times.
FILE_LOCK = threading.Lock()

################################################
# Logging Functions
################################################

def log_to_csv(filename, data, headers):
    # global FILE_LOCK
    with FILE_LOCK:
        # Write headers for new file
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
        
        # Append data
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)


def log_to_txt(filename, data):
    """
    Writes logs to txt file.
    Closes file after each write, which writes to disk.
    """
    # global FILE_LOCK
    with FILE_LOCK:
        with open(filename, 'a') as file:
            file.write(f"{data}\n")


def log_telemetry_to_csv(filename, curr_date_time, from_node, data_dict, telemetry_key):
    """
    Use a set of expected preset telemetry data to log to csv file while accounting for missing data.

    Parameters:
    - filename: str, path to the csv file
    - curr_date_time: str, current date and time
    - from_node: str, node id
    - data_dict: Dict, dictionary of data keys and values
    - telemetry_key, str, telemetry type

    Private variables:
    - data_to_log: list, data to log
    """

    expected_keys_dict = {
        'environmentMetrics' : ['temperature', 'relativeHumidity', 'barometricPressure', 'gasResistance', 'iaq', 'windDirection', 'windSpeed'],
        'airQualityMetrics' : ['pm10Standard', 'pm25Standard', 'pm100Standard', 'pm10Environmental', 'pm25Environmental', 'pm100Environmental'],
        'powerMetrics' : ['ch3Voltage', 'ch3Current'],
        'deviceMetrics' : ['batteryLevel', 'voltage', 'channelUtilization', 'airUtilTx']
    }

    expected_keys = expected_keys_dict[telemetry_key] + ['rxSnr', 'rxRssi', 'hopStart', 'hopLimit']

    data_to_log = [curr_date_time, from_node]
    for key in expected_keys:
        if key in data_dict:
            data_to_log.append(data_dict[key])
        else:
            data_to_log.append(None)

    headers = ['datetime', 'fromNode'] + expected_keys
    log_to_csv(filename, data_to_log, headers)


################################################
# Callback Functions
################################################

def on_receive(packet, interface):
    """
    Callback reads BME688 and PMSA003I data packets over the e.g. serial interface.
    """
    # Datetime unique identifier for log filename
    global ON_RECEIVE_DT
    # Update datetime identifier (new file) once every 1 hour of logging
    if (datetime.now() >= ON_RECEIVE_DT + timedelta(hours=1)):
        ON_RECEIVE_DT = datetime.now()

    # print("All reachable nodes:", interface.nodes.keys())

    # nodeid is the last 4 hex digits of node connected via serial port
    nodeid = hex(interface.myInfo.my_node_num)[-4:]

    # TODO: create new folder for each type of telemetry
    log_file_prefix = f'./data/{nodeid}'

    try:
        from_node = hex(packet['from'])
        print("\nFrom node:", from_node)
        
        if packet['decoded']['portnum'] == 'TELEMETRY_APP':
            telemetry_data = packet['decoded']['telemetry']
            print(f"[{str(datetime.now())}] Packet from {from_node} (fromId: {packet['fromId']})")

            # Note any situation where the from_node and fromId are different
            if from_node != packet['fromId']:
                print(f"WARNING: from_node and fromId are different: {from_node} != {packet['fromId']}")

            # Expected telemetry
            telemetry_list = ['environmentMetrics', 'airQualityMetrics', 'powerMetrics', 'deviceMetrics']
            expected_telemetry = False  # True if expected sensor telemetry received, else False

            signal_strength_data = {key: packet[key] for key in ['rxSnr', 'rxRssi', 'hopLimit', 'hopStart'] if key in packet}

            # Format as 'YYYY-MM-DD_HH-MM-SS', such as '2024-12-17_13-07-56'
            format_dt_str = ON_RECEIVE_DT.strftime("%Y-%m-%d_%H-%M-%S")    # Format datetime for filename

            for telemetry_key in telemetry_list:
                if telemetry_key in telemetry_data:
                    print(f"Telemetry key: {telemetry_key}")

                    metrics = telemetry_data[telemetry_key]
                    print(f"Metrics: {metrics}")

                    log_telemetry_to_csv(f'{log_file_prefix}_{telemetry_key}_{format_dt_str}.csv', str(datetime.now()), 
                                        from_node, metrics | signal_strength_data, telemetry_key)
                    
                    expected_telemetry = True
                    break
                
            if not expected_telemetry:
                print("Other packet")
                print(f"Telemetry data: {telemetry_data}")
                other_headers = [''] * len(telemetry_data)
                log_to_csv(f'{log_file_prefix}_other_{format_dt_str}.csv', [str(datetime.now()), from_node, telemetry_data], other_headers)

            # log telemetry data to txt file
            log_to_txt(f'{log_file_prefix}_logs_{format_dt_str}.txt', [str(datetime.now()), from_node, packet])

    except KeyError:
        print("ERROR: KeyError")
        pass  # Ignore KeyError silently
    except UnicodeDecodeError:
        print("ERROR: UnicodeDecodeError")
        pass  # Ignore UnicodeDecodeError silently

    print(f"\nReceived Packet: {packet}")
    print("-"*30, "\n")     # Separate packets more visibly


################################################
# Main Function
################################################

# Runs every time script is started
def main():
    ON_RECEIVE_DT = datetime.now()
    print(f"{ON_RECEIVE_DT} Raspberry Pi Logging Script started")

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
            time.sleep(1)  # Sleep to reduce CPU usage (time in seconds)
    except KeyboardInterrupt:
        print("Script terminated by user")
        local.close()


if __name__ == "__main__":
    main()
