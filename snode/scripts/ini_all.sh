#!/bin/bash

# We expect that the username is "pi" such that this script accesses the proper directories

# Note to self: we want to configure flashing the SD card... and perhaps that's where we can input the WiFi secrets!

#  This script is appended to /boot/firstrun.sh and is run only once, at the first boot of the RPi.
#  It sets up the RPi to run the smesh software and connect to the smesh network.
#  https://forums.raspberrypi.com/viewtopic.php?t=320331
#
#  
#
#  Set up EE-IoT and SMesh phone hot spot SSID's.  Give them time to connect.
#

#
# Setup WiFi to EE-IoT
#
wifi_source_SSID="EE-IoT"

nmcli radio wifi on
# INSERT Wifi configuration section... TODO
if ! nmcli connection show | grep -q "$wifi_source_SSID"; then
	nmcli connection add type wifi ifname wlan0 con-name "$wifi_source_SSID" ssid "$wifi_source_SSID"
	nmcli connection modify "$wifi_source_SSID" wifi-sec.key-mgmt wpa-psk
	nmcli connection modify "$wifi_source_SSID" wifi-sec.psk "350Serra"
	nmcli connection modify "$wifi_source_SSID" 802-11-wireless.hidden yes
	nmcli connection modify "$wifi_source_SSID" 802-11-wireless-security.proto rsn
	nmcli connection modify "$wifi_source_SSID" connection.autoconnect yes
	echo "connected to $wifi_source_SSID"
else
	echo "already setup $wifi_source_SSID, skipping setup"
fi

# nmcli connection up "$wifi_source_SSID" 

#
#  Enable overlays to activate the I2C real time clock and 
#  the shutdown switch on GPIO 6 (pin 30 & 31). If no RTC available, will throw no 
#  issues. Not that the RTC will use the I2C bus on GPIO 2 and 3 (pins 3 and 5).
#

#  check for if we have the following text prior to appending 
overlays="\ndtoverlay=i2c-rtc,ds1307\ndtoverlay=gpio-shutdown,gpio_pin=6\n"
overlay_no_returns="dtoverlay=i2c-rtc,ds1307\ndtoverlay=gpio-shutdown,gpio_pin=6"
overlays_path="/boot/firmware/config.txt"
if ! grep -qxF "$overlay_no_returns" "$overlays_path"; then 
	echo "setting up dtoverlay"
	sudo echo -e "$overlays" | sudo tee -a "$overlays_path"
else
	echo "already enabled overlays to activate the I2C RTC and shutdown, skipping setup"
fi

#
# Setup swap space to be 1G
# turn off swap file such that we can change it
#
# Change swappiness from a default of 60 to 1to decrease swap activity to preserve the life of the SD card
#

sudo dphys-swapfile swapoff 

# we only anticipate one CONF_SWAPSIZE so there should be no concern of a different line
# being modified for the swapsize, so checking if the line already exists isn't necessary
sudo sed -i '0,/^CONF_SWAPSIZE=/s/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

swappiness="vm.swappiness=1\n"
swappiness_path="/etc/sysctl.conf"
if ! grep -qxF "$swappiness" "$swappiness_path"; then
	sudo echo -e "$swappiness" | sudo tee -a "$swappiness_path" 
else
	echo "already set swappiness to 1, skipping setup"
fi

#
# Parameters: 
# argument $1: name of the hotspot provided by user

# TODO: add in the setup for the cellular link

#
# Grab any relevant libraries to install dependencies and download repo
#

sudo apt update
sudo apt -y upgrade
sudo apt -y install git pip

directory_name="/home/pi/Documents"
git clone "https://github.com/smesh-stanford/smesh.git" "$directory_name"

# cd smesh/snode
source /home/pi/.bashrc

# Install the required packages 
pip install -r /home/pi/Documents/smesh/snode/requirements.txt --break-system-packages

# Initialize the radio (if connected)
python -m meshtastic --configure /home/pi/Documents/smesh/firmware/build_1_config.yaml

# Set up the logger script, which will run automatically each time the RPi boots
if ! test -f /var/spool/cron/crontabs/pi; then echo "pi's crontab does not exist."
    echo "$(echo '@reboot source /home/pi/.bashrc; cd /home/pi/Documents/smesh/snode; python scripts/rpi_logger.py /dev/ttyUSB0 >> data/rpi_stdouterr.txt 2>&1' ;) " | crontab  -
fi
crontab -l
#
# WiFi hotspot to SSH into RaspberryPi (i.e. setup access point)
#

# desired wifi accesspoint name
wifi_ap="smesh_1"
if ! nmcli connection show | grep -q "$wifi_ap"; then
	sudo nmcli con add type wifi ifname wlan0 mode ap con-name 'accesspoint' ssid "$wifi_ap" autoconnect true
	sudo nmcli con modify 'accesspoint' 802-11-wireless.band bg ipv4.method shared ipv4.address 192.168.6.1/24
	sudo nmcli con modify 'accesspoint' ipv6.method disabled
	sudo nmcli con modify 'accesspoint' wifi-sec.key-mgmt wpa-psk
	sudo nmcli con modify 'accesspoint' wifi-sec.psk "smesh1234"
	sudo nmcli con up 'accesspoint'
else
	echo "wifi accesspoint already setup under $wifi_ap, skipping setup"
fi

#  The RPi takes care of insuring that this file runs only once, at setup time, and reboots the 
#  RPi after the setup is complete.
