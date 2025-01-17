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

I've used the next Python libraries:

- `apiflask` (https://apiflask.com) - It is a wrapper of `Flask` (https://flask.palletsprojects.com) only to deal with API and generates OpenAPI documentation. It will install `Flask`, `Jinja2`, `Werkzeug` and other Flask's funcions such as `Jsonify`, used to serialize the response object into JSON format.
- `"apiflask[yaml]"` - Allow to generate the OpenAPI spec in YAML as well because it installs `PyYAML`.
- `flask-cors` (https://flask-cors.readthedocs.org) - It solves cross-domain issues.
- `sqlalchemy` (http://www.sqlalchemy.org/) is a Python SQL toolkit and ORM. It allows to work with `SQLite3` (https://www.sqlite.org) and doesn't require install extra modules.
- `pyopenssl` (https://www.pyopenssl.org) is a library to work with X.509 certificates. Required to start the embedded Webserver on HTTPS (TLS).
- `unicodecsv` (https://github.com/jdunck/python-unicodecsv) - CVS module with unicode support. It is used to import Wireshark Manufacturer File into SQLite3 DB.

The [01-sca-app-deps-dec-trivy Github Action](https://github.com/chilcano/mac-address-manuf-lookup/actions/workflows/01-sca-app-deps-sec-trivy.yaml) or running Trivy from terminal, both will detect vulnerabilities in our dependencies.
Fix them and update the `requirements.txt` file. For example, follow these commands:
```sh
# run trivy
$ trivy fs --format table --vuln-type os,library --scanners vuln,secret,misconfig --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL . 

# trivy will detect 3 vulnerable dependencies, so remove them
$ pip -q uninstall Werkzeug Jinja2 Flask-Cors

# reinstall recommended fixed dependencies
$ pip -q install Werkzeug==3.0.3 Jinja2==3.1.4 Flask-Cors==4.0.1

# update requeriments.txt file
$ pip freeze > requirements.txt 
```

We should do the same with Snyk and scan for vulnerabilities in the source code. If Snyk is installed and configured in VSCode, then it will detect some vulnerabilities in the code and dependencies:
```sh
$ pip uninstall cryptography
$ pip install cryptography==42.0.6
$ pip freeze > requirements.txt 
```


Next command is optional, only execute it if you want to install all packages and transitive dependencies automatically.
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
$ cd mac-address-manuf-lookup/
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

### 1. Scanning for vulnerable dependencies

We will publish the entire source code repository _if and only if_ is:

1. Sanitized - Not leaked secrets, tokens, PII, etc.
2. Free of vulnerabilities in application's dependencies such as internal and external libraries, component or modules used to build the application.
3. Free of misconfigurations in the Infrastructure as code such as Terraform, Ansible, Cloudformation, Dockerfile, Helm Charts, etc.
4. And if using Docker containers to package and ship your application, those Docker containers have not vulnerable OS libraries and misconfigurations. 

To accomplish that, I will use Trivy.

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

![](01_sca_trivy_repo.png)

3. Scan for vulns, secrets and misconfigs in local container image and send results to stdout. We will use the locally built image `chilcano/mac-manuf-lookup-py:test-01` already created.

```sh
$ trivy image --format table --vuln-type os,library --scanners vuln,secret --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL chilcano/mac-manuf-lookup-py:test-01 
```

![](02_sca_trivy_docker.png)


#### 1.2. Running Trivy CLI or Trivy Github Actions in automated way

You have 2 options, implement a Github Workflow to run Trivy CLI or use the Trivy Github Action.

- The Github Workflow created is [01-sca-app-deps-sec-trivy](.github/workflows/01-sca-app-deps-sec-trivy.yaml).
  * It is triggered by `PUSH` (commits) events and summary will be available in Github Actions Dashboard (https://github.com/chilcano/mac-address-manuf-lookup/actions/workflows/01-sca-app-deps-sec-trivy.yaml).
  * The reports (Json, Junit, HTML, Sarif) generated are available as Github Artifacts and can be downloaded from Github Actions Dashboard.
  * The Junit report has been generated to be imported into Github Action Summary view and as Annotations. In this case the Github Action used is [EnricoMi/publish-unit-test-result-action](https://github.com/EnricoMi/publish-unit-test-result-action).
  * The Sarif report is imported into Github and the report is available from Github Security Dashboard: https://github.com/chilcano/mac-address-manuf-lookup/security
  * The Json report has been transformed to SonarQube format. The SonarQube report has not been imported yet to SonarQube or SonarCloud instance.
  * The [01-sca-app-deps-sec-trivy](.github/workflows/01-sca-app-deps-sec-trivy.yaml) will build a Docker container. It will be scanned for vulnerabilities, once completed, it will be uploaded to Github Container Register (https://ghcr.io/chilcano/mac-address-manuf-lookup) and will be available only the Repo Owner.

![](03_sca_trivy_repo_github_action.png)


### 2. Secure Static Analysis of Application and APIs


Again, we will publish  the entire source code repository _if and only if_ is:

1. Free of vulnerabilities in the source code. This means that the code must remove bad code practices, exploitable routines, mock code, sample code, etc.
2. Free of vulnerabilities in the API. This means that we should obtain the _OpenAPI_ spec to assess the API security according Security Best Practices.

__Tools used__: 
  * SAST for Applications: [SonarCloud](https://sonarcloud.io).
    - The Application Security Best Practices used are OWASP Top 10, CWE Top 25, tool's built-in rules, etc. 
    - See the report here: https://sonarcloud.io/summary/overall?id=chilcano_mac-address-manuf-lookup

  * SAST for APIs: [Stoplight Spectral](https://stoplight.io/open-source/spectral).
    - The API Security Best Practices used: [OWASP API Security Top 10 2023](https://owasp.org/www-project-api-security/) and [Spectral OWASP Ruleset](https://github.com/stoplightio/spectral-owasp-ruleset).
    - The reports (Text, HTML, Sarif) generated are available as Github Artifacts and can be downloaded from Github Actions Dashboard.
    - The Sarif report is imported into Github Security Dashboard and available here: https://github.com/chilcano/mac-address-manuf-lookup/security

#### 2.1. Running Stoplight Spectral CLI locally

1. Install Stoplight Spectral and Spectral-Sarif converter

```sh
$ node -v
v20.11.0

$ npm -v
10.5.2

$ npm install @stoplight/spectral-cli
$ npm install @stoplight/spectral-owasp-ruleset

$ echo 'extends: ["@stoplight/spectral-owasp-ruleset"]' > .spectral_owasp.yaml
```

2. Generate the OpenAPI spec file.

```sh
$ cd src/python/

$ python3 -V
Python 3.11.4

$ pip -V
pip 23.0.1 from /usr/lib/python3/dist-packages/pip (python 3.11)

$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip -q install -r requirements.txt 

$ flask --app mac_manuf_api_rest_https.py spec > openapi.yaml
```

3. Run Stoplight Spectral CLI.

```sh
$ cd ../../
$ npx spectral lint src/python/openapi.yaml -r .spectral_owasp.yaml \
  -f stylish -o.stylish "<stdout>" \
  -f json -o.json report_spectral_owasp.json
```

![](04_sast_spectral_apisec.png)

4. Convert Spectral Json report to Sarif

```sh
$ git clone --branch fix-level-attribute https://github.com/chilcano/spectral-sarif
$ cd spectral-sarif
$ npm install
$ npm run build
$ npx spectral-sarif --version
0.0.18

$ npx spectral-sarif ../report_spectral_owasp.json -o ../report_spectral_owasp.sarif -r ${PWD%/*}/
```

#### 2.2. Running Stoplight Spectral CLI in an automated way


You have to implement a Github Workflow to run Spectral CLI.

- The Github Workflow created is [02-sast-api-sec-spectral-owasp](.github/workflows/02-sast-api-sec-spectral-owasp.yaml).
  * It is triggered by `PUSH` (commits) events and summary will be available in Github Actions Dashboard (https://github.com/chilcano/mac-address-manuf-lookup/actions/workflows/02-sast-api-sec-spectral-owasp.yaml).
  * The reports (Json, HTML, Sarif) generated are available as Github Artifacts and can be downloaded from Github Actions Dashboard.
  * The Json report has been transformed to Sarif format, it has been imported into Github to be available from Github Security Dashboard (https://github.com/chilcano/mac-address-manuf-lookup/security).

![](05_sast_spectral_apisec_gha_artifact_html.png)
![](05_sast_spectral_apisec_gha_github_security.png)
![](05_sast_spectral_apisec_gha_github_security_code_view.png)


## Handling found vulnerabilities in the Microservice and APIs

First thing to do is download and review the reports generated by:
1. Trivy (SCA: vulnerabilities in the dependencies, configuration, Dockerfile in the Repository and Docker image, leaked secrets, etc.)
  * Remove vulnerable Python libraries or modules from [src/python/requirements.txt](src/python/requirements.txt).
  * Use a secure Docker image, remove vulnerable OS packages and update the [./Dockerfile](./Dockerfile) accordingly.
2. Stoplight Spectral (SAST for APIs: OWASP API Security Top 10)
  * Update the Python API to fix OWASP issues in the [./openapi.yaml](./openapi.yaml) file. Once updated the Python code, the `openapi.yaml` file must be generated.
  * You can follow the Stoplight API Stylebook for OWASP in order to fix the issues: https://apistylebook.stoplight.io/docs/owasp-top-10-2023
3. SonarQube (SAST for Application: vulnerable code)
  * Same recommendations detailed in point 2.

