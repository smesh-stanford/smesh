#!/bin/bash

# Navigate to the project directory (Neccessary)
cd ~/smesh/snode

# Run the Python script (will use Python 3.10 by default)
python ~/smesh/snode/scripts/rpi_log_script_v3.py /dev/ttyUSB0 >> ~/smesh/snode/data/rpi_log_script_v3_stdouterr_log.txt 2>&1

