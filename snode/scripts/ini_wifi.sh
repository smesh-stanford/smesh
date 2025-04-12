wifi_source_SSID="EE-IoT"

sudo nmcli radio wifi on
# INSERT Wifi configuration section... TODO
if ! sudo nmcli connection show | grep -q "$wifi_source_SSID"; then
	sudo nmcli connection add type wifi ifname wlan0 con-name "$wifi_source_SSID" ssid "$wifi_source_SSID"
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.key-mgmt wpa-psk
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.psk "350Serra"
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
	sudo nmcli connection modify "$wifi_source_SSID" wifi-sec.psk "spaghetti"
	sudo nmcli connection modify "$wifi_source_SSID" 802-11-wireless.hidden no
	sudo nmcli connection modify "$wifi_source_SSID" 802-11-wireless-security.proto rsn
	sudo nmcli connection modify "$wifi_source_SSID" connection.autoconnect yes
	echo "enabled connection to $wifi_source_SSID"
else
	echo "already setup $wifi_source_SSID, skipping setup"
fi
