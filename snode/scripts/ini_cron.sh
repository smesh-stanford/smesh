# Set up the logger script, which will run automatically each time the RPi boots
# Workflow:
# 1. Check if the command is already in the crontab
# 2. If not, add the command to pi's crontab
#    a. At reboot (i.e., when the system starts up)
#    b. Source the .bashrc to match the environment variables
#    c. Change to the directory to the snode directory
#    d. Create the data directory if it doesn't exist
#    e. Run the logger script with the specified arguments (i.e., serial port)
#    f. Redirect the standard output and error to a file in the data directory
# 3. Verify that the command has been added successfully
if ! sudo test -f /var/spool/cron/crontabs/pi; then echo "pi's crontab does not exist."
    echo "$(echo '@reboot source /home/pi/.bashrc; cd /home/pi/Documents/smesh/snode; mkdir -p data/; python scripts/rpi_log_script.py /dev/ttyUSB0 >> data/rpi_stdouterr.txt 2>&1' ;) " | crontab  - -u pi
fi
crontab -l
#
