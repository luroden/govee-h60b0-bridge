#!/usr/bin/with-contenv bashio

LAMP_IP=$(bashio::config 'lamp_ip')

# Try to get MQTT from services, fall back to defaults
if bashio::services.available "mqtt"; then
    MQTT_HOST=$(bashio::services mqtt "host")
    MQTT_PORT=$(bashio::services mqtt "port")
    MQTT_USER=$(bashio::services mqtt "username")
    MQTT_PASS=$(bashio::services mqtt "password")
else
    MQTT_HOST="core-mosquitto"
    MQTT_PORT="1883"
    MQTT_USER=""
    MQTT_PASS=""
fi

bashio::log.info "Starting Govee H60B0 bridge"
bashio::log.info "Lamp IP: ${LAMP_IP}"
bashio::log.info "MQTT: ${MQTT_HOST}:${MQTT_PORT}"

ARGS="--lamp ${LAMP_IP} --broker ${MQTT_HOST} --port ${MQTT_PORT}"
if [ -n "${MQTT_USER}" ]; then
    ARGS="${ARGS} --user ${MQTT_USER} --password ${MQTT_PASS}"
fi

exec python3 /bridge.py ${ARGS}
