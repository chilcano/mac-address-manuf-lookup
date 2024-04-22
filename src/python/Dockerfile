# Official Dockerfile used: https://hub.docker.com/_/python
FROM python:3.12-alpine

# Adds metadata to image
LABEL author="Roger Carhuatocto"
LABEL description="A MAC Address Manufacturer Lookup RESTful API"
LABEL blog="https://holisticsecurity.io"
LABEL post="https://holisticsecurity.wordpress.com/2016/02/02/everything-generates-data-capturing-wifi-anonymous-traffic-raspberrypi-wso2-part-i/"
LABEL version="1.4"

# Fixes CVE for pip
# https://scout.docker.com/v/CVE-2023-5752
RUN pip install --upgrade pip

# Fixes CVEs for openssl
# * https://scout.docker.com/v/CVE-2023-5678 
# * https://scout.docker.com/v/CVE-2023-5363
RUN apk add --update --no-cache openssl

# Create and switch to workdir
WORKDIR /code

RUN addgroup -S mygroup && adduser -S myuser -G mygroup -s /sbin/nologin
RUN chown -R myuser:mygroup /code
USER myuser

COPY requirements.txt .
RUN pip install -r requirements.txt

# Allocate the 5443 to run a HTTP/HTTPS server
EXPOSE 5443

COPY mac_manuf_wireshark_file.py .
COPY mac_manuf_table_def.py .
COPY mac_manuf_api_rest.py .
COPY mac_manuf_api_rest_https.py .

# Download Manuf file and create DB in build-time
RUN python ./mac_manuf_wireshark_file.py

# Launch the HTTPS API on 5443 port
CMD [ "python", "./mac_manuf_api_rest_https.py" ]