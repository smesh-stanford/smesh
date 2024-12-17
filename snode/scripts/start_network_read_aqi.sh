#!/bin/bash

# Navigate to the project directory (Neccessary)
cd ~/smesh/snode

# Run the Python script
/usr/bin/python3 ~/smesh/snode/scripts/network_test.py /dev/ttyUSB0 >> ~/smesh/snode/data/network_test_stdouterr_log.txt 2>&1

