#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# file name: mac_manuf_table_def.py
#

# from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('sqlite:///mymusic.db', echo=True)
Base = declarative_base()

#
# Model for 'MacAddressManuf':
# used for API Rest to get access to data from DB
#
class MacAddressManuf(Base):
    """
    """
    __tablename__ = "MacAddressManuf"
 
    mac = Column(String, primary_key=True)
    manuf = Column(String)
    manuf_desc = Column(String)

    def __init__(self, manuf, manuf_desc):
        """
        """
        self.manuf = manuf
        self.manuf_desc = manuf_desc
