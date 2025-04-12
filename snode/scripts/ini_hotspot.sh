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
