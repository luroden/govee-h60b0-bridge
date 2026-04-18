# Govee H60B0 Section Control - Home Assistant Add-on

Per-section control for the Govee H60B0 Uplighter Floor Lamp via local LAN. No cloud dependency.

The Govee H60B0 has three independent light sections that the official API doesn't expose for individual control. This add-on sends commands over LAN UDP, giving you full per-section control in Home Assistant.

## What it does

Creates three light entities in Home Assistant:


| Entity               | Controls                 | Features                              |
| -------------------- | ------------------------ | ------------------------------------- |
| **Uplighter Top**    | Lamp head (ripple light) | On/off, brightness, RGB color         |
| **Uplighter Side**   | RGBIC pillar light       | On/off, RGB color                     |
| **Uplighter Bottom** | Warm white base light    | On/off, brightness, color temperature |


## Installation

### As a Home Assistant Add-on

1. In Home Assistant, go to **Settings > Add-ons > Add-on Store**
2. Click the three dots (top right) > **Repositories**
3. Add this URL: `https://github.com/luroden/govee-h60b0-bridge`
4. Click **Reload**, then find "Govee H60B0 Section Control" in the store
5. Install, configure the lamp IP, and start

### Prerequisites

- Govee H60B0 lamp on the same network
- LAN control enabled in the Govee Home app (Device Settings > LAN Control)
- MQTT broker (Mosquitto) running in Home Assistant

### Configuration


| Option    | Default         | Description                   |
| --------- | --------------- | ----------------------------- |
| `lamp_ip` | `192.168.7.101` | IP address of your H60B0 lamp |


The add-on auto-discovers MQTT broker credentials from Home Assistant.

## How it works

The lamp communicates over UDP port 4003 using the Govee LAN protocol. Section control uses the `ptReal` command with BLE-format packets:

- **Section toggle**: `[0x33, 0x30, section_id, on/off]`
  - Section 1 = top, Section 2 = side, Section 3 = bottom
- **Bottom brightness**: `[0x33, 0x05, 0x2C, 0x03, 0x02, percent]`
- **Bottom color temp**: `[0x33, 0x05, 0x2C, 0x03, 0x01, kelvin_hi, kelvin_lo]`
- **Top color**: `[0x33, 0x05, 0x2C, 0x01, 0x01, R, G, B, 0, 0]`

## Standalone CLI

The `bridge.py` script can also be used outside Home Assistant:

```bash
pip install paho-mqtt
python bridge.py --lamp 192.168.7.101 --broker <mqtt_host> --user <user> --password <pass>
```

## License

MIT