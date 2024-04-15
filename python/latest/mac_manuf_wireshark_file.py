#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# file name: mac_manuf_wireshark_file.py
#

import glob, hashlib, os, re, urllib, sqlite3
import urllib.request
import unicodecsv as unicodecsv
from datetime import datetime

WIRESHARK_MANUF_URL = "https://www.wireshark.org/download/automated/data/manuf"
#WIRESHARK_MANUF_URL = "https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=manuf"
#WIRESHARK_MANUF_URL = "http://anonsvn.wireshark.org/wireshark/trunk/manuf"
ROOT_DIR = "manuf"
#ROOT_DIR = "."
FILENAME_PREFIX = ""
#FILENAME_PREFIX = "manuf_"
TABLE_NAME = "MacAddressManuf"
FINAL_MANUF_DB_FILENAME = "mac_address_manuf.db"

def download_file(rootdir, filename_prefix, url):
    file_timestamp = datetime.now().strftime('%Y%m%d.%H%M%S.%f')[:-3]
    try:
        filename = filename_prefix + file_timestamp
        urllib.request.urlretrieve(url, os.path.join(rootdir, filename))
        return filename
    except Exception as e:
        print(e)
        return filename_prefix + file_timestamp + "_error"


def generate_file_md5(rootdir, filename, blocksize=2**20):
    m = hashlib.md5()
    with open(os.path.join(rootdir, filename), "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def clean_manuf_file(rootdir, filename):
    f1 = open(os.path.join(rootdir, filename), "r")
    lines = f1.readlines()
    f1.close()
    f2 = open(os.path.join(rootdir, filename + "_cleaned"), "w")
    for text_line in lines:
        if text_line.strip()[:1] != "#" and text_line.strip():
            # remove duplicates
            if text_line.strip() != "03-00-00-00-00-10	(OS/2-1.3-EE+Communications-Manager)":
                f2.write(text_line)
    f2.close()
    return f2.name[len(ROOT_DIR)+1:]


def create_manuf_file_tab(rootdir, filename):
    file1 = open(os.path.join(rootdir, filename), "r")
    file2 = open(os.path.join(rootdir, filename + ".tab"), "w")
    for line1 in file1:
        if line1.strip() != "":
            cols = re.split("\s\s+|\t", line1)
            try:
                col1 = cols[0].strip()
            except:
                col1 = " "
            try:
                col2 = cols[1].strip()
            except:
                col2 = " "
            try:
                col3 = cols[2].strip()
            except:
                col3 = " "
            file2.write(col1 + "\t" + col2 + "\t" + col3 + "\n")
    file2.close()
    return file2.name[len(ROOT_DIR)+1:]


def load_manuf_tab_file_into_db(rootdir, tabfilename, dbfilename, tablename):
    db_name = os.path.join(rootdir, dbfilename)
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("CREATE TABLE " + tablename + " (mac TEXT, manuf TEXT, manuf_desc TEXT, PRIMARY KEY (mac))")
    with open(os.path.join(rootdir, tabfilename), 'rb') as input_file:
        reader = unicodecsv.reader(input_file, delimiter="\t")
        data = [row for row in reader]
    try:
        cur.executemany("INSERT INTO " + tablename + " (mac, manuf, manuf_desc) VALUES (?, ?, ?);", data)
        con.commit()
        return cur.rowcount
    except:
        return False

#
# main process:
# download manuf file, generate hash, cleaning and load into db
#
try:
    if not os.path.exists(ROOT_DIR):
        os.makedirs(ROOT_DIR)
    manuf_newest_local = max(glob.iglob(os.path.join(ROOT_DIR, FILENAME_PREFIX + "*.*.*_*_ok")), key=os.path.getctime)
    try:
        f = open(manuf_newest_local, "r")
        manuf_newest_local = manuf_newest_local[len(ROOT_DIR)+1:]
        md5_local = manuf_newest_local[len(FILENAME_PREFIX)+20:-3]
        print("Local file found (being used): " + os.path.join(ROOT_DIR, manuf_newest_local))
        f.close()
    except:
        md5_local = ""
        print("Not local file found. Is '" + manuf_newest_local + "' a file?.")
except:
    md5_local = ""

manuf_downloaded_filename = download_file(ROOT_DIR, FILENAME_PREFIX, WIRESHARK_MANUF_URL)
if manuf_downloaded_filename[-6:] == "_error":
    print("Error when downloading from '" + WIRESHARK_MANUF_URL + "'. Nothing to do.")
    manuf_to_db = False
else:
    md5_downloaded_manuf = generate_file_md5(ROOT_DIR, manuf_downloaded_filename)
    if md5_downloaded_manuf == md5_local:
        manuf_filename_final = manuf_downloaded_filename + "_" + md5_downloaded_manuf + "_ko"
        manuf_to_db = False
    else:
        manuf_filename_final = manuf_downloaded_filename + "_" + md5_downloaded_manuf + "_ok"
        manuf_to_db = True
    os.rename(os.path.join(ROOT_DIR, manuf_downloaded_filename), os.path.join(ROOT_DIR, manuf_filename_final))
    print("New Manuf file downloaded: " + os.path.join(ROOT_DIR, manuf_filename_final))

if manuf_to_db:
    filename_cleaned = clean_manuf_file(ROOT_DIR, manuf_filename_final)
    print("Cleaned Manuf file created: " + os.path.join(ROOT_DIR, filename_cleaned))
    tab_filename = create_manuf_file_tab(ROOT_DIR, filename_cleaned)
    print("TAB Manuf file created: " + os.path.join(ROOT_DIR, tab_filename))
    total_row_loaded = load_manuf_tab_file_into_db(ROOT_DIR, tab_filename, tab_filename + ".db", TABLE_NAME)
    print("DB Manuf file created: " + os.path.join(ROOT_DIR, tab_filename + ".db"))
    os.rename(os.path.join(ROOT_DIR, tab_filename + ".db"), os.path.join(ROOT_DIR, FINAL_MANUF_DB_FILENAME))
    if total_row_loaded:
        print("( '" +  FINAL_MANUF_DB_FILENAME + "' was created and " + str(total_row_loaded) + " rows were loaded into '" + TABLE_NAME + "' table. )")
    else:
        print("( Error: TAB Manuf file wasn't loaded into DB )")
else:
    print("The newest Manuf file download has same MD5 (not cleaning and not loading into DB)")
