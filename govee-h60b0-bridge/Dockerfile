ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip
RUN pip3 install --no-cache-dir --break-system-packages paho-mqtt

COPY run.sh /
COPY bridge.py /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
