#!/bin/bash
set -e

# Read add-on options
OPTIONS_FILE="/data/options.json"
if [ -f "$OPTIONS_FILE" ]; then
    LAMP_IP=$(python3 -c "import json; print(json.load(open('$OPTIONS_FILE')).get('lamp_ip', '192.168.7.101'))")
else
    LAMP_IP="192.168.7.101"
fi

# Try to get MQTT from supervisor API
if [ -n "$SUPERVISOR_TOKEN" ]; then
    MQTT_INFO=$(curl -s -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/services/mqtt 2>/dev/null || echo "")
    if echo "$MQTT_INFO" | python3 -c "import sys,json; json.load(sys.stdin)['data']" 2>/dev/null; then
        MQTT_HOST=$(echo "$MQTT_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['host'])")
        MQTT_PORT=$(echo "$MQTT_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['port'])")
        MQTT_USER=$(echo "$MQTT_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['username'])")
        MQTT_PASS=$(echo "$MQTT_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['password'])")
    fi
fi

# Fallback
MQTT_HOST="${MQTT_HOST:-core-mosquitto}"
MQTT_PORT="${MQTT_PORT:-1883}"

echo "Starting Govee H60B0 bridge"
echo "Lamp IP: ${LAMP_IP}"
echo "MQTT: ${MQTT_HOST}:${MQTT_PORT}"

ARGS="--lamp ${LAMP_IP} --broker ${MQTT_HOST} --port ${MQTT_PORT}"
if [ -n "${MQTT_USER}" ]; then
    ARGS="${ARGS} --user ${MQTT_USER} --password ${MQTT_PASS}"
fi

exec python3 /bridge.py ${ARGS}
