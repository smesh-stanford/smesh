
# First, set up the directory
directory_name="/home/pi/Documents"
mkdir -p "$directory_name"

# Install the necessary packages
echo "---"
echo "Checking internet connection..."
ping google.com -c 3
date

# the line below is a bit scary, but it seems to be a possible solution to 
# apt-get update error (mainly the package lists are out of date and need to 
# be completely refreshed)
sudo rm -vrf /var/lib/apt/lists/* 
# apt-get is the script version. using apt will not work here
# also, update seems to be needed before install
sudo apt-get update
sudo apt-get -y install git pip screen
# sudo apt-get -y install network-manager screen dos2unix
#sudo apt update
#sudo apt -y upgrade


#  This is pulling down main.  It won't pull down a development branch

if  ! test -f "$directory_name/smesh"; then
	 echo "file $directory_name/smesh does not exist yet"
     git clone "https://github.com/smesh-stanford/smesh.git" "$directory_name/smesh"
     echo "cloned smesh repo"
fi

# add the path that Python will be looking for.  Needs the export so we can use it in the current shell
if ! grep "PATH" /home/pi/.bashrc; then
    echo "PATH=$PATH:/home/pi/.local/bin" >> /home/pi/.bashrc
    echo "export PATH" >> /home/pi/.bashrc
# cd smesh/snode
    source /home/pi/.bashrc
fi

# Install the required packages as pi!
sudo -u pi pip install -r /home/pi/Documents/smesh/snode/requirements.txt --break-system-packages

# Initialize the radio (if connected) as pi!
sudo -u pi python -m meshtastic --configure /home/pi/Documents/smesh/firmware/build_1_config.yaml

# Check if the USB is available in devices
echo "---"
echo "Checking tty devices (should see a ttyUSB*)..."
ls /dev/ttyUSB*
echo "---"
