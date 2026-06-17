
# First, set up the directory
directory_name="/home/pi/Documents"
sudo -u pi mkdir -p "$directory_name"

# Install the necessary packages
echo "---"
echo "Checking internet connection..."
ping google.com -c 3
date

# Check that the time is uptodate
echo "---"
echo "Checking time manager is active..."
timedatectl status
timedatectl show
timedatectl
timedatectl set-ntp true
echo "---"
echo "Manually setting time..."
sudo date -s 2025-04-15T12:00:00
date
echo "---"
echo "Wait 40 seconds for the time to sync if possible..."
sleep 40
date
timedatectl status
timedatectl show
echo "---"


# the line below is a bit scary, but it seems to be a possible solution to 
# apt-get update error (mainly the package lists are out of date and need to 
# be completely refreshed)
sudo rm -vrf /var/lib/apt/lists/* 
# apt-get is the script version. using apt will not work here
# also, update seems to be needed before install
sudo apt-get update

# Install Python 3.10 and required packages
sudo apt-get -y install software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get -y install python3.10 python3.10-venv python3.10-dev python3.10-distutils
sudo apt-get -y install git screen

# Install pip for Python 3.10
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10

# Set Python 3.10 as the default python3 and python commands system-wide
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 100
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 100

# Make pip3 point to Python 3.10's pip
sudo update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.10 100
sudo update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.10 100
# sudo apt-get -y install network-manager screen dos2unix
#sudo apt update
#sudo apt -y upgrade


#  This is pulling down main.  It won't pull down a development branch

if  ! test -f "$directory_name/smesh"; then
	 echo "file $directory_name/smesh does not exist yet"
     sudo -u pi git clone "https://github.com/smesh-stanford/smesh.git" "$directory_name/smesh"
     echo "cloned smesh repo"
fi

# add the path that Python will be looking for.  Needs the export so we can use it in the current shell
if ! grep "PATH" /home/pi/.bashrc; then
    echo "PATH=$PATH:/home/pi/.local/bin" >> /home/pi/.bashrc
    echo "export PATH" >> /home/pi/.bashrc
fi

# Ensure Python 3.10 is used by default for the pi user
if ! grep "alias python=" /home/pi/.bashrc; then
    echo "# Use Python 3.10 as default" >> /home/pi/.bashrc
    echo "alias python=python3.10" >> /home/pi/.bashrc
    echo "alias python3=python3.10" >> /home/pi/.bashrc
    echo "alias pip=pip3.10" >> /home/pi/.bashrc
    echo "alias pip3=pip3.10" >> /home/pi/.bashrc
fi

# Source the updated bashrc
source /home/pi/.bashrc

# Install the required packages as pi (will use Python 3.10 by default)!
sudo -u pi pip install -r /home/pi/Documents/smesh/snode/requirements.txt --break-system-packages

# Initialize the radio (if connected) as pi (will use Python 3.10 by default)!
echo "---"
sudo -u pi python -m meshtastic --configure /home/pi/Documents/smesh/firmware/build_1_config.yaml

# Check if the USB is available in devices
echo "---"
echo "Checking tty devices (should see a ttyUSB*)..."
ls /dev/ttyUSB*
echo "---"
