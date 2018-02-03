import re

import sys
import mechanize

import sqlite3
import pandas as pd

import os

from pytz import timezone
from datetime import timedelta
from datetime import datetime

import sqlite3

import requests

import urllib
import urllib2
import json
import time
import hmac,hashlib

COINCHECK_DB = "maindata.db"
CSV_FOLDER = "temp/"
CSV_FILE_PREFIX = "polo_"

EPOCH = datetime(1970, 1, 1, tzinfo=timezone('utc'))


def fetch_a_file_and_store_db(filename, prefix='polo_'):
    df_raw = pd.read_csv(CSV_FOLDER + CSV_FILE_PREFIX + filename)
    df = df_raw.rename(columns=lambda s: s.replace(" ", "_").lower())
    r = []
    for i in df.index:
        r.append(i+1)
    s = pd.Series(r)
    df['id'] = s

    dbname = COINCHECK_DB
    tablename = (prefix + re.findall('(.*?)\.csv', filename)[0]).replace(" ", "_").lower()
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    df.to_sql(tablename, conn, if_exists="replace")

    select_sql = 'select * from %s' % tablename
    for row in c.execute(select_sql):
        print(row)

    conn.close()


def store_data_to_db():
    fetch_a_file_and_store_db('depositHistory.csv')
    fetch_a_file_and_store_db('withdrawalHistory.csv')
    fetch_a_file_and_store_db('tradeHistory.csv')


store_data_to_db()
