#!/bin/bash

# Navigate to the project directory (Neccessary)
cd ~/smesh/snode

# Run the Python script
/usr/bin/python3 ~/smesh/snode/scripts/upload_to_gdrive.py >> ~/smesh/snode/data/upload_gdrive_stdouterr_log.txt 2>&1

