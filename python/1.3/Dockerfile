# Official Dockerfile used: https://hub.docker.com/_/python
FROM python:3.7-alpine

LABEL author="Roger Carhuatocto"
LABEL description="Dockerfile to MAC Address Manufacturer Lookup container"
LABEL version="1.3"

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY src/ /app
WORKDIR /appCMD ["gunicorn", "-w 4", "main:app"]

# Allocate the 5000/5443 to run a HTTP/HTTPS server
EXPOSE 5000 5443

COPY mac_manuf_wireshark_file.py /
COPY mac_manuf_table_def.py /
RUN python mac_manuf_wireshark_file.py
COPY mac_manuf_api_rest.py /
COPY mac_manuf_api_rest_https.py /
COPY mac_manuf_run.sh /
RUN ["chmod", "+x", "/mac_manuf_run.sh"]

CMD ./mac_manuf_run.sh
