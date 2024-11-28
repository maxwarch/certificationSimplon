#!/usr/bin/env python

import os
from warnings import filterwarnings
import pyodbc
import pandas as pd

DB_SERVER = os.getenv('DB_SERVER')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
CONN_STR = f'Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{DB_SERVER}.database.windows.net,1433;Database={DB_NAME};Uid={DB_USER};Pwd={DB_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

filterwarnings("ignore", category=UserWarning, message='.*pandas only supports SQLAlchemy connectable.*')

name = 'adventureworks'
base_data_path = './data/'
os.makedirs(f'{base_data_path}{name}', exist_ok=True)

print(pyodbc.drivers())

cnxn = pyodbc.connect(CONN_STR)
cursor = cnxn.cursor()

df = pd.read_sql(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'", cnxn)

def fetch_table(row):
    filename = f'{row['TABLE_SCHEMA']}_{row['TABLE_NAME']}'
    print(filename)
    table = f'{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}'
    df = pd.read_sql(f"SELECT * FROM {table}", cnxn)
    df.to_csv(f'{base_data_path}{name}/{filename}.csv')


df.apply(fetch_table, axis=1)