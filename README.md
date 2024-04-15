# Docker MAC Address Manufacturer Lookup


This is a Microservice and its RESTful API that implements a MAC Address Manufacturer resolution service. They are part of the "Everything generates Data: Capturing WIFI Anonymous Traffic using Raspberry Pi and WSO2 BAM" blog serie, but you can use it independently as part of other scenario.

"Everything generates Data: Capturing WIFI Anonymous Traffic using Raspberry Pi and WSO2 BAM" blog serie:
- [Capturing WIFI/802.11 traffic using Raspberry Pi, Kismet, Python and Thrift](https://holisticsecurity.io/2016/02/02/everything-generates-data-capturing-wifi-anonymous-traffic-raspberrypi-wso2-part-i)
- [Storing WIFI/802.11 traffic in a Database (NoSQL and RDBMS)](https://holisticsecurity.io/2016/02/04/everything-generates-data-capturing-wifi-anonymous-traffic-using-raspberry-pi-and-wso2-bam-part-ii)
- [Creating a Dashboard in WSO2 BAM showing captured WIFI/802.11 traffic in real-time](https://holisticsecurity.io/2016/02/09/everything-generates-data-capturing-wifi-anonymous-traffic-raspberrypi-wso2-part-iii)


MAC Address Manufacturer resolution service will work in this scenario as shown below:

![The MAC Address Manufacturer Lookup Docker Container](https://github.com/chilcano/docker-mac-address-manuf-lookup/blob/master/chilcano_docker_microservice_mac_address_manuf_lookup_2.png "The MAC Address Manufacturer Lookup Docker Container")


In this version I've used Python and the next frameworks:


- `Flask` (http://flask.pocoo.org) is a microframework for Python based on Werkzeug and Jinja 2. I will use `Flask` to implement a mini-web application.
- `SQLAlchemy` (http://www.sqlalchemy.org/) is a Python SQL toolkit and ORM.
- `SQLite3` (https://www.sqlite.org) is a software library that implements a self-contained, serverless, zero-configuration, transactional SQL database engine.
- `pyOpenSSL` library to work with X.509 certificates. Required to start the embedded Webserver on HTTPS (TLS).
- `CORS extension for Flask` (https://flask-cors.readthedocs.org) useful to solve cross-domain Ajax request issues.


## Getting started

### Preparing the Microservice and its RESTful API

__1. Download the Wireshark Manufacturer file__


Clone this Github repository.

```sh
$ git clone https://github.com/chilcano/docker-mac-address-manuf-lookup.git
$ cd docker-mac-address-manuf-lookup/python/latest
```

Set the python virtual environment and update the Python packages.

```sh
$ python3 -V
Python 3.11.4

$ pip -V
pip 23.0.1 from /home/chilcano/repos/me/docker-mac-address-manuf-lookup/python/1.4/.venv/lib/python3.11/site-packages/pip (python 3.11)

$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip -q install -r requirements.txt

(.venv) $ pip list --outdated
Package      Version Latest Type
------------ ------- ------ -----
click        7.1.2   8.1.7  wheel
Flask        1.1.4   3.0.3  wheel
Flask-Admin  1.5.8   1.6.1  wheel
gunicorn     19.10.0 21.2.0 wheel
itsdangerous 1.1.0   2.1.2  wheel
Jinja2       2.11.3  3.1.3  wheel
pip          23.0.1  24.0   wheel
setuptools   66.1.1  69.5.1 wheel
Werkzeug     1.0.1   3.0.2  wheel

(.venv) $ pip -q install -U pip
(.venv) $ pip -q uninstall click Flask Flask-Admin gunicorn itsdangerous Jinja2 setuptools Werkzeug MarkupSafe

(.venv) $ pip -q install click Flask Flask-Admin gunicorn itsdangerous Jinja2 setuptools Werkzeug

(.venv) $ pip freeze > requirements.txt 
```

If the main packages are the latest, then uninstall and install the outdated packages, only run this:
```sh
(.venv) $ pip -q install -r requirements.txt 
```

Now, to download the Wireshark Manufacturer file.

```sh
(.venv) $ python mac_manuf_wireshark_file.py
New Manuf file downloaded: manuf/20240415.183121.853_20481313db0bbfbf9dd24648e2ed4ede_ok
Cleaned Manuf file created: manuf/20240415.183121.853_20481313db0bbfbf9dd24648e2ed4ede_ok_cleaned
TAB Manuf file created: manuf/20240415.183121.853_20481313db0bbfbf9dd24648e2ed4ede_ok_cleaned.tab
DB Manuf file created: manuf/20240415.183121.853_20481313db0bbfbf9dd24648e2ed4ede_ok_cleaned.tab.db
( 'mac_address_manuf.db' was created and 50751 rows were loaded into 'MacAddressManuf' table. )
```

__2. Running the Python Microservice__


_Running over HTTP_

```sh
(.venv) $ python mac_manuf_api_rest.py

 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger pin code: 258-876-642

127.0.0.1 - - [15/Apr/2024 19:17:05] "GET /chilcano/api/manuf/00-50:Ca-ca-fe-ca-fe HTTP/1.1" 400 -
127.0.0.1 - - [15/Apr/2024 19:17:30] "GET /chilcano/api/manuf/00-50:Ca-ca-fe-ca HTTP/1.1" 200 -
```

And from other Terminal to call the RESTful API.

```sh
$ curl -i http://127.0.0.1:5000/chilcano/api/manuf/00-50:Ca-ca-fe-ca-fe

HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.0.2 Python/3.11.4
Date: Mon, 15 Apr 2024 17:17:05 GMT
Content-Type: application/json
Content-Length: 69
Access-Control-Allow-Origin: *
Connection: close

{
  "error": "The MAC Address '00-50:Ca-ca-fe-ca-fe' is malformed"
}

$ curl -i http://127.0.0.1:5000/chilcano/api/manuf/00-50:Ca-ca-fe-ca

HTTP/1.1 200 OK
Server: Werkzeug/3.0.2 Python/3.11.4
Date: Mon, 15 Apr 2024 17:17:30 GMT
Content-Type: application/json
Content-Length: 70
Access-Control-Allow-Origin: *
Connection: close

{
  "mac": "00:50:CA",
  "manuf": "DZS",
  "manuf_desc": "DZS Inc."
}

```

_Running over HTTPS_

The `pyOpenSSL` moodule is required to start the embedded Webserver on HTTPS (TLS), to install it just run `pip install pyOpenSSL`.
Then, the Python App will run over HTTPS:

```sh
(.venv) ± python mac_manuf_api_rest_https.py 

 * Serving Flask app 'mac_manuf_api_rest_https'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on https://127.0.0.1:5443
 * Running on https://192.168.1.153:5443
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 135-791-615

127.0.0.1 - - [15/Apr/2024 19:21:33] "GET /chilcano/api/manuf/00-50:Ca-ca-fe-ca HTTP/1.1" 200 -

```

And calling the API:

```sh
$ curl -ik https://127.0.0.1:5443/chilcano/api/manuf/00-50:Ca-ca-fe-ca

HTTP/1.1 200 OK
Server: Werkzeug/3.0.2 Python/3.11.4
Date: Mon, 15 Apr 2024 17:21:33 GMT
Content-Type: application/json
Content-Length: 70
Access-Control-Allow-Origin: *
Connection: close

{
  "mac": "00:50:CA",
  "manuf": "DZS",
  "manuf_desc": "DZS Inc."
}
```

### Running the Microservice and its RESTful API into a Docker Container

__1. Clone the Github repository and build the container__

```sh
$ git clone https://github.com/chilcano/docker-mac-address-manuf-lookup.git

$ cd docker-mac-address-manuf-lookup

$ docker build --rm -t chilcano/mac-manuf-lookup-py:1.4 python/1.4/.
$ docker build --rm -t chilcano/mac-manuf-lookup-py:latest python/latest/.
```

__2. Pull from Docker Hub__

```sh
$ docker pull chilcano/mac-manuf-lookup-py
```

__3. Run and check the container__

```sh
$ docker run -dt --name=mac-manuf-py-14 -p 5000:5000/tcp -p 6443:5443/tcp chilcano/mac-manuf-lookup-py:1.4
$ docker run -dt --name=mac-manuf-py-latest -p 5443:5443/tcp chilcano/mac-manuf-lookup-py:latest

$ docker ps

CONTAINER ID   IMAGE                                 COMMAND                  CREATED          STATUS          PORTS                                                                                  NAMES
090e66be2427   chilcano/mac-manuf-lookup-py:1.4      "python ./mac_manuf_…"   11 seconds ago   Up 10 seconds   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp, 0.0.0.0:6443->5443/tcp, :::6443->5443/tcp   mac-manuf-py-14
96b12ce87cdc   chilcano/mac-manuf-lookup-py:latest   "python ./mac_manuf_…"   9 minutes ago    Up 9 minutes    5000/tcp, 0.0.0.0:5443->5443/tcp, :::5443->5443/tcp                                    mac-manuf-py-latest

```

__4. Gettting SSH access to the Container to check if SQLite DB exists__

```sh
$ docker exec -ti mac-manuf-py-14 bash
$ docker exec -ti mac-manuf-py-latest bash
```


### Testing

Since I'm only running the API on HTTPS enabled, then the available port will be `5443`. The port `5000` (HTTP) will be not available.
Then, calling the Microservice through its RESTful API on HTTPS, you could call it as shown below.

```sh
$ curl -ik https://localhost:5443/chilcano/api/manuf/00-50:Ca-ca-fe-ca

HTTP/1.1 200 OK
Server: Werkzeug/3.0.2 Python/3.12.3
Date: Mon, 15 Apr 2024 18:31:23 GMT
Content-Type: application/json
Content-Length: 70
Access-Control-Allow-Origin: *
Connection: close

{
  "mac": "00:50:CA",
  "manuf": "DZS",
  "manuf_desc": "DZS Inc."
}
```
