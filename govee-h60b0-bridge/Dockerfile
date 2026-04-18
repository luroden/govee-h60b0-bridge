ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip
RUN pip3 install --no-cache-dir --break-system-packages paho-mqtt

COPY bridge.py /
COPY run.sh /etc/services.d/govee-bridge/run
RUN chmod a+x /etc/services.d/govee-bridge/run
