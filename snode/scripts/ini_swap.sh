 Setup swap space to be 1G
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