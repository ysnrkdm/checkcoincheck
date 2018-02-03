import requests
from datetime import datetime
from pytz import timezone

EPOCH = datetime(1970, 1, 1, tzinfo=timezone('utc'))

def btc_price_query_day_close(at):
    at_unixtime = (at - EPOCH).total_seconds()
    url = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=BTC&tsyms=JPY&ts=%s&markets=coincheck&extraParams=checkcoincheck' % (str(at_unixtime))
    # print url
    response = requests.get(url)
    # print '^-- response'
    # print response.json()
    if 'BTC' in response.json():
        price = response.json()['BTC']['JPY']
        return price


def btc_price_at(at):
    # at must be timezone aware
    res_day = btc_price_query_day_close(at)
    return res_day

def coin_price_query_day_close(currency, at):
    # print '%s - %s' % (at.strftime('%Y-%m-%d %H:%M:%S %Z'), EPOCH.strftime('%Y-%m-%d %H:%M:%S %Z'))
    at_unixtime = (at - EPOCH).total_seconds()
    url = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=%s&tsyms=JPY&ts=%s&markets=coincheck&extraParams=checkcoincheck' % (currency, str(at_unixtime))
    # print url
    response = requests.get(url)
    # print '^-- response'
    # print response.json()
    if currency in response.json():
        price = response.json()[currency]['JPY']
        return price


def coin_price_at(currency, at):
    # at must be timezone aware
    res_day = coin_price_query_day_close(currency, at)
    return res_day