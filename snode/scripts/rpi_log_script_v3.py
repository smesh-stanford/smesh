"""
Updated Raspberry Pi 4 Logging Script

Changes post-Henry Coe Deployment:
- Start new log file (with datetime appended) every time and every 1 hour this script is run.
-- Purpose: 1) Detect RPi 4 crashes, 2) Prevent wearing out directory when writing to disk

New changes in v3:
- Filename convension
- Added headers in CSV data
- Handle LARK wind data (when available)
- Safe threading for file writing operations
- Heard from node counter

Issues to address in v4:
- Place all data and log files into separate folders for better readibility

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

# Dictionary to keep track of the number of times a node has been heard
HEARD_FROM_NODE_COUNTER = {}

################################################
# Printing Helper Functions
################################################

def print_active_threads():
    """
    Prints all active threads.
    """
    print(f"[{datetime.now()}] Main thread (should be the main python script):")
    print(f"Main thread name: {threading.main_thread().name}, " + 
          f"Main thread ID: {threading.main_thread().ident}, " + 
          f"Is daemon: {threading.main_thread().daemon}")
    print(f"[{datetime.now()}] There are {threading.active_count()} active threads:")
    for thread in threading.enumerate():
        print(f"Thread name: {thread.name}, Thread ID: {thread.ident}, Is daemon: {thread.daemon}")
    print("Of which, current thread is:")
    print(f"Current thread name: {threading.current_thread().name}, " +
          f"Current thread ID: {threading.current_thread().ident}, " +
          f"Is daemon: {threading.current_thread().daemon}")


################################################
# Logging Functions
################################################

def log_to_csv(filename, data, headers):
    """
    Writes logs to csv file. Closes file after each write, which writes to disk.
    The file lock ensures thread safety when multiple packets arrive at similar 
    times.

    If the file does not exist, it creates a new file and writes the headers.
    Technically, headers can be None thereafter.

    Parameters:
    - filename: str, path to the csv file
    - data: list, data to log
    - headers: list, headers for the csv file
    """
    print_active_threads()
    print("----")

    # global FILE_LOCK
    with FILE_LOCK:
        print(f"Current thread (with lock) at log_to_csv for {filename}: " + 
              f"{threading.current_thread().name} at {threading.current_thread().ident}")
        print(f"Lock is: {FILE_LOCK}")
    
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
    Writes logs to txt file. Closes file after each write, which writes to disk.
    The file lock ensures thread safety when multiple packets arrive at similar
    times.

    Parameters:
    - filename: str, path to the txt file
    - data: list, data to log
    """
    # global FILE_LOCK
    with FILE_LOCK:
        print(f"Current thread (with lock) at log_to_txt for {filename}: " + 
             f"{threading.current_thread().name} at {threading.current_thread().ident}")
        print(f"Lock is: {FILE_LOCK}")
        
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
# Counter Functions
################################################

def increment_heard_from_node_counter(from_node):
    """
    Increment the counter for the number of times a node has been heard.
    """
    global HEARD_FROM_NODE_COUNTER
    if from_node in HEARD_FROM_NODE_COUNTER:
        HEARD_FROM_NODE_COUNTER[from_node] += 1
    else:
        HEARD_FROM_NODE_COUNTER[from_node] = 1

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

    # nodeid is the last 4 hex digits of node connected via serial port
    # (i.e., the node that is logging)
    nodeid = hex(interface.myInfo.my_node_num)[-4:]

    # TODO: create new folder for each type of telemetry
    log_file_prefix = f'./data/{nodeid}'

    try:
        from_node = hex(packet['from'])
        print("\nFrom node:", from_node)

        # Note any situation where the from_node and fromId are different
        # Note that from is printed as 0x12345678, while fromId is printed 
        # as !12345678. So, we only need the last 8 characters.
        # Note also that the id is in decimal, not hex.
        check_from_node = str(from_node)[-8:]
        check_fromid_node = str(packet['fromId'])[-8:]
        if check_from_node != check_fromid_node:
            print("WARNING: from_node and fromId are different:" + \
                    f"{check_from_node} != {check_fromid_node}")
        
        # Increment the counter for the number of times a node has been heard
        increment_heard_from_node_counter(from_node)                   
        
        if packet['decoded']['portnum'] == 'TELEMETRY_APP':
            telemetry_data = packet['decoded']['telemetry']
            print(f"[{str(datetime.now())}] Packet from {from_node} (fromId: {packet['fromId']})")

            # Expected telemetry
            telemetry_list = ['environmentMetrics', 'airQualityMetrics', 'powerMetrics', 'deviceMetrics']
            expected_telemetry = False  # True if expected sensor telemetry received, else False

            signal_keys = ['rxSnr', 'rxRssi', 'rxTime', 'hopLimit', 'hopStart']
            signal_strength_data = {key: packet[key] for key in signal_keys if key in packet}

            # Format datetime for filename
            # Format as 'YYYY-MM-DD_HH-MM-SS', such as '2024-12-17_13-07-56'
            format_dt_str = ON_RECEIVE_DT.strftime("%Y-%m-%d_%H-%M-%S")    

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
                # Empty headers for other data, since we don't know what it is a priori
                other_headers = [''] * len(telemetry_data) 
                log_to_csv(f'{log_file_prefix}_other_{format_dt_str}.csv', 
                           [str(datetime.now()), from_node, telemetry_data], other_headers)

            # log telemetry data to txt file
            log_to_txt(f'{log_file_prefix}_logs_{format_dt_str}.txt', 
                       [str(datetime.now()), from_node, packet])

            # Log the incremented counter dictionary to a text file
            log_to_txt(f'{log_file_prefix}_heard_from_node_counter_{format_dt_str}.txt', 
                       [str(datetime.now()), HEARD_FROM_NODE_COUNTER])

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

    # Print the current active threads before starting
    print("----\nBefore starting the script, the thread information is as follows:")
    print_active_threads()
    print("----")

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

    # Print the current active threads
    print("----\nAfter subscribing to meshtastic.receive, the thread information is as follows:")
    print_active_threads()
    print("----")

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
