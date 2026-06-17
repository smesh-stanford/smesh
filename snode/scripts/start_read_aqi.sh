#!/bin/bash

# Navigate to the project directory (Neccessary)
cd ~/smesh/snode

# Run the Python script (will use Python 3.10 by default)
python ~/smesh/snode/scripts/read_aqi.py /dev/ttyUSB0 >> ~/smesh/snode/data/read_aqi_stdouterr_log.txt 2>&1
