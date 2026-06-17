#!/bin/bash

# Navigate to the project directory (Neccessary)
cd ~/smesh/snode

# Run the Python script (will use Python 3.10 by default)
python ~/smesh/snode/scripts/upload_to_gdrive.py >> ~/smesh/snode/data/upload_gdrive_stdouterr_log.txt 2>&1

