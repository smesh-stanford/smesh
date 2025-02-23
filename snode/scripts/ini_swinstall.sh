sudo apt update
sudo apt -y upgrade
sudo apt -y install git pip

directory_name="/home/pi/Documents"
git clone "https://github.com/smesh-stanford/smesh.git" "$directory_name/smesh"

# cd smesh/snode
source /home/pi/.bashrc

# Install the required packages 
pip install -r /home/pi/Documents/smesh/snode/requirements.txt --break-system-packages

# Initialize the radio (if connected)
python -m meshtastic --configure /home/pi/Documents/smesh/firmware/build_1_config.yaml
