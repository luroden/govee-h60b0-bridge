ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip bash
RUN pip3 install --no-cache-dir --break-system-packages paho-mqtt

COPY bridge.py /
COPY run.sh /
RUN chmod a+x /run.sh

ENTRYPOINT []
CMD [ "/run.sh" ]
