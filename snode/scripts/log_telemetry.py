"""
Updated Script for Logging Telemetry (from read_aqi.py)

Authors: Lisa Fung, Daniel Neamati, Joshua Dong
Last Updated: 11/07/2024
"""

import time
import sys
import os
import csv
from datetime import datetime
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from matplotlib.animation import FuncAnimation
from pubsub import pub
from meshtastic.serial_interface import SerialInterface
# from meshtastic import portnums_pb2

"""
Log data by Meshtastic node ID (MAC Address) and Sensor Type

For each telemetry reading:
    Recipient node (logger) : last 4 digits of MAC address
    Sender node : 8-digit MAC address
    Telemetry (sensor) type : {BME, PMSA, INA, DeviceMetrics}
    Timestamp : datetime.now() when packet was received
    Sensor reading values
"""

def log_to_csv(filename, data, headers):
    # Write headers if file does not yet exist
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    
    # Append data
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def log_to_txt(filename, data):
    with open(filename, 'a') as file:
        file.write(f"{data}\n")

def format_to_log(data_dict, expected_keys):
    """
    Format data to log to csv file while handling possible missing data.

    Parameters:
    - data_dict: dict, data to log
    - expected_keys: list, keys to expect in the data_dict
    """
    data = []
    for key in expected_keys:
        if key in data_dict:
            data.append(data_dict[key])
        else:
            data.append(None)
    return data

def format_bme_log(data_dict):
    """
    Format BME688 data to log to csv file while handling possible missing data.
    """
    expected_keys = ['temperature', 'relativeHumidity', 'barometricPressure', 'gasResistance', 'iaq']
    expected_keys += ['rxSnr', 'hopLimit', 'rxRssi', 'hopStart']
    return format_to_log(data_dict, expected_keys), expected_keys

def format_pmsa_log(data_dict):
    """
    Format PMSA003I data to log to csv file while handling possible missing data.
    """
    expected_keys = ['pm10Standard', 'pm25Standard', 'pm100Standard', 'pm10Environmental', 'pm25Environmental', 'pm100Environmental']
    expected_keys += ['rxSnr', 'hopLimit', 'rxRssi', 'hopStart']
    return format_to_log(data_dict, expected_keys), expected_keys

def format_ina_log(data_dict):
    """
    Format INA260 data to log to csv file while handling possible missing data.
    """
    expected_keys = ['ch3Voltage', 'ch3Current']
    expected_keys += ['rxSnr', 'hopLimit', 'rxRssi', 'hopStart']
    return format_to_log(data_dict, expected_keys), expected_keys

def format_device_metrics_log(data_dict):
    """
    Format device metrics data to log to csv file while handling possible missing data.
    """
    expected_keys = ['batteryLevel', 'voltage', 'channelUtilization', 'airUtilTx']
    expected_keys += ['rxSnr', 'hopLimit', 'rxRssi', 'hopStart']
    return format_to_log(data_dict, expected_keys), expected_keys

def log_to_csv_from_preset(filename, curr_date_time, from_node, data_dict, preset):
    """
    Use a set of expected preset data to log to csv file while accounting for missing data.

    Parameters:
    - filename: str, path to the csv file
    - curr_date_time: str, current date and time
    - from_node: str, node id
    - data: list, data to log
    - preset: function handle, function to format data
    - headers: list, expected keys of sensor readings
    """
    
    preset_data, expected_keys = preset(data_dict)
    print("Expected_keys:", expected_keys)
    print("Preset data:", preset_data)
    data_to_log = [curr_date_time, from_node] + preset_data
    headers = ["Timestamp", "Sender"] + expected_keys

    log_to_csv(filename, data_to_log, headers)

def on_receive(packet, interface):
    """
    Callback reads BME688, PMSA003I, INA260, DeviceMetrics data packets over the e.g. serial interface.
    """

    print(f"Received Packet: {packet}")
    # print("All reachable nodes:", interface.nodes.keys())

    # nodeid is the last 4 hex digits of node connected via serial port
    nodeid = hex(interface.myInfo.my_node_num)[-4:]

    log_file_prefix = f'./data/{nodeid}'

    try:
        from_node = hex(packet['from'])
        print("\nFrom node:", from_node)
        
        if packet['decoded']['portnum'] == 'TELEMETRY_APP':
            telemetry_data = packet['decoded']['telemetry']
            print(f"Packet from {packet['fromId']} at {str(datetime.now())}")

            signal_strength_data = {key: packet[key] for key in ['rxSnr', 'rxRssi', 'hopLimit', 'hopStart'] if key in packet}

            if 'environmentMetrics' in telemetry_data:
                expected_keys = []
                print("BME688")
                metrics = telemetry_data['environmentMetrics']
                print(metrics)
                # log_to_csv(f'./data/{nodeid}_bme688.csv', [str(datetime.now()), from_node, metrics['temperature'], metrics['relativeHumidity'],
                #          metrics['barometricPressure'], metrics['gasResistance'], metrics['iaq']])
                log_to_csv_from_preset(f'{log_file_prefix}_bme.csv', str(datetime.now()), 
                                       from_node, metrics | signal_strength_data, format_bme_log)

            elif 'airQualityMetrics' in telemetry_data:
                print("PMSA003I")
                metrics = telemetry_data['airQualityMetrics']
                print(metrics)
                # log_to_csv(f'./data/{nodeid}_pmsa003i.csv', 
                #            [str(datetime.now()), from_node, metrics['pm10Standard'], metrics['pm25Standard'], metrics['pm100Standard'], 
                #             metrics['pm10Environmental'], metrics['pm25Environmental'], metrics['pm100Environmental']])
                log_to_csv_from_preset(f'{log_file_prefix}_pmsa.csv', str(datetime.now()),
                                       from_node, metrics | signal_strength_data, format_pmsa_log)
                
            elif 'powerMetrics' in telemetry_data:
                print("INA260")
                metrics = telemetry_data['powerMetrics']
                print(metrics)
                # log_to_csv(f'./data/{nodeid}_ina260.csv', [str(datetime.now()), from_node, metrics['ch3Voltage']])
                log_to_csv_from_preset(f'{log_file_prefix}_ina.csv', str(datetime.now()),
                                       from_node, metrics | signal_strength_data, format_ina_log)

            elif 'deviceMetrics' in telemetry_data:
                print("Device Metrics")
                metrics = telemetry_data['deviceMetrics']
                print(metrics)
                # log_to_csv(f'./data/{nodeid}_device_metrics.csv', [str(datetime.now()), from_node, metrics['batteryLevel'], 
                #     metrics['voltage'], metrics['channelUtilization'], metrics['airUtilTx']])
                log_to_csv_from_preset(f'{log_file_prefix}_devicemetrics.csv', str(datetime.now()),
                                       from_node, metrics | signal_strength_data, format_device_metrics_log)

            else:
                print("Other packet")
                print(telemetry_data)
                log_to_csv(f'{log_file_prefix}_other.csv', [str(datetime.now()), from_node, telemetry_data])

            # log telemetry data
            log_to_txt(f'{log_file_prefix}_logs.txt', [str(datetime.now()), from_node, telemetry_data])

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
