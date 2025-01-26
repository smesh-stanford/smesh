"""
Raspberry Pi 4/Zero Logging Script

Changes in v4:
- Added timeout on the file lock
- Try/except catches general exceptions (Exception)
- Watch dog timer (WDT) and recovery by unsubscribing and subscribing to pub
- Counting number of times heard from each node

Future Improvements:
- Use SQLite for logging data
- Add keyboard node logging

Authors: Lisa, Kirby, Rohan, Pete, Daniel
Previous Authors: Joshua
Last Updated: 12/29/2024
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

# Create new folder for each type of telemetry
LOG_FILE_PREFIX = ""
# Global variable for unique datetime identifier in log file name
# Creates new log file every time script is run and once every 1 hour
ON_RECEIVE_DT = datetime.now()

# Global variable for file lock to ensure thread safety
# in the file writing operations when multiple packets arrive
# at similar times.
FILE_LOCK = threading.Lock()

# Dictionary to keep track of the number of times a node has been heard
HEARD_FROM_NODE_COUNTER = {}

WDT = datetime.now()

def create_new_logging_dir(node_id):

    """
    Ensures that a directory is created prior to running any logging functions
    Parameters: 
    - node_id: the logger node ID
    """
    global LOG_FILE_PREFIX 
    # create new directory if the current one doesn't exist including the nodeid
    if not os.path.exists(LOG_FILE_PREFIX) or LOG_FILE_PREFIX == "":
        format_dt_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        LOG_FILE_PREFIX = f'./data-{format_dt_str}/{node_id}/'
        print(f'Created new logging directory {LOG_FILE_PREFIX}')
        # update the directory because either the block was corrupted for the provided directory OR
        # we have not yet defined and created the desired directory

        try:
            os.makedirs(LOG_FILE_PREFIX, exist_ok=False) # also creates any relevant parent directories
        except OSError as e:
            # fail LOUDLY! if we can no longer write data over :-)
            raise SystemError(f"Could not create directory path at '{LOG_FILE_PREFIX}'. Threw error {e}")


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
    print(f"Lock status of {FILE_LOCK}: {FILE_LOCK.locked()}")


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
    if FILE_LOCK.acquire(timeout=5):  # Timeout set to 5 seconds
        try:
            print(f"Current thread (with lock) at log_to_csv for {filename}: " +
                f"{threading.current_thread().name} at {threading.current_thread().ident}")
            print(f"Lock is: {FILE_LOCK} (locked: {FILE_LOCK.locked()})")
    
            # Write headers for new file
            if not os.path.exists(filename):
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)

            # Append data
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(data)
        finally:
                FILE_LOCK.release()
    else:
        print(f"ERROR: Could not acquire file lock for {filename} within timeout period.")

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
    if FILE_LOCK.acquire(timeout=5):  # Timeout set to 5 seconds
        try:
            print(f"Current thread (with lock) at log_to_txt for {filename}: " +
             f"{threading.current_thread().name} at {threading.current_thread().ident}")
            print(f"Lock is: {FILE_LOCK} (locked: {FILE_LOCK.locked()})")

            with open(filename, 'a') as file:
                file.write(f"{data}\n")
        finally:
            FILE_LOCK.release()
    else:
        print(f"ERROR: Could not acquire file lock for {filename} within timeout period.")


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

    expected_keys = expected_keys_dict[telemetry_key] + ['rxSnr', 'rxRssi', 'rxTime', 'hopStart', 'hopLimit']

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
    #Feed the watchdog timer
    global WDT
    WDT = datetime.now()

    # Datetime unique identifier for log filename
    global ON_RECEIVE_DT
    # Update datetime identifier (new file) once every 1 hour of logging
    if (datetime.now() >= ON_RECEIVE_DT + timedelta(hours=1)):
        ON_RECEIVE_DT = datetime.now()

    try:
        # nodeid is the last 4 hex digits of node connected via serial port
        # (i.e., the node that is logging)
        logger_node_id = hex(interface.myInfo.my_node_num)[-4:]
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
            # expected_telemetry = False  # True if expected sensor telemetry received, else False

            signal_keys = ['rxSnr', 'rxRssi', 'rxTime', 'hopLimit', 'hopStart']
            signal_strength_data = {key: packet[key] for key in signal_keys if key in packet}

            # Format datetime for filename
            # Format as 'YYYY-MM-DD_HH-MM-SS', such as '2024-12-17_13-07-56'
            format_dt_str = ON_RECEIVE_DT.strftime("%Y-%m-%d_%H-%M-%S")    

            # create new directories if necessary to log data
            create_new_logging_dir(logger_node_id)

            for telemetry_key in telemetry_list:
                if telemetry_key in telemetry_data:
                    print(f"Telemetry key: {telemetry_key}")

                    metrics = telemetry_data[telemetry_key]
                    print(f"Metrics: {metrics}")

                    log_telemetry_to_csv(f'{LOG_FILE_PREFIX}{telemetry_key}_{format_dt_str}.csv', str(datetime.now()), 
                                        from_node, metrics | signal_strength_data, telemetry_key)
                    
                    # expected_telemetry = True
                    break
                

            # Commented! Needs to be tested-- last issues documented at burnbot
            # if not expected_telemetry:
            #     print("Other packet")
            #     print(f"Telemetry data: {telemetry_data}")
            #     # Empty headers for other data, since we don't know what it is a priori
            #     other_headers = [''] * len(telemetry_data) 
            #     log_to_csv(f'{LOG_FILE_PREFIX}_other_{format_dt_str}.csv', 
            #                [str(datetime.now()), from_node, telemetry_data], other_headers, logger_node_id)

            # log telemetry data to txt file
            log_to_txt(f'{LOG_FILE_PREFIX}logs_{format_dt_str}.txt', 
                       [str(datetime.now()), from_node, packet])

            # Log the incremented counter dictionary to a text file
            log_to_txt(f'{LOG_FILE_PREFIX}heard_from_node_counter_{format_dt_str}.txt', 
                       [str(datetime.now()), HEARD_FROM_NODE_COUNTER])

    except KeyError:
        print("ERROR: KeyError")
        pass  # Ignore KeyError silently
    except UnicodeDecodeError:
        print("ERROR: UnicodeDecodeError")
        pass  # Ignore UnicodeDecodeError silently
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        pass  # Ignore unexpected errors silently

    print(f"\nReceived Packet: {packet}")
    print("-"*30, "\n")     # Separate packets more visibly


################################################
# Main Function
################################################

# Runs every time script is started
def main():
    global WDT
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
    try:
        pub.subscribe(on_receive, "meshtastic.receive")
        print("Subscribed to meshtastic.receive")
    except Exception as e:
        print(f"Unable to subscribe: {e}")

    # Print the current active threads
    print("----\nAfter subscribing to meshtastic.receive, the thread information is as follows:")
    print_active_threads()
    print("----")

    # Keep the script running to listen for messages
    try:
        while True:
            sys.stdout.flush()
            time.sleep(1)  # Sleep to reduce CPU usage (time in seconds)
            if (datetime.now() >= WDT + timedelta(minutes=1)):
                WDT = datetime.now()
                print(f"{WDT} - ERROR -- - ERROR -- - ERROR -- - ERROR --- ERROR -- - ERROR -- - ERROR -- - ERROR -- Watchdog Timer Reset")
                increment_heard_from_node_counter("WDT ERROR")
    # Unsubscribe from the topic if already subscribed
                try:
                    pub.unsubscribe(on_receive, "meshtastic.receive")
                    print("Unsubscribed from meshtastic.receive")
                except KeyError:
                    print("No existing subscription to meshtastic.receive")
                except Exception as e:
                    print(f"ERROR: Unexpected error: {e}")
                    pass  # Ignore unexpected errors silently

                # Subscribe to the topic
                pub.subscribe(on_receive, "meshtastic.receive")
                print("Subscribed to meshtastic.receive")
    
    except KeyboardInterrupt:
        print("Script terminated by user")
        local.close()
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        pass  # Ignore unexpected errors silently


if __name__ == "__main__":
    main()
