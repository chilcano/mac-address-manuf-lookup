# Docker MAC Address Manufacturer Lookup


This Docker container provides a Microservice (API Rest) to MAC Address Manufacturer resolution.

This Docker container is part of the "Everything generates Data: Capturing WIFI Anonymous Traffic using Raspberry Pi and WSO2 BAM" blog serie ([Part I](http://ow.ly/YcEf1), [Part II](http://ow.ly/YcEgz) & [Part III](http://ow.ly/YcEij)), but you can use it independently as part of other set of Docker containers.


This Docker Container will work in this scenario, as shown below:

![The MAC Address Manufacturer Lookup Docker Container](https://github.com/chilcano/docker-mac-address-manuf-lookup/blob/master/chilcano_docker_microservice_mac_address_manuf_lookup_2.png "The MAC Address Manufacturer Lookup Docker Container")


In this first version I have used Python and the next frameworks:


- `Flask` (http://flask.pocoo.org) is a microframework for Python based on Werkzeug and Jinja 2. I will use `Flask` to implement a mini-web application.
- `SQLAlchemy` (http://www.sqlalchemy.org/) is a Python SQL toolkit and ORM.
- `SQLite3` (https://www.sqlite.org) is a software library that implements a self-contained, serverless, zero-configuration, transactional SQL database engine.
- `pyOpenSSL` library to work with X.509 certificates. Required to start the embedded Webserver on HTTPS (TLS).
- `CORS extension for Flask` (https://flask-cors.readthedocs.org) useful to solve cross-domain Ajax request issues.


## Getting started


__1) Download the Wireshark Manufacturer file__


Download this Github repository.

```bash
$ git clone https://github.com/chilcano/docker-mac-address-manuf-lookup.git
$ cd docker-mac-address-manuf-lookup/python/1.0
```

Now, to download the Wireshark Manufacturer file.

```bash
$ python mac_manuf_wireshark_file.py

New Manuf file downloaded: manuf/20160220.073718.660_f8866ea289904350b5ff60ffda53edca_ok
Cleaned Manuf file created: manuf/20160220.073718.660_f8866ea289904350b5ff60ffda53edca_ok_cleaned
TAB Manuf file created: manuf/20160220.073718.660_f8866ea289904350b5ff60ffda53edca_ok_cleaned.tab
DB Manuf file created: manuf/20160220.073718.660_f8866ea289904350b5ff60ffda53edca_ok_cleaned.tab.db
( 'mac_address_manuf.db' was created and 28441 rows were loaded into 'MacAddressManuf' table. )

```


__2) Running the Python Microservice__


_2.1. over HTTP_


```bash
$ python mac_manuf_api_rest.py
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger pin code: 258-876-642

...
127.0.0.1 - - [20/Feb/2016 08:38:05] "GET /chilcano/api/manuf/00-50:Ca-ca-fe-ca-fe HTTP/1.1" 400 -
127.0.0.1 - - [20/Feb/2016 08:38:15] "GET /chilcano/api/manuf/00-50:Ca-ca-fe-ca HTTP/1.1" 200 -

```

And from other Terminal to call the API Rest.

```bash
$ curl -i http://127.0.0.1:5000/chilcano/api/manuf/00-50:Ca-ca-fe-ca-fe
HTTP/1.0 400 BAD REQUEST
Content-Type: application/json
Content-Length: 68
Server: Werkzeug/0.11.4 Python/2.7.11
Date: Sat, 20 Feb 2016 07:38:05 GMT

{
  "error": "The MAC Address '00-50:Ca-ca-fe-ca-fe' is malformed"
}


$ curl -i http://127.0.0.1:5000/chilcano/api/manuf/00-50:Ca-ca-fe-ca
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 93
Server: Werkzeug/0.11.4 Python/2.7.11
Date: Sat, 20 Feb 2016 07:38:15 GMT

{
  "mac": "00:50:CA",
  "manuf": "NetToNet",
  "manuf_desc": "# NET TO NET TECHNOLOGIES"
}
```


_2.2. Over HTTPS_


`pyOpenSSL` moodule was required to start the embedded Webserver on HTTPS (TLS).
To install it just run `pip install pyOpenSSL`.

Then, the Python App is running over HTTPS:

```bash
$ python mac_manuf_api_rest.py
 * Running on https://0.0.0.0:5443/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger pin code: 258-876-642
```

And calling the API:

```bash
$ curl -ik https://127.0.0.1:5443/chilcano/api/manuf/00-50:Ca-ca-fe-ca
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 93
Server: Werkzeug/0.11.4 Python/2.7.11
Date: Mon, 29 Feb 2016 15:58:21 GMT

{
  "mac": "00:50:CA",
  "manuf": "NetToNet",
  "manuf_desc": "# NET TO NET TECHNOLOGIES"
}
```


__3) Running everything into a Docker container__

_3.1. Clonning the Github repository and Building the container_

```bash
$ git clone https://github.com/chilcano/docker-mac-address-manuf-lookup.git

$ cd docker-mac-address-manuf-lookup

$ docker build --rm -t chilcano/mac-manuf-lookup-py:1.0 python/1.0/.
$ docker build --rm -t chilcano/mac-manuf-lookup-py:1.1 python/1.1/.
$ docker build --rm -t chilcano/mac-manuf-lookup-py:1.2 python/1.2/.
$ docker build --rm -t chilcano/mac-manuf-lookup-py:latest python/latest/.
```

_3.2. Pull from Docker Hub_

```bash
$ docker pull chilcano/mac-manuf-lookup-py
```


_3.3. Run and check the container_

```bash
$ docker run -dt --name=mac-manuf-py-12 -p 5000:5000/tcp -p 5443:5443/tcp chilcano/mac-manuf-lookup-py:1.2
$ docker run -dt --name=mac-manuf-py-latest -p 5000:5000/tcp -p 5443:5443/tcp chilcano/mac-manuf-lookup-py:latest

$ docker ps -a
CONTAINER ID        IMAGE                                 COMMAND                  CREATED             STATUS              PORTS                                            NAMES
0d5c2df25520        chilcano/mac-manuf-lookup-py:latest   "/bin/sh -c 'pytho..."   8 seconds ago       Up 6 seconds        0.0.0.0:5000->5000/tcp, 0.0.0.0:5443->5443/tcp   mac-manuf-py-latest
```

_3.4. Gettting SSH access to the Container to check if SQLite DB exists_

```bash
$ docker exec -ti mac-manuf-py-12 bash
$ docker exec -ti mac-manuf-py-latest bash
```


__4) Testing__


Calling the Microservice (API Rest).

```bash
$ curl -i http://localhost:5000/chilcano/api/manuf/00-50:Ca-ca-fe-ca
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 93
Server: Werkzeug/0.11.4 Python/2.7.11
Date: Sat, 20 Feb 2016 09:01:38 GMT

{
  "mac": "00:50:CA",
  "manuf": "NetToNet",
  "manuf_desc": "# NET TO NET TECHNOLOGIES"
}
```

If the embedded server was started on HTTPS, you could test it as shown below.

```bash
$ curl -ik https://localhost:5443/chilcano/api/manuf/00-50:Ca-ca-fe-ca
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 93
Server: Werkzeug/0.11.4 Python/2.7.11
Date: Mon, 29 Feb 2016 15:58:21 GMT

{
  "mac": "00:50:CA",
  "manuf": "NetToNet",
  "manuf_desc": "# NET TO NET TECHNOLOGIES"
}
```
