#!/usr/bin/with-contenv bashio

LAMP_IP=$(bashio::config 'lamp_ip')
MQTT_HOST=$(bashio::services mqtt "host")
MQTT_PORT=$(bashio::services mqtt "port")
MQTT_USER=$(bashio::services mqtt "username")
MQTT_PASS=$(bashio::services mqtt "password")

bashio::log.info "Starting Govee H60B0 bridge"
bashio::log.info "Lamp IP: ${LAMP_IP}"
bashio::log.info "MQTT: ${MQTT_USER}@${MQTT_HOST}:${MQTT_PORT}"

exec python3 /bridge.py \
    --lamp "${LAMP_IP}" \
    --broker "${MQTT_HOST}" \
    --port "${MQTT_PORT}" \
    --user "${MQTT_USER}" \
    --password "${MQTT_PASS}"
