#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# file name: mac_manuf_api_rest.py
#

import os, re
from flask import Flask, jsonify
from flask.ext.cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mac_manuf_table_def import MacAddressManuf

ROOT_DIR = "manuf"
FINAL_MANUF_DB_FILENAME = "mac_address_manuf.db"
HTTPS_ENABLED = "true"

engine = create_engine("sqlite:///" + os.path.join(ROOT_DIR, FINAL_MANUF_DB_FILENAME))
Session = sessionmaker(bind=engine)

app = Flask(__name__)
cors = CORS(app, resources={r"/chilcano/api/*": {"origins": "*"}})

# 
# API Rest:
#   i.e. curl -i http://localhost:5000/chilcano/api/manuf/00:50:5a:e5:6e:cf
#   i.e. curl -ik https://localhost:5443/chilcano/api/manuf/00:50:5a:e5:6e:cf
#
@app.route("/chilcano/api/manuf/<string:macAddress>", methods=["GET"])
def get_manuf(macAddress):
    try:
        if re.search(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', macAddress.strip(), re.I).group():
            # expected MAC formats : a1-b2-c3-p4-q5-r6, a1:b2:c3:p4:q5:r6, A1:B2:C3:P4:Q5:R6, A1-B2-C3-P4-Q5-R6
            mac1 = macAddress[:2] + ":" + macAddress[3:5] + ":" + macAddress[6:8]
            mac2 = macAddress[:2] + "-" + macAddress[3:5] + "-" + macAddress[6:8]
            mac3 = mac1.upper()
            mac4 = mac2.upper()
            session = Session()
            result = session.query(MacAddressManuf).filter(MacAddressManuf.mac.in_([mac1, mac2, mac3, mac4])).first()
            try:
                return jsonify(mac=result.mac, manuf=result.manuf, manuf_desc=result.manuf_desc)
            except:
                return jsonify(error="The MAC Address '" + macAddress + "' does not exist"), 404
        else:
            return jsonify(mac=macAddress, manuf="Unknown", manuf_desc="Unknown"), 404
    except:
        return jsonify(error="The MAC Address '" + macAddress + "' is malformed"), 400

if __name__ == "__main__":
    if HTTPS_ENABLED == "true":
        # 'adhoc' means auto-generate the certificate and keypair
        app.run(host="0.0.0.0", port=5443, ssl_context="adhoc", threaded=True, debug=True)
    else:
        app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)