echo "Checking internet access to google.com ..."
# Only run 3 pings
ping google.com -c 3

echo "---"
echo "Current ifconfig:"
ifconfig

# desired wifi accesspoint name
wifi_ap="INSERT" # CHANGE THIS PER PI
if ! nmcli d wifi list | grep -q "$wifi_ap"; then
	# The first if catches when we are already connected to the wifi accesspoint
	if ! nmcli connection show | grep -q "accesspoint"; then
		# The second if catches when we are not connected to the wifi accesspoint
		sudo nmcli con add type wifi ifname wlan0 mode ap con-name 'accesspoint' ssid "$wifi_ap" autoconnect true
		# CHANGE THE IP ADDRESS PER PI
		sudo nmcli con modify 'accesspoint' 802-11-wireless.band bg ipv4.method shared ipv4.address 192.1{INSERT}8.6.1/24
		sudo nmcli con modify 'accesspoint' ipv6.method disabled
		sudo nmcli con modify 'accesspoint' wifi-sec.key-mgmt wpa-psk
		sudo nmcli con modify 'accesspoint' wifi-sec.psk "smesh1234"
		sudo nmcli con up 'accesspoint'
	else 
		echo "accesspoint already setup, skipping setup"
	fi
else
	echo "wifi accesspoint already setup under $wifi_ap, skipping setup"
fi

echo "---"
echo "Current nmcli connections:"
nmcli connection show
nmcli d wifi list
echo "---"
echo "Current ifconfig:"
ifconfig
