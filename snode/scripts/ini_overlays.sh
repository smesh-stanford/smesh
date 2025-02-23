#  check for if we have the following text prior to appending 
overlays="\ndtoverlay=i2c-rtc,ds1307\ndtoverlay=gpio-shutdown,gpio_pin=6\n"
overlay_no_returns="dtoverlay=i2c-rtc,ds1307\ndtoverlay=gpio-shutdown,gpio_pin=6"
overlays_path="/boot/firmware/config.txt"
if ! grep -qxF "$overlay_no_returns" "$overlays_path"; then 
	echo "setting up dtoverlay"
	sudo echo -e "$overlays" | sudo tee -a "$overlays_path"
else
	echo "already enabled overlays to activate the I2C RTC and shutdown, skipping setup"
fi
