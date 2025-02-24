#  This runs the SMesh Logger setups.
#  It doesn't need sudo when called during boot time from firstrun, but for running later in debug, it might be helpful.
#  For this to work, after imaging the OS from your laptop, do this
#      git clone https://github.com/smesh-stanford/smesh.git ; cp smesh/snode/script/ini_* <path to sd card>/boot/firmware/firmware

sudo chmod +x /boot/firmware/ini_cron.sh
sudo chmod +x /boot/firmware/ini_hotspot.sh
sudo chmod +x /boot/firmware/ini_overlays.sh
sudo chmod +x /boot/firmware/ini_swap.sh
sudo chmod +x /boot/firmware/ini_swinstall.sh
sudo chmod +x /boot/firmware/ini_wifi.sh

sudo bash -c '/boot/firmware/ini_wifi.sh >> /boot/firmware/firstrun_ini_wifi.log 2>&1'
sudo bash -c '/boot/firmware/ini_overlays.sh >> /boot/firmware/firstrun_ini_overlays.log 2>&1'
sudo bash -c '/boot/firmware/ini_swap.sh >> /boot/firmware/firstrun_ini_swap.log 2>&1'
sudo bash -c '/boot/firmware/ini_swinstall.sh >> /boot/firmware/firstrun_ini_swinstall.log 2>&1'
sudo bash -c '/boot/firmware/ini_cron.sh >> /boot/firmware/firstrun_ini_cron.log 2>&1'
sudo bash -c '/boot/firmware/ini_hotspot.sh >> /boot/firmware/firstrun_ini_hotspot.log 2>&1'
