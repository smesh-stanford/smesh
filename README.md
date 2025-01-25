# What is SMesh?
___
SMesh is a sensor mesh network ("smesh") that performs long duration environmental sensing for sustainability research at Stanford.

A smesh node (or "snode") consists of a sensor payload plus a Meshtastic board that can relay readings using long range LoRa radio.

# Customizing Meshtastic firmware
___
Snodes run a stable version of Meshtastic firmware with small modifications.

To access this firmware:
1. Clone the firmware fork, i.e. `git clone https://github.com/josdo/meshtastic-firmware.git`
2. Follow https://meshtastic.org/docs/development/firmware/build/ to set up PlatformIO, a tool to build firmware from source. 
   **Note:** at step 3, pick `heltec-v3` from the list of options given.

# SMesh - Raspberry Pi Setup Guide
___

## Install Raspberry Pi OS on SD Card

1. Go to: [Raspberry Pi Software](https://www.raspberrypi.com/software/)
2. Download and install **Raspberry Pi Imager**.
3. Insert your SD card into your computer or laptop.
4. Open **Raspberry Pi Imager**.
5. Click on the **CHOOSE OS** box, then select:
    - `Raspberry Pi OS (other)`
    - Scroll down and select: `Raspberry Pi OS (Legacy, 32-bit) Lite`
6. Click on the **CHOOSE STORAGE** box and select your SD card.
7. Click on the **Settings** icon in the bottom right corner, then follow the steps:
    - Set hostname to `smeshX` (where X represents the number of the current system).
    - Tick the **Enable SSH** box.
    - Set the username and password:
      - Username: `pi`
      - Password: `smesh`
    - Configure wireless LAN:
      - SSID: Name of your WiFi network
      - Password: Password of your WiFi network
      - Wireless LAN country: `US`
    - Click **SAVE**.
8. Click **WRITE** to begin writing the OS to the SD card.
9. Once the Raspberry Pi OS has been installed, remove the SD card from your computer and insert it into your Raspberry Pi.
10. Power the Raspberry Pi by connecting a micro USB cable to the **PWR IN** slot (connected to a battery pack or wall outlet).
11. A green LED should light up near the **PWR IN** slot to indicate that the Raspberry Pi is ON.

## Remotely Connect to Raspberry Pi via SSH

1. After a couple of minutes, the Raspberry Pi should be connected to your local WiFi network.
2. Ensure your computer/laptop is connected to the same network.
3. Open a Terminal and enter the command:
   ```
   ssh pi@smeshX.local
   ```
4. During the first SSH connection, you may get the following error:
5. If you see this error:
    - Go to your user folder on your computer/laptop.
    - Find a folder named `.ssh`.
    - Open the file named `known_hosts` and delete its content, then save.
    - Try connecting again with:
      ```
      ssh pi@smeshX.local
      ```
6. When asked "*Are you sure you want to continue connecting?*", enter: `yes`.
7. Enter the password: `smesh`.
8. Once you see the prompt starting with `pi@smeshX`, you have successfully connected to the Raspberry Pi via SSH.

## Install Software and Dependencies on Raspberry Pi

1. Once connected via SSH, start by running the following commands:
    ```
    sudo apt update
    sudo apt upgrade
    ```
2. Install Python **pip**:
    ```
    sudo apt install python3-pip
    ```
3. Install **Git**:
    ```
    sudo apt install git -y
    ```
4. Clone the project's GitHub repository:
    ```
    git clone https://github.com/smesh-stanford/smesh.git
    ```
5. Open a different Terminal and upload the `credential.json` file from your own local directory to the Raspberry Pi by entering the command:
    ```
    scp /local/path/to/credentials.json pi@smeshX.local: /home/pi/smesh/snode
    ```
    (e.g. if the credentials.json file is stored in your local Downloads directory: `scp ~/Downloads/credentials.json pi@smeshX.local: /home/pi/smesh/snode` , where X in smeshX represents the number of the current system).
6. Once the upload has been completed, close this Terminal and go back to the previous one (where the SSH connection to the Raspberry Pi was established).
7. Navigate to the `snode` directory:
    ```
    cd ./smesh/snode
    ```
8. Install required dependencies:
    ```
    pip3 install -r requirements.txt
    ```
9. Create a data directory:
    ```
    mkdir data
    ```
10. In its default stage, the code will store any upcoming data packet to this data directory (absolute path: `/home/pi/smesh/snode/data`). In some cases, the user may want to change the name of the data directory to help with data management. In such case, the path to the data directory needs to be changed in the **read_aqi.py, start_read_aqi.sh** and **upload_to_gdrive.py** scripts located in `/smesh/snode/scripts`:
    - **read_aqi.py:** From line 46 - 76, all the path arguments in the **log_to_csv()** function need to be changed to the new data directory path. For instance, if the user created a different data directory named *data_pepperwood*, all path arugments in the log_to_csv() function would be changed to: `f’/home/pi/smesh/snode/**data_pepperwood**/{nodeid}_bme688.csv’`
    - **start_read_aqi.sh:** Line 7, Change the path in the last line from `~/smesh/snode/**data**/read_aqi_stdouterr_log.txt` to the new data directory path (e.g., `~/smesh/snode/**data_pepperwood**/read_aqi_stdouterr_log.txt`)
    - **uploading_to_gdrive.py:** Change the path in ****Line 33 in the main function, to the new data directory path (e.g. `'/home/pi/smesh/snode/**data_pepperwood'**`)
11. Give execute permissions to the script **start_read_aqi.sh**:
    ```
    chmod +x ~/smesh/snode/scripts/start_read_aqi.sh
    ```
12. Open the cron table editor:
    ```
    crontab -e
    ```
13. Enter `1` to select the **nano** text editor.
14. Scroll to the bottom and add the following two lines (the number `5` in the second line indicates the time in minutes between uploads):
    ```
    @reboot ~/smesh/snode/scripts/start_read_aqi.sh
    */5 * * * * /usr/bin/python3 ~/smesh/snode/scripts/upload_to_gdrive.py
    ```
15. Press `Ctrl + X` to exit.
16. Type `Y` and press `Enter` to save changes.
17. Run the command:
    ```
    python3 read_aqi.py /dev/ttyUSB0
    ```
18. The Cron Unix-based job scheduler should now be active, running the `read_aqi.py` and `upload_to_gdrive.py` scripts to upload data to Google Drive.

## Troubleshooting Tips

- Restart the Cron Unix-based job scheduler:
  ```
  sudo service cron restart
  ```
- Check the status of the Cron Unix-based job scheduler:
  ```
  systemctl status cron
  ```

- Test the `read_aqi.py` script for errors:
  1. Navigate to the script directory:
     ```
     cd ~/smesh/snode/scripts/
     ```
  2. Run the script without providing a serial port:
     ```
     python3 read_aqi.py
     ```
  3. If the only error shown is similar to the following, it means all dependencies are correctly installed:
  4. Next, run the script with the USB0 port:
     ```
     python3 read_aqi.py /dev/ttyUSB0
     ```
  5. If you get an error indicating that the port cannot be found, reconnect the Meshtastic or reboot the Raspberry Pi:
     ```
     reboot
     ```
  6. After reboot, reconnect via SSH:
     ```
     ssh pi@smeshX.local
     ```
  7. Enter the password: `smesh`.

# Contributing
*Cutting Releases*
Releases will be formatted as "XX.YY.ZZ" with the following scheme: 
- XX: major feature release, breaking changes
- YY: minor feature change, new functions or classes 
- ZZ: patches, bug fixes, optimizations
*Pushing commits*
Create a new branch following "task/feature-name", "bug/bug-name" and so forth
A recommended workflow would be:
```
git stash
git checkout main
git pull
git checkout (your branch)
git stash pop
git rebase -i main
Fix merge conflicts
git push -—force-with-lease
```
Prior to merging a PR, be sure to squash your commits. One way to do this is to run `git rebase -i` and replace everything but the first commit message with `s` for squash as so:
```
pick abc123 Commit message 1
s def456 Commit message 2
s ghi789 Commit message 3
```

# Usage (depreciated)
___
`snode` is a Python package that contains all dependencies and code to read from snodes.

Files are organized into three directories:
1. One-off scripts go into `snode/scripts`
2. Reusable code that scripts can import go into `snode/snode`
3. Tests for reusable code go into `snode/tests`

To run any Python code:
1. Install Poetry by following https://python-poetry.org/docs/#installing-with-pipx
2. Enter the package you're using, e.g., `cd snode`
3. Install the Python dependencies the code needs, i.e., `poetry install`
4. Run a Python script, i.e., `poetry run python PATH/TO/SCRIPT.PY`
