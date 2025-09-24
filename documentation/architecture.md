# Software History of Build Standards

The general hardware and software setup are diagrammed below according to the Build Standard.
> [!IMPORTANT]
> When cutting a release, the tagged release IS NOT the same as the build version. Please refer to the tagged version on GitHub for this repository to understand which Build Standard it corresponds to. As a reminder, the Build Standard determines the version of a SMesh Snode with regards to the hardware, software, and mechanical components it contains. **To rewind to the software/firmware of an earlier build standard, refer to the tagged versions of the software**

## Build Standard V1.0.0
[![alt text](<images/Software_V1.0.0.drawio.png>)](https://app.diagrams.net/#G1fAv-SE9_RxRZVmG-vSABV_piun6t15Nv#%7B%22pageId%22%3A%22qIs5qMzjnXvv36_teBx7%22%7D)

## Build Standard V2.0.0
[![alt text](<images/Software_V2.0.0.drawio.png>)](https://app.diagrams.net/#G1eQ8WNSo4UubmN6jEKkkb3obQR31KExnv#%7B%22pageId%22%3A%22qIs5qMzjnXvv36_teBx7%22%7D)

# Software Systems


## Raspberry Pi
We use the Raspberry Pi to save data transmitted from other SMesh nodes to its local SD card.

**Reason for use of Pi**

- TBD...

## Meshtastic

**Reason for use of Meshtastic**
The meshtastic is required to *understand* the data being spit out by our sensors (which the firmware handles) and transmit this data over LoRa (a low-power, long-range radio technology for IoT devices) via [Meshtastic's broadcast algorithm](https://meshtastic.org/docs/overview/mesh-algo/)

