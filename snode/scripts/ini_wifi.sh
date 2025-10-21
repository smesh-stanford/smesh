
# First, check if we have internet access
echo "Checking internet access to google.com ..."
# Only run 3 pings
ping google.com -c 3

echo "---"
date
echo "Current ifconfig:"
ifconfig

# Activate the NetworkManager service over the default raspberry pi network
echo "---"
echo "Checking NetworkManager is in /etc/..."
ls /etc/NetworkManager
echo "---"
echo "Checking NetworkManager status..."
sudo systemctl status NetworkManager
echo "---"
echo "Current nmcli connections:"
nmcli connection show
nmcli d wifi list
echo "---"
echo "Activating NetworkManager service..."
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager


echo "---"
echo "Current nmcli connections:"
nmcli connection show
nmcli d wifi list

echo "Adding wifi connections to the system"


wifi_source_SSID="EE-IoT"
sudo nmcli radio wifi on
# INSERT Wifi configuration section... TODO
if ! sudo nmcli connection show | grep -q "$wifi_source_SSID"; then
	sudo nmcli connection add type wifi ifname wlan0 con-name "$wifi_source_SSID" ssid "$wifi_source_SSID"
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.key-mgmt wpa-psk
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.psk "INSERT"
	sudo nmcli connection modify "$wifi_source_SSID" 802-11-wireless.hidden yes
	sudo nmcli connection modify "$wifi_source_SSID" 802-11-wireless-security.proto rsn
	sudo nmcli connection modify "$wifi_source_SSID" connection.autoconnect yes
	echo "enabled connection to $wifi_source_SSID"
else
	echo "already setup $wifi_source_SSID, skipping setup"
fi

wifi_source_SSID="K6TJ iPhone"
sudo nmcli radio wifi on
# INSERT Wifi configuration section... TODO
if ! sudo nmcli connection show | grep -q "$wifi_source_SSID"; then
	sudo nmcli connection add type wifi ifname wlan0 con-name "$wifi_source_SSID" ssid "$wifi_source_SSID"
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.key-mgmt wpa-psk
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.psk "INSERT"
	sudo nmcli connection modify "$wifi_source_SSID" 802-11-wireless.hidden no
	sudo nmcli connection modify "$wifi_source_SSID" 802-11-wireless-security.proto rsn
	sudo nmcli connection modify "$wifi_source_SSID" connection.autoconnect yes
	echo "enabled connection to $wifi_source_SSID"
else
	echo "already setup $wifi_source_SSID, skipping setup"
fi


wifi_source_SSID="aerocloud"
sudo nmcli radio wifi on
# INSERT Wifi configuration section... TODO
if ! sudo nmcli connection show | grep -q "$wifi_source_SSID"; then
	sudo nmcli connection add type wifi ifname wlan0 con-name "$wifi_source_SSID" ssid "$wifi_source_SSID"
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.key-mgmt wpa-psk
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.psk "INSERT"
	sudo nmcli connection modify "$wifi_source_SSID" 802-11-wireless.hidden no
	sudo nmcli connection modify "$wifi_source_SSID" 802-11-wireless-security.proto rsn
	sudo nmcli connection modify "$wifi_source_SSID" connection.autoconnect yes
	echo "enabled connection to $wifi_source_SSID"
else
	echo "already setup $wifi_source_SSID, skipping setup"
fi

# Show the wifi connections
sudo nmcli d wifi list
sudo nmcli connection show
