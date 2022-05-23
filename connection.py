import sqlalchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import urllib
from sqlalchemy import MetaData

import pyodbc 

class config:
    app = Flask(__name__)
    config_server = 'LAPTOP-T54URQKB'
    config_database = 'resits'
    config_UID = ''
    config_password = ''

    ## koneksi ke database MSSQL menggunakan PyODBC
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                          'Server='+config_server+';'+
                          'Database='+config_database+';'+
                          'Trusted_Connection=yes;')

    print("connection established with pyodbc")