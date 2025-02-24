sudo apt -y install git pip network-manager screen dos2ux
sudo apt update
sudo apt -y upgrade


#  This is pulling down main.  It won't pull down a development branch
directory_name="/home/pi/Documents"
git clone "https://github.com/smesh-stanford/smesh.git" "$directory_name/smesh"

# add the path that Python will be looking for.  Needs the export so we can use it in the current shell
if ! grep "PATH" /home/pi/.bashrc 
    echo "PATH=$PATH:/home/pi/.local/bin" >> /home/pi/.bashrc
    echo "export PATH" >> /home/pi/.bashrc
# cd smesh/snode
    source /home/pi/.bashrc
fi

# Install the required packages 
pip install -r /home/pi/Documents/smesh/snode/requirements.txt --break-system-packages

# Initialize the radio (if connected)
python -m meshtastic --configure /home/pi/Documents/smesh/firmware/build_1_config.yaml
