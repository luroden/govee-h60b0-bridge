#!/usr/bin/env python3
"""Home Assistant MQTT bridge for Govee H60B0 Uplighter Floor Lamp.

Creates three HA light entities (top, side, bottom) via MQTT auto-discovery.
Listens for HA commands and sends them to the lamp over LAN UDP.
"""

import argparse
import base64
import json
import socket
import sys
import time

import paho.mqtt.client as mqtt

CONTROL_PORT = 4003
DEVICE_ID = "govee_h60b0_5488"
DEVICE_NAME = "Uplighter Floor Lamp"

SECTIONS = {
    "top": {
        "id": 1,
        "name": "Uplighter Top",
        "icon": "mdi:ceiling-light",
        "supports_color": True,
        "supports_temp": False,
    },
    "side": {
        "id": 2,
        "name": "Uplighter Side",
        "icon": "mdi:led-strip-variant",
        "supports_color": True,
        "supports_temp": False,
    },
    "bottom": {
        "id": 3,
        "name": "Uplighter Bottom",
        "icon": "mdi:floor-lamp",
        "supports_color": False,
        "supports_temp": True,
    },
}

section_state = {
    "top": {"on": True, "brightness": 100, "r": 255, "g": 255, "b": 255},
    "side": {"on": True, "brightness": 100, "r": 255, "g": 255, "b": 255},
    "bottom": {"on": True, "brightness": 100, "temp": 4000},
}


def make_pkt(pro_type, cmd_type, data):
    pkt = bytearray(20)
    pkt[0] = pro_type
    pkt[1] = cmd_type
    for i, b in enumerate(data):
        pkt[2 + i] = b
    checksum = pkt[0]
    for i in range(1, 19):
        checksum ^= pkt[i]
    pkt[19] = checksum
    return bytes(pkt)


def make_pos_bytes(bool_arr):
    padded = [False] * 16
    for i, v in enumerate(bool_arr[:16]):
        padded[i] = v
    s1 = "".join("1" if b else "0" for b in padded[:8])[::-1]
    s2 = "".join("1" if b else "0" for b in padded[8:])[::-1]
    return [int(s1, 2), int(s2, 2)]


def send_udp(ip, cmd, data):
    msg = json.dumps({"msg": {"cmd": cmd, "data": data}}).encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, (ip, CONTROL_PORT))
    sock.close()


def send_ptreal(ip, packets):
    cmds = [base64.b64encode(p).decode() for p in packets]
    send_udp(ip, "ptReal", {"command": cmds})


def lamp_section_toggle(ip, section_id, on):
    send_ptreal(ip, [make_pkt(0x33, 0x30, [section_id, 1 if on else 0])])


def lamp_bottom_brightness(ip, percent):
    send_ptreal(ip, [make_pkt(0x33, 0x05, [0x2C, 0x03, 0x02, max(1, min(100, percent))])])


def lamp_bottom_temp(ip, kelvin):
    kelvin = max(2700, min(6500, kelvin))
    send_ptreal(ip, [make_pkt(0x33, 0x05, [0x2C, 0x03, 0x01, (kelvin >> 8) & 0xFF, kelvin & 0xFF])])


def lamp_top_color(ip, r, g, b):
    send_ptreal(ip, [make_pkt(0x33, 0x05, [0x2C, 0x01, 0x01, r, g, b, 0, 0])])


def lamp_top_brightness(ip, percent):
    send_ptreal(ip, [make_pkt(0x33, 0x05, [0x2C, 0x01, 0x03, max(1, min(100, percent))])])


def lamp_side_color(ip, r, g, b):
    pos = make_pos_bytes([True] * 9)
    send_ptreal(ip, [make_pkt(0x33, 0x05, [0x2C, 0x04, 0x01, r, g, b, 0, 0] + pos)])


def kelvin_to_mired(k):
    return int(1000000 / k)


def mired_to_kelvin(m):
    return int(1000000 / m)


def publish_discovery(client):
    for section_key, cfg in SECTIONS.items():
        uid = f"{DEVICE_ID}_{section_key}"
        topic = f"homeassistant/light/{uid}/config"
        state_topic = f"govee/{DEVICE_ID}/{section_key}/state"
        cmd_topic = f"govee/{DEVICE_ID}/{section_key}/set"

        payload = {
            "name": cfg["name"],
            "unique_id": uid,
            "object_id": uid,
            "state_topic": state_topic,
            "command_topic": cmd_topic,
            "schema": "json",
            "brightness": True,
            "brightness_scale": 100,
            "icon": cfg["icon"],
            "device": {
                "identifiers": [DEVICE_ID],
                "name": DEVICE_NAME,
                "manufacturer": "Govee",
                "model": "H60B0",
            },
        }

        if cfg["supports_color"]:
            payload["supported_color_modes"] = ["rgb"]
            payload["color_mode"] = True

        if cfg["supports_temp"]:
            payload["supported_color_modes"] = ["color_temp"]
            payload["color_mode"] = True
            payload["min_mireds"] = kelvin_to_mired(6500)
            payload["max_mireds"] = kelvin_to_mired(2700)

        client.publish(topic, json.dumps(payload), qos=1, retain=True)
        print(f"Published discovery: {cfg['name']}")


def publish_state(client, section_key):
    state_topic = f"govee/{DEVICE_ID}/{section_key}/state"
    s = section_state[section_key]
    cfg = SECTIONS[section_key]

    payload = {
        "state": "ON" if s["on"] else "OFF",
        "brightness": s["brightness"],
    }

    if cfg["supports_color"]:
        payload["color_mode"] = "rgb"
        payload["color"] = {"r": s["r"], "g": s["g"], "b": s["b"]}

    if cfg["supports_temp"]:
        payload["color_mode"] = "color_temp"
        payload["color_temp"] = kelvin_to_mired(s["temp"])

    client.publish(state_topic, json.dumps(payload), qos=1, retain=True)


def handle_command(client, section_key, payload_str, lamp_ip):
    try:
        cmd = json.loads(payload_str)
    except json.JSONDecodeError:
        return

    s = section_state[section_key]
    cfg = SECTIONS[section_key]
    sid = cfg["id"]

    if "state" in cmd:
        on = cmd["state"] == "ON"
        s["on"] = on
        lamp_section_toggle(lamp_ip, sid, on)
        print(f"  {section_key}: {'ON' if on else 'OFF'}")

    if "brightness" in cmd:
        s["brightness"] = cmd["brightness"]
        if section_key == "bottom":
            lamp_bottom_brightness(lamp_ip, s["brightness"])
        elif section_key == "top":
            lamp_top_brightness(lamp_ip, s["brightness"])
        print(f"  {section_key}: brightness {s['brightness']}%")

    if "color" in cmd:
        s["r"] = cmd["color"].get("r", s["r"])
        s["g"] = cmd["color"].get("g", s["g"])
        s["b"] = cmd["color"].get("b", s["b"])
        if section_key == "top":
            lamp_top_color(lamp_ip, s["r"], s["g"], s["b"])
        elif section_key == "side":
            lamp_side_color(lamp_ip, s["r"], s["g"], s["b"])
        print(f"  {section_key}: color ({s['r']}, {s['g']}, {s['b']})")

    if "color_temp" in cmd:
        s["temp"] = mired_to_kelvin(cmd["color_temp"])
        lamp_bottom_temp(lamp_ip, s["temp"])
        print(f"  {section_key}: temp {s['temp']}K")

    publish_state(client, section_key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lamp", required=True)
    parser.add_argument("--broker", required=True)
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    lamp_ip = args.lamp

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected to MQTT broker at {args.broker}:{args.port}")
        publish_discovery(client)
        for section_key in SECTIONS:
            cmd_topic = f"govee/{DEVICE_ID}/{section_key}/set"
            client.subscribe(cmd_topic, qos=1)
            publish_state(client, section_key)
        print("Bridge running.")
        sys.stdout.flush()

    def on_message(client, userdata, msg):
        for section_key in SECTIONS:
            cmd_topic = f"govee/{DEVICE_ID}/{section_key}/set"
            if msg.topic == cmd_topic:
                handle_command(client, section_key, msg.payload.decode(), lamp_ip)
                return

    client = mqtt.Client(
        client_id=f"govee-h60b0-bridge",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    client.on_connect = on_connect
    client.on_message = on_message

    if args.user:
        client.username_pw_set(args.user, args.password)

    while True:
        try:
            client.connect(args.broker, args.port, keepalive=60)
            client.loop_forever()
        except Exception as e:
            print(f"Connection error: {e}. Retrying in 10s...")
            time.sleep(10)


if __name__ == "__main__":
    main()
