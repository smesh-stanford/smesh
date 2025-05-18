# Set up the logger script, which will run automatically each time the RPi boots
if ! sudo test -f /var/spool/cron/crontabs/pi; then echo "pi's crontab does not exist."
    echo "$(echo '@reboot source /home/pi/.bashrc; cd /home/pi/Documents/smesh/snode; mkdir -p data/; echo "wind logging starting" >> data/pigpio_stderr_wind.txt 2>&1; sudo pigpiod & >> data/pigpio_stderr_wind.txt 2>&1; python scripts/rpi_log_wind.py >> data/rpi_stderr_wind.txt 2>&1' ;) " | crontab  - -u pi
fi
crontab -l
#