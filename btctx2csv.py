import sys

import requests

from datetime import datetime
from pytz import timezone
import market_data

def addr_only_or_all(wallet_address, ios):
    addrs = map(lambda ie: (ie['addr'], ie['value']), ios)
    values = 0
    addr_and_values_list = map(lambda ie: (ie['addr'], ie['value']), ios)
    addr_and_values = {}
    for a_and_v in addr_and_values_list:
        addr = a_and_v[0]
        addr_and_values[addr] = addr_and_values.get(addr, 0) + a_and_v[1]
    if wallet_address in addr_and_values:
        addrs = [wallet_address]
        values = addr_and_values[wallet_address]
    else:
        addrs = addr_and_values.keys()
        values = 0

    return (addrs, values)

def entry_from_transaction(wallet_address, trans):
    value_satoshi = 0
    # input == sending
    res_input = []
    input = map(lambda e: e['prev_out'], trans['inputs'])
    addrs, values = addr_only_or_all(wallet_address, input)
    res_input = addrs
    if values > 0:
        value_satoshi = -values

    addrs, values = addr_only_or_all(wallet_address, trans['out'])
    res_output = addrs
    if values > 0:
        value_satoshi = values

    return {'input': res_input, 'output': res_output, 'value_satoshi': value_satoshi, 'unixtime': trans['time']}

def get_replies(wallet_address, limit=50, offset=0):
    url = 'https://blockchain.info/rawaddr/%s?limit=%d&offset=%d' % (wallet_address, limit, offset)
    # print url
    response = requests.get(url)
    res_json = response.json()
    if res_json['address'] <> wallet_address:
        raise 'Address requested is not equal to replied. Something wrong.'
    n_tx = res_json['n_tx']
    replies = res_json['txs']
    return replies

def csv_for_wallet_address(wallet_address, limit=50):
    offset = 0
    fetched = 0
    while(True):
        replies = get_replies(wallet_address, limit=limit, offset=offset)
        if len(replies) == 0:
            break

        for reply in replies:
            r = entry_from_transaction(wallet_address, reply)
            rr = r
            time_utc = datetime.utcfromtimestamp(r['unixtime']).replace(tzinfo=timezone('UTC'))
            rr['time'] = time_utc.strftime('%Y-%m-%d %H:%M:%S %Z')
            del rr['unixtime']
            # print rr['time']
            rate = market_data.btc_price_at(time_utc)
            rr['jpy_per_btc_at_tx_time'] = rate
            rr['in_jpy_at_tx_time'] = rate * rr['value_satoshi'] / 100000000
            print '%s\t%s\t%s\t%s\t%s\t%s\n' % (rr['time'], str(rr['value_satoshi']), 
                str(rr['output']), str(rr['input']),
                str(rr['jpy_per_btc_at_tx_time']), str(rr['in_jpy_at_tx_time']))
            fetched += 1
        offset += limit
    print 'Fetched %d entries' % fetched

argvs = sys.argv
argc = len(argvs)
if argc != 2:
    print 'Usage: # python %s <BTC wallet_address>' % argvs[0]
    raise 'Wallet address not found in command line'

# 14Cqss4i1UHZjjcD4ybdHS2zwp5tycQK71
csv_for_wallet_address(argvs[1])