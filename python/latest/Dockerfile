# Dockerfile to MAC Address Manufacturer Lookup container.
#
# $ git clone https://github.com/chilcano/docker-mac-address-manuf-lookup.git
# $ cd docker-mac-address-manuf-lookup
# $ docker build --rm -t chilcano/mac-manuf-py:latest python/latest/.
# $ docker run -dt --name=mac-manuf-py-latest -p 5000:5000/tcp -p 5443:5443/tcp chilcano/mac-manuf-py:latest
# $ docker exec -ti mac-manuf-py-latest bash
# $ curl -ik https://127.0.0.1:5443/chilcano/api/manuf/00-50:Ca-ca-fe-ca
# $ curl -ik https://192.168.99.100:5443/chilcano/api/manuf/00-50:Ca-ca-fe-ca
#

# Official Dockerfile used: https://hub.docker.com/_/python
FROM python:2.7

MAINTAINER Roger CARHUATOCTO <chilcano at intix dot info>

RUN pip install --upgrade pip
RUN pip install unicodecsv
RUN pip install Flask
RUN pip install sqlalchemy
RUN pip install pyOpenSSL
RUN pip install -U flask-cors

# Allocate the 5000/5443 to run a HTTP/HTTPS server
EXPOSE 5000 5443

COPY mac_manuf_wireshark_file.py /
COPY mac_manuf_table_def.py /
COPY mac_manuf_api_rest.py /

RUN python mac_manuf_wireshark_file.py
CMD python mac_manuf_api_rest.py
