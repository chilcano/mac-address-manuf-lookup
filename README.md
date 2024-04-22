# MAC Address Manufacturer Lookup


This is a Microservice and its RESTful API that implements a MAC Address Manufacturer resolution service. They are part of the "Everything generates Data: Capturing WIFI Anonymous Traffic using Raspberry Pi and WSO2 BAM" blog serie, but you can use it independently as part of other scenario.

"Everything generates Data: Capturing WIFI Anonymous Traffic using Raspberry Pi and WSO2 BAM" blog serie:
- [Capturing WIFI/802.11 traffic using Raspberry Pi, Kismet, Python and Thrift](https://holisticsecurity.io/2016/02/02/everything-generates-data-capturing-wifi-anonymous-traffic-raspberrypi-wso2-part-i)
- [Storing WIFI/802.11 traffic in a Database (NoSQL and RDBMS)](https://holisticsecurity.io/2016/02/04/everything-generates-data-capturing-wifi-anonymous-traffic-using-raspberry-pi-and-wso2-bam-part-ii)
- [Creating a Dashboard in WSO2 BAM showing captured WIFI/802.11 traffic in real-time](https://holisticsecurity.io/2016/02/09/everything-generates-data-capturing-wifi-anonymous-traffic-raspberrypi-wso2-part-iii)


MAC Address Manufacturer resolution service will work in this scenario as shown below:

![The MAC Address Manufacturer Lookup Docker Container](https://github.com/chilcano/mac-address-manuf-lookup/blob/master/chilcano_docker_microservice_mac_address_manuf_lookup_2.png "The MAC Address Manufacturer Lookup Docker Container")


## Running the Microservice locally

__1. Setup the Python environment__


Clone this Github repository.

```sh
$ git clone https://github.com/chilcano/mac-address-manuf-lookup.git
$ cd mac-address-manuf-lookup/src/python/
```

Set the python virtual environment and update the Python packages.

```sh
$ python3 -V
Python 3.11.4

$ pip -V
pip 23.0.1 from /usr/lib/python3/dist-packages/pip (python 3.11)

$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip -q install apiflask "apiflask[yaml]" flask-cors sqlalchemy pyopenssl unicodecsv
(.venv) $ pip freeze > requirements.txt 
```

I've used the next Python modelues and libraries:

- `apiflask` (https://apiflask.com) - It is a wrapper of `Flask` (https://flask.palletsprojects.com) only to deal with API and generates OpenAPI documentation. It will install `Flask`, `Jinja2`, `Werkzeug` and other Flask's funcions such as `Jsonify` used to serialize the response object into JSON format.
- `"apiflask[yaml]"` - Allow to generate the OpenAPI spec in YAML as well because it installs `PyYAML`.
- `flask-cors` (https://flask-cors.readthedocs.org) - It solves cross-domain issues.
- `sqlalchemy` (http://www.sqlalchemy.org/) is a Python SQL toolkit and ORM. It allows to work with `SQLite3` (https://www.sqlite.org) and doesn't require install extra modules.
- `pyopenssl` (https://www.pyopenssl.org) is a library to work with X.509 certificates. Required to start the embedded Webserver on HTTPS (TLS).
- `unicodecsv` (https://github.com/jdunck/python-unicodecsv) - CVS module with unicode support. It is used to import Wireshark Manufacturer File into SQLite3 DB.

If the packages in `requirements.txt` are updated and don't have any vulnerability, then you can install all of them running this:
```sh
(.venv) $ pip -q install -r requirements.txt 
```

__2. Download the Wireshark Manufacturer file__

To download the Wireshark Manufacturer file and import into a local SQLite3 DB, run this command:

```sh
(.venv) $ python mac_manuf_wireshark_file.py

New Manuf file downloaded: manuf/20240415.183121.853_20481313db0bbfbf9dd24648e2ed4ede_ok
Cleaned Manuf file created: manuf/20240415.183121.853_20481313db0bbfbf9dd24648e2ed4ede_ok_cleaned
TAB Manuf file created: manuf/20240415.183121.853_20481313db0bbfbf9dd24648e2ed4ede_ok_cleaned.tab
DB Manuf file created: manuf/20240415.183121.853_20481313db0bbfbf9dd24648e2ed4ede_ok_cleaned.tab.db
( 'mac_address_manuf.db' was created and 50751 rows were loaded into 'MacAddressManuf' table. )
```

__3. Run the Python MAC Address Lookup microservice__


The `pyOpenSSL` module is used to generate the self-signed TLS certificate and start an embedded webserver on HTTPS (TLS) to serve the API:

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

__4. Call the Python MAC Address Lookup microservice__

```sh
$ curl -ik https://localhost:5443/chilcano/api/manuf/00-50:Ca-ca-fe-ca

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

The API served on HTTP is available on `5000` port and can be launched running this:

```sh
(.venv) $ python mac_manuf_api_rest.py
```


## Running the Microservice from a Docker Container


__1. Build the container__

```sh
$ cd src/python/
$ docker build --rm -t chilcano/mac-manuf-lookup-py:test-01 .
$ docker images
```

__2. Run and check the container__

The microservice will be exposed on `6443` port.

```sh
$ docker run -dt --name=mac-manuf-lookup-py-test-01 -p 6443:5443/tcp chilcano/mac-manuf-lookup-py:test-01
$ docker ps
```

__3. Gettting SSH access to the Container and check the SQLite3 DB__

```sh
$ docker exec -ti mac-manuf-lookup-py-test-01 sh

/code $ ls -la
total 40
drwxr-xr-x    1 myuser   mygroup       4096 Apr 16 09:18 .
drwxr-xr-x    1 root     root          4096 Apr 16 09:18 ..
drwxr-xr-x    2 myuser   mygroup       4096 Apr 16 09:18 __pycache__
-rw-rw-r--    1 root     root          1915 Apr 15 14:28 mac_manuf_api_rest.py
-rw-rw-r--    1 root     root          2000 Apr 15 14:28 mac_manuf_api_rest_https.py
-rw-rw-r--    1 root     root           717 Apr 15 14:28 mac_manuf_table_def.py
-rw-rw-r--    1 root     root          5714 Apr 15 16:31 mac_manuf_wireshark_file.py
drwxr-xr-x    2 myuser   mygroup       4096 Apr 16 09:05 manuf
-rw-rw-r--    1 root     root           309 Apr 16 09:04 requirements.txt

/code $ ls -la manuf/
total 11320
drwxr-xr-x    2 myuser   mygroup       4096 Apr 16 09:05 .
drwxr-xr-x    1 myuser   mygroup       4096 Apr 16 09:18 ..
-rw-r--r--    1 myuser   mygroup    2745094 Apr 16 09:05 20240416.090520.805_20481313db0bbfbf9dd24648e2ed4ede_ok
-rw-r--r--    1 myuser   mygroup    2744635 Apr 16 09:05 20240416.090520.805_20481313db0bbfbf9dd24648e2ed4ede_ok_cleaned
-rw-r--r--    1 myuser   mygroup    2304121 Apr 16 09:05 20240416.090520.805_20481313db0bbfbf9dd24648e2ed4ede_ok_cleaned.tab
-rw-r--r--    1 myuser   mygroup    3780608 Apr 16 09:05 mac_address_manuf.db
```


__4. Call the Microservice running in the Docker container__

The API is exposed on HTTPS and available on `6443` port which is being forwarded from `5443`.
Then, to call the microservice on HTTPS, you could call it as shown below.

```sh
$ curl -ik https://localhost:6443/chilcano/api/manuf/00-50:Ca-ca-fe-ca

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

## Securing the Microservice and APIs


Some time ago I wrote about how to implement [The Minimum Viable Security on Kubernetised Applications](https://holisticsecurity.io/2020/03/08/minimum-viable-security-for-a-k8s-webapp-tls-everywhere-part1/) considering the Pareto Principle and the Shift-Left Testing approach. In this case, we are going to do the same for Microservices and RESTful APIs. 

### 1. Scanning vulnerable dependencies

We will publish the entire source code repository _if and only if_ is:

1. Sanitized - Not leaked secrets, tokens, PII, etc.
2. Free of vulnerabilities in application's dependencies such as internal and external libraries, component or modules used to build the application.
3. Free of misconfigurations in the Infrastructure as code such as Terraform, Ansible, Cloudformation, Dockerfile, Helm Charts, etc.
4. And if using Docker containers to package and ship your application, those Docker containers have not vulnerable OS libraries and misconfigurations. 


__Tools used__: 
  * Software Composition Analysis (SCA): [Trivy](https://trivy.dev)


#### 1.1. Running Trivy CLI locally


1. Install latest released binary of Trivy.
```sh
$ curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ~/.local/bin -d
$ trivy -v
Version: 0.49.0
```

2. Scan for vulns, secrets and misconfigs in local folder repo and send results to stdout.

```sh
$ trivy fs --format table --vuln-type os,library --scanners vuln,secret,misconfig --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL .
```

3. Scan for vulns, secrets and misconfigs in local container image and send results to stdout. We will use the locally built image `chilcano/mac-manuf-lookup-py:test-01` already created.

```sh
$ trivy image --format table --vuln-type os,library --scanners vuln,secret --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL chilcano/mac-manuf-lookup-py:test-01 
```

#### 1.2. Running Trivy CLI or Trivy Github Actions

You have 2 options, implement a Github Workflow to run Trivy CLI or use the Trivy Github Action.

- The Github Workflow created is [01-sca-app-deps-sec-trivy](01-sca-app-deps-sec-trivy.yaml). 
  * It is triggered by `PUSH` (commits) events and summary will be available in Github Actions Dashboard (https://github.com/chilcano/mac-address-manuf-lookup/actions/workflows/01-sca-app-deps-sec-trivy.yaml).
  * The reports (Junit, HTML, Sarif) generated are available as Github Artifacts and the Sarif report is imported into Github Security Dashboard and available here: https://github.com/chilcano/mac-address-manuf-lookup/security


### 2. Secure Static Analysis of Application and APIs


Again, we will publish  the entire source code repository _if and only if_ is:

1. Free of vulnerabilities in the source code. This means that the code must remove bad code practices, exploitable routines, mock code, sample code, etc.
2. Free of vulnerabilities in the API. This means that we should obtain the _OpenAPI_ spec to assess the API security according Security Best Practices.

__Tools used__: 
  * SAST for Applications: [SonarCloud](https://sonarcloud.io).
    - The Application Security Best Practices used are OWASP Top 10, CWE Top 25, tool's built-in rules, etc. 
    - See the report here: https://sonarcloud.io/summary/overall?id=chilcano_docker-mac-address-manuf-lookup

  * SAST for APIs: [Stoplight Spectral](https://stoplight.io/open-source/spectral).
    - The API Security Best Practices used: [OWASP API Security Top 10 2023](https://owasp.org/www-project-api-security/) and [Spectral OWASP Ruleset](https://github.com/stoplightio/spectral-owasp-ruleset)
    - The reports (Text, HTML, Sarif) generated are available as Github Artifacts and the Sarif report is imported into Github Security Dashboard and available here: https://github.com/chilcano/mac-address-manuf-lookup/security

