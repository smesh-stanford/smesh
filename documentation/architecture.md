# Software History of Build Standards

The general hardware and software setup are diagrammed below according to the Build Standard.
> [!IMPORTANT]
> When cutting a release, the tagged release IS NOT the same as the build version. Please refer to the tagged version on GitHub for this repository to understand which Build Standard it corresponds to. As a reminder, the Build Standard determines the version of a SMesh Snode with regards to the hardware, software, and mechanical components it contains. **To rewind to the software/firmware of an earlier build standard, refer to the tagged versions of the software**

## Build Standard V1.0.0
Note: The Meshtastic connected to the Pi is how we receive device metrics via USB but this is NOT receiving the sensor data
Note: there is a logger node that is in charge of the Pi + meshtastic
    - SNode has sensors, this has no RTC
    - RTC is used on reception of a message for logging...

Transmission:
- time between transmission and being logged is not always consistent. 
- we need the RTC bc.: if the pi goes off we can lose track of the time, we also need to know the real time of when the sample was *acurrately*
- as of right now, we only use the RTC on receive otherwise the meshtastics need to be equipped with more hardware 

Note: this is where we were saving data to a CSV locally... meshtastic --> CPU
[![alt text](<images/Software_V1.0.0.drawio.png>)](https://app.diagrams.net/#G1fAv-SE9_RxRZVmG-vSABV_piun6t15Nv#%7B%22pageId%22%3A%22qIs5qMzjnXvv36_teBx7%22%7D)

## Build Standard V2.0.0
[![alt text](<images/Software_V2.0.0.drawio.png>)](https://app.diagrams.net/#G1eQ8WNSo4UubmN6jEKkkb3obQR31KExnv#%7B%22pageId%22%3A%22qIs5qMzjnXvv36_teBx7%22%7D)

# Software Systems


## Raspberry Pi

Setup:
- Meshtastic <--> (Python API) Raspberry Pi
- 
We use the Raspberry Pi to save data transmitted from other SMesh nodes to its local SD card.

Note to self...: rpi_log_script.py this is how we receive a packet...
**Reason for use of Pi**

- TBD...

## Meshtastic

### Communication
- **Flood style**: broadcast the packet to everyone in the network and have the packet with the:
    - Sender ID (this is a hexcode, each meshtastic's last 4 digits are written on the box)
    - Hop Limit: used to decrement and track how many hops this has been set to initially
    - Hop start: Remains the same between each hop, this is like "bookkeeping" for the original hop limit
        - So hop start - hop limit = # hops we have already made
- The phone app talks over bluetooth to the Meshtastic. This requires an ACK. This happens over the meshtastic network. It will send an ACK only after the phone message has travelled to the desired node through whatever path it takes
**Reason for use of Meshtastic**
The meshtastic is required to *understand* the data being spit out by our sensors (which the firmware handles) and transmit this data over LoRa (a low-power, long-range radio technology for IoT devices) via [Meshtastic's broadcast algorithm](https://meshtastic.org/docs/overview/mesh-algo/)

### CRC
- This is something enabled through LoRa, but this doesn't have "full coverage". Corrupted packets are incredibly uncommon, but aren't impossible
- This would be configured on chip for the meshtastic