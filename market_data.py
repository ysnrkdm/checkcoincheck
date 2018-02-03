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
