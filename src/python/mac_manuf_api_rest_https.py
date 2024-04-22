#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# file name: mac_manuf_api_rest_https.py
#

import os, re
from flask import jsonify
from flask_cors import CORS
from apiflask import APIFlask, Schema, abort, HTTPError
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from mac_manuf_table_def import MacAddressManuf

ROOT_DIR = "manuf"
FINAL_MANUF_DB_FILENAME = "mac_address_manuf.db"
MAC_FORMATS_SUPPORTED = "Examples of MAC addresses supported: 09-aB:d1:FF-99-cC, f1:00-D1:CA-a9:01"

engine = create_engine("sqlite:///" + os.path.join(ROOT_DIR, FINAL_MANUF_DB_FILENAME))
Session = sessionmaker(bind=engine)

app = APIFlask(__name__, title='MAC Manufacturer Lookup RESTful API', version='1.4')
app.config['SPEC_FORMAT'] = 'yaml'
app.config['DESCRIPTION'] = """

A MAC Manufacturer Lookup RESTful API.

This service, download the Manufacturer file from Wireshark Website running `python mac_manuf_wireshark_file.py` manually or when building the `Dockerfile`.

Example:

   `curl -ik https://localhost:5443/chilcano/api/manuf/00:50:5a:e5:6e:cf`

"""

cors = CORS(app, resources={r"/chilcano/api/*": {"origins": "*"}})

class ManufacturerIn(Schema):
    mac = String(
        required=True, 
        validate=Length(0, 8),
        metadata={'title': 'MAC Address', 'description': 'The MAC address.'}
    )
    manuf = String(
        required=True, 
        validate=Length(0, 24),
        metadata={'title': 'Manufacturer', 'description': 'The short vendor name who made the NIC.'}
    )
    manuf_desc = String(
        required=True, 
        validate=Length(0, 80),
        metadata={'title': 'Manufacturer Description', 'description': 'The full vendor name or vendor description who made the NIC.'}
    )

@app.get('/chilcano/api/manuf/healthcheck')
@app.doc(tags=['Healthcheck'])
def status():
    return {'status': 'healthy'}

@app.get("/chilcano/api/manuf/<string:macAddress>")
@app.doc(tags=['Manufacturer'], operation_id='getManuf')
def get_manuf(macAddress):
    try:
        mac_upper = str(macAddress).upper()
        parse_mac = re.search(r'^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', mac_upper.strip(), re.I).group()
        mac_first3 = mac_upper[:2] + ":" + mac_upper[3:5] + ":" + mac_upper[6:8]
        mac_first4 = mac_upper[:2] + ":" + mac_upper[3:5] + ":" + mac_upper[6:8] + ":" + mac_upper[9:10] + "0"
        mac_first5 = mac_upper[:2] + ":" + mac_upper[3:5] + ":" + mac_upper[6:8] + ":" + mac_upper[9:11] + ":" + mac_upper[12:13] + "0"
        session = Session()
        result = session.query(MacAddressManuf).filter(MacAddressManuf.mac.like(mac_first3 + "%"))
        
        if result.count() == 1:
            row = result.first()
            return {'mac': row.mac, 'manuf': row.manuf, 'manuf_desc': row.manuf_desc}, 200
        elif result.count() > 1:
            result = session.query(MacAddressManuf).filter(MacAddressManuf.mac.like(mac_first4 + "%"))
            if result.count() == 1:
                row = result.first()
                return {'mac': row.mac, 'manuf': row.manuf, 'manuf_desc': row.manuf_desc}, 200
            elif result.count() > 1:
                result = session.query(MacAddressManuf).filter(MacAddressManuf.mac.like(mac_first5 + "%"))
                if result.count() == 1:
                    row = result.first()
                    return {'mac': row.mac, 'manuf': row.manuf, 'manuf_desc': row.manuf_desc}, 200
                else:
                    return jsonify(message="MAC Address '" + macAddress + "' not found in Manufacturer DB.", detail=MAC_FORMATS_SUPPORTED), 404
        else:
            return jsonify(message="MAC Address '" + macAddress + "' not found in Manufacturer DB.", detail=MAC_FORMATS_SUPPORTED), 404
    except:
        return jsonify(message="MAC Address '" + macAddress + "' is malformed.", detail=MAC_FORMATS_SUPPORTED), 400

if __name__ == "__main__":
    # The 'adhoc' value means auto-generate the keypair and certificate
    app.run(host="0.0.0.0", port=5443, ssl_context="adhoc", threaded=True, debug=True)
