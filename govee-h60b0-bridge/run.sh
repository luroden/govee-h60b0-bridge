#!/usr/bin/with-contenv bashio

LAMP_IP=$(bashio::config 'lamp_ip')
MQTT_HOST=$(bashio::config 'mqtt_host')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_USER=$(bashio::config 'mqtt_user')
MQTT_PASS=$(bashio::config 'mqtt_pass')

bashio::log.info "Starting Govee H60B0 bridge"
bashio::log.info "Lamp: ${LAMP_IP}"
bashio::log.info "MQTT: ${MQTT_HOST}:${MQTT_PORT}"

ARGS="--lamp ${LAMP_IP} --broker ${MQTT_HOST} --port ${MQTT_PORT}"
if [ -n "${MQTT_USER}" ]; then
    ARGS="${ARGS} --user ${MQTT_USER} --password ${MQTT_PASS}"
fi

exec python3 /bridge.py ${ARGS}
