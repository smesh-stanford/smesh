#  This runs the SMesh Logger setups.
#  It doesn't need sudo when called during boot time from firstrun, but for running later in debug, it might be helpful.
#  For this to work, after imaging the OS from your laptop, do this
#      git clone https://github.com/smesh-stanford/smesh.git ; cp smesh/snode/script/ini_* <path to sd card>/boot/firmware

sudo chmod +x /boot/ini_cron.sh
sudo chmod +x /boot/ini_hotspot.sh
sudo chmod +x /boot/ini_overlays.sh
sudo chmod +x /boot/ini_swap.sh
sudo chmod +x /boot/ini_swinstall.sh
sudo chmod +x /boot/ini_wifi.sh

sudo source /boot/ini_wifi.sh >> /boot/firstrun_ini_wifi.log 2>&1
sudo source /boot/ini_overlays.sh >> /boot/firstrun_ini_overlays.log 2>&1
sudo source /boot/ini_swap.sh >> /boot/firstrun_ini_swap.log 2>&1
sudo source /boot/ini_swinstall.sh >> /boot/firstrun_ini_swinstall.log 2>&1
sudo source /boot/ini_cron.sh >> /boot/firstrun_ini_cron.log 2>&1
sudo source /boot/ini_hotspot.sh >> /boot/firstrun_ini_hotspot.log 2>&1
