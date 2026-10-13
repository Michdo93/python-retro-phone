# Python Retro Phone

A cross-platform Python application to read, map, and publish button inputs (Volume Up, Volume Down, Call/End) from a USB-C retro handset/phone using `hidapi` and MQTT.

## Features

* **Cross-Platform:** Works seamlessly on both Windows and Linux.
* **HID Packet Parsing:** Decodes raw USB input reports to filter out key press states.
* **Console Mapping (`retro_phone_mapping.py`):** Translates hardware inputs into clear English log output.
* **MQTT Integration (`retro_phone_mqtt.py`):** Broadcasts phone button presses directly to an MQTT broker (great for Home Assistant or smart home automation).

## Prerequisites

Make sure you have Python 3.8+ installed on your system.

### Install Dependencies

Install the required Python packages via pip:

```bash
pip install hidapi paho-mqtt
```

> **Linux Note:** On Linux distributions, you may need user permission rules (`udev` rules) or system packages for `hidapi` / `libusb` (`sudo apt-get install libhidapi-hidraw0`) to access USB devices without root privileges.

## Usage

1. Connect your USB-C retro phone to your computer.
2. **Run the raw diagnostic/mapping script:**
```bash
python retro_phone_mapping.py
```


3. **Run the MQTT publisher script:** (Make sure to update `MQTT_BROKER` inside the script to match your broker's address if not running locally)
```bash
python retro_phone_mqtt.py
```

## Hardware Mapping Reference

Based on standard USB HID Consumer Control packets captured from the device:

* `[3, 1, ...]` $\rightarrow$ **Volume Up**
* `[3, 2, ...]` $\rightarrow$ **Volume Down**
* `[3, 4, ...]` $\rightarrow$ **Call / End Call**
* `[3, 0, ...]` $\rightarrow$ **Key Released**

## License

Distributed under the MIT License. See `LICENSE` for more information.
