#  This runs the SMesh Logger setups.
#  It doesn't need sudo when called during boot time from firstrun, but for running later in debug, it might be helpful.
#  For this to work, after imaging the OS from your laptop, do this
#      git clone https://github.com/smesh-stanford/smesh.git ; cp smesh/snode/script/ini_* <path to sd card>/boot/firmware/firmware

# It seems we are not giving full rwx permissions to root and user int these
# ini_* scripts.
# 777 gives rwx to all users.
sudo chmod +x /boot/firmware/ini_cron.sh
sudo chmod 777 /boot/firmware/ini_cron.sh
sudo chmod +x /boot/firmware/ini_hotspot.sh
sudo chmod +x /boot/firmware/ini_overlays.sh
sudo chmod +x /boot/firmware/ini_swap.sh
sudo chmod +x /boot/firmware/ini_swinstall.sh
sudo chmod +x /boot/firmware/ini_wifi.sh

#  Get rid of the ^m's.  This is a problem when the file is copied from Windows to Linux
# dos2ux ini_*

# Make the directory for the logs
log_dir="/home/pi/logs_firstrun"
sudo mkdir -p $log_dir
sudo chmod 777 $log_dir

# Order matters! (Must be sequential)
# 1. ini_wifi.sh: (WIFI) Needed for software download
# 2. ini_overlays.sh: (Clock & Switch) Needed for safe power off
# 3. ini_swap.sh: (Swap) Needed for space for software installation
# 4. ini_swinstall.sh: (Software Install) Needed for running cron & logger
# 5. ini_cron.sh: (Run logger at boot)
# 6. ini_hotspot.sh: (Hotspot) Needed for connecting to the pi without a network
#
# We may want to run these with sudo -u pi, but for now, let's run them as root.
# Use the directory above for the logs. 
echo "WIFI INITIALIZATION"
sudo bash -c "/boot/firmware/ini_wifi.sh 2>&1 | tee -a ${log_dir}/firstrun_ini_wifi.log"
echo "---"
echo "OVERLAYS INITIALIZATION"
sudo bash -c "/boot/firmware/ini_overlays.sh 2>&1 | tee -a ${log_dir}/firstrun_ini_overlays.log"
echo "---"
echo "SWAP INITIALIZATION"
sudo bash -c "/boot/firmware/ini_swap.sh 2>&1 | tee -a ${log_dir}/firstrun_ini_swap.log"
echo "---"
echo "SOFTWARE INSTALLATION INITIALIZATION"
sudo bash -c "/boot/firmware/ini_swinstall.sh 2>&1 | tee -a ${log_dir}/firstrun_ini_swinstall.log"
echo "---"
echo "CRON INITIALIZATION"
sudo bash -c "/boot/firmware/ini_cron.sh 2>&1 | tee -a ${log_dir}/firstrun_ini_cron.log"
echo "---"
echo "HOTSPOT INITIALIZATION"
sudo bash -c "/boot/firmware/ini_hotspot.sh 2>&1 | tee -a ${log_dir}/firstrun_ini_hotspot.log"
echo "SMESH LOGGER INITIALIZATION COMPLETE"
