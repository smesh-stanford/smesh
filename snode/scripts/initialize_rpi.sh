#!/bin/bash

# We expect that the name of the pi is "pi" such that this script accesses the proper directories

# Note to self: we want to configure flashing the SD card... and perhaps that's where we can input the WiFi secrets!

#  This script is appended to /boot/firstrun.sh and is run only once, at the first boot of the RPi.
#  It sets up the RPi to run the smesh software and connect to the smesh network.
#  https://forums.raspberrypi.com/viewtopic.php?t=320331
#
#  Set up EE-IoT and SMesh phone hot spot SSID's.  Give them time to connect.
nmcli radio wifi on
# INSERT Wifi configuration section... TODO
nmcli connection add type wifi ifname wlan0 con-name "EE-IoT" ssid "EE-IoT"
nmcli connection modify "EE-IoT" wifi-sec.key-mgmt wpa-psk
nmcli connection modify "EE-IoT" wifi-sec.psk "INSERT_PASSWORD"
nmcli connection modify "EE-IoT" 802-11-wireless.hidden yes
nmcli connection modify "EE-IoT" 802-11-wireless-security.proto rsn
nmcli connection up "EE-IoT"
# currently sleeping for 15 seconds... this seems to make a difference for the time required
# to setup the connection
sleep 15


#  Enable overlays to activate the I2C real time clock and 
#  the shutdown/reboot switch on GPIO 3 (pin 5). If no RTC available, will throw no issues
sudo echo -e "\ndtoverlay=i2c-rtc,ds1307\ndtoverlay=gpio-shutdown,gpio_pin=3\n" | sudo tee -a /boot/firmware/config.txt 

# Setup swap space to be 1G
# turn off swap file such that we can change it
sudo dphys-swapfile swapoff 
sudo sed -i '0,/^CONF_SWAPSIZE=/s/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# TODO: LED showing RPi running https://drive.google.com/file/d/1JKwW2ykTD3mngxr49Tp5c5CxWLDgQb8F/view?usp=share_link

# Change swappiness from a default of 60 to 1to decrease swap activity to preserve the life of the SD card
sudo echo -e "vm.swappiness=1\n" | sudo tee -a /etc/sysctl.conf

# Does this still make sense if we append this script to the end of firstrun.sh?
# Parameters: 
# argument $1: name of the hotspot provided by user
wifi_name="1234"

# TODO: add in the setup for the cellular link

# section requires internet you set when imaging the uSD card
sudo apt update
sudo apt -y upgrade
sudo apt -y install git pip
cd /home/pi
mkdir Documents
cd Documents
git clone https://github.com/smesh-stanford/smesh.git
cd smesh/snode
source /home/pi/.bashrc

# Install the required packages 
pip install -r requirements.txt --break-system-packages

# Initialize the radio (if connected)
python -m meshtastic --configure /home/pi/Documents/smesh/firmware/build_1_config.yaml

# Set up the logger script, which will run automatically each time the RPi boots
echo "$(echo '@reboot source /home/pi/.bashrc; cd /home/pi/Documents/smesh/snode; python scripts/rpi_logger.py /dev/ttyUSB0 >> data/rpi_stdouterr.txt 2>&1' ;) " | crontab  -
crontab -l

# WiFi hotspot to SSH into RaspberryPi 
# TODO, come back and make this where it won't recreate this wifi network 
sudo nmcli con add type wifi ifname wlan0 mode ap con-name 'accesspoint' ssid "smesh_INSERT_NAME" autoconnect true
sudo nmcli con modify 'accesspoint' 802-11-wireless.band bg ipv4.method shared ipv4.address 192.168.6.1/24
sudo nmcli con modify 'accesspoint' ipv6.method disabled
sudo nmcli con modify 'accesspoint' wifi-sec.key-mgmt wpa-psk
sudo nmcli con modify 'accesspoint' wifi-sec.psk "smesh1234"
sudo nmcli con up 'accesspoint'
#  The RPi takes care of insuring that this file runs only once, at setup time, and reboots the 
# RPi after the setup is complete.
