#!/bin/bash

# Navigate to the project directory (Neccessary)
cd ~/smesh/snode

# Run the Python script
/usr/bin/python3 ~/smesh/snode/scripts/read_aqi.py /dev/ttyUSB0 >> ~/smesh/snode/data/read_aqi_stdouterr_log.txt 2>&1