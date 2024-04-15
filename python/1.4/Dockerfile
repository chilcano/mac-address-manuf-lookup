# Official Dockerfile used: https://hub.docker.com/_/python
FROM python:3.12-alpine

LABEL author="Roger Carhuatocto"
LABEL description="A MAC Address Manufacturer Lookup RESTful API"
LABEL version="1.4"

# Fixes CVE for pip
# https://scout.docker.com/v/CVE-2023-5752
RUN pip install --upgrade pip

# Fixes CVEs for openssl
# * https://scout.docker.com/v/CVE-2023-5678 
# * https://scout.docker.com/v/CVE-2023-5363
RUN apk add --update --no-cache openssl

COPY requirements.txt /
RUN pip install -r /requirements.txt

# Allocate the 5000/5443 to run a HTTP/HTTPS server
EXPOSE 5000 5443

COPY mac_manuf_wireshark_file.py /
COPY mac_manuf_table_def.py /
RUN python mac_manuf_wireshark_file.py
COPY mac_manuf_api_rest.py /
COPY mac_manuf_api_rest_https.py /

CMD [ "python", "./mac_manuf_api_rest_https.py" ]