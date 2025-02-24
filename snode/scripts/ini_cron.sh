# Set up the logger script, which will run automatically each time the RPi boots
if ! sudo test -f /var/spool/cron/crontabs/pi; then echo "pi's crontab does not exist."
    echo "$(echo '@reboot source /home/pi/.bashrc; cd /home/pi/Documents/smesh/snode; python scripts/rpi_logger.py /dev/ttyUSB0 >> data/rpi_stdouterr.txt 2>&1' ;) " | crontab  - -u pi
fi
crontab -l
#