import sqlalchemy
from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey, BigInteger
from flask_sqlalchemy import SQLAlchemy
import connection
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

class ResponseData(object):
    code = ""
    message = ""
    data = ""
    data_len = ""

    def __init__(self, code, message, data, data_len):
        self.code = code
        self.data = data
        self.message = message
        self.data_len = data_len

class Serialisasi(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)