import re

import sys
import mechanize

from pytz import timezone
from dateutil import parser
from datetime import timedelta
from datetime import datetime

import sqlite3
import pandas as pd

import coincheck
import requests


def btc_price_query_60(at, delta=3600, range=60):
    from_time = at + timedelta(seconds=-delta)
    to_time = at + timedelta(seconds=delta)
    from_time = int(from_time.strftime('%s'))
    to_time = int(to_time.strftime('%s'))
    url = 'https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc?periods=%d&after=%s&before=%s' % (range, str(from_time), str(to_time))
    print url
    response = requests.get(url)
    print response.json()
    print '^-- response'
    if 'result' in response.json():
        lines = response.json()['result'][str(range)]
        if lines:
            aline = lines[0]
            close_time_unixtime, open_price, high_price, low_price, close_price, _, _ = aline
            close_time = datetime.datetime.fromtimestamp(close_time_unixtime, tz=timezone('UTC'))
            return {'close_time': close_time, 'open_price': open_price, 'high_price': high_price, 'low_price': low_price, 'close_price': close_price}
        else:
            return None
    else:
        return None

def btc_price_query_1h(at):
    at_unixtime = int(at.strftime('%s'))
    url = 'https://min-api.cryptocompare.com/data/histohour?fsym=BTC&tsym=JPY&limit=10&e=coincheck&toTs=%s' % (str(at_unixtime))
    # print url
    response = requests.get(url)
    # print '^-- response 000'
    # print response.json()
    response = response.json()
    if 'Response' in response and response['Response'] == 'Success' and 'Data' in response:
        data = response['Data']
        last_data = data[-1]
        last_data_time = last_data['time']
        last_data_time_adj = datetime.fromtimestamp(last_data_time, tz=timezone('UTC'))
        last_data['time'] = last_data_time_adj
        print last_data
        return last_data
    else:
        print 'whats wrong'
        return None

def btc_price_query_day_close(at):
    at_unixtime = int(at.strftime('%s'))
    url = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=BTC&tsyms=JPY&ts=%s&markets=coincheck&extraParams=checkcoincheck' % (str(at_unixtime))
    # print url
    response = requests.get(url)
    # print '^-- response'
    # print response.json()
    if 'BTC' in response.json():
        price = response.json()['BTC']['JPY']
        return price


def btc_price_at(at):
    res_day = btc_price_query_day_close(at)
    return res_day