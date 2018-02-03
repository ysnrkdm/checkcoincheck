import sqlite3
from dateutil import parser
from pytz import timezone

import market_data

COINCHECK_DB = "coincheck.db"

def get_table_for_scheme(scheme):
    dbname = COINCHECK_DB
    tablename = scheme
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    select_sql = 'select * from %s' % tablename
    data = c.execute(select_sql)
    descr = c.description
    headers = map(lambda a:a[0], descr)
    ret = []
    for row in data:
        ent = {}
        for i, header in enumerate(headers):
            ent[header] = row[i]
        ret.append(ent)
    conn.close()
    return ret

def create_main_table():
    conn = sqlite3.connect(COINCHECK_DB)
    sql = u"""create table main_trades (
        id PRIMARY KEY,
        category,
        time,
        from_amount, from_unit, from_rate_jpy,
        to_amount, to_unit, to_rate_jpy,
        fee_paid_jpy,
        description
        )
    """
    c = conn.cursor()
    c.execute(sql)
    conn.close()

def show_trade(id, category, time,
              from_amount, from_unit, from_rate_jpy,
              to_amount, to_unit, to_rate_jpy,
              fee_paid_jpy, description):
    to_show = {'id': id, 'category': category, 'time': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'from_c': '%s %s [%s]' % (str(from_amount), from_unit, str(from_rate_jpy)),
               'to_c': '%s %s [%s]' % (str(to_amount), to_unit, str(to_rate_jpy)), 'fee': fee_paid_jpy, 'description': description
               }
    print "Inserting %s\n" % to_show


def add_trade(id, category, time,
    from_amount, from_unit, from_rate_jpy,
              to_amount, to_unit, to_rate_jpy,
              fee_paid_jpy, description):
    show_trade(id, category, time,
               from_amount, from_unit, from_rate_jpy,
               to_amount, to_unit, to_rate_jpy,
               fee_paid_jpy, description)
    conn = sqlite3.connect(COINCHECK_DB)
    sql_template = u"""insert into main_trades values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    c = conn.cursor()
    c.execute(sql_template, (id, category, time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                             from_amount, from_unit, from_rate_jpy,
                             to_amount, to_unit, to_rate_jpy,
                             fee_paid_jpy, description)
              )
    conn.commit()
    conn.close()


def normalized_currency_pair(pair_map, at):
    currencies = set(pair_map.keys())
    ret = {}
    if 'JPY' in pair_map:
        currencies.remove('JPY')
        other_cur = list(currencies)[0]
        ret[other_cur] = float(pair_map['JPY']) / float(pair_map[other_cur])
        ret['JPY'] = 1.0
        return ret
    elif 'BTC' in pair_map:
        jpy_per_btc_rate = float(market_data.btc_price_at(at))

        currencies.remove('BTC')
        other_cur = list(currencies)[0]
        ret[other_cur] = float(pair_map['BTC']) / float(pair_map[other_cur]) * jpy_per_btc_rate
        ret['BTC'] = jpy_per_btc_rate
        return ret
    else:
        raise 'Either from_unit or to_unit needs to be either BTC or JPY!'


def jpy_rate_from_pair(from_amount, from_unit, to_amount, to_unit, at):
    # only supports A to {JPY, BTC}, or {JPY, BTC} to B
    if not from_unit in {'BTC', 'JPY'} and not to_unit in {'BTC', 'JPY'}:
        raise 'Either from_unit or to_unit needs to be either BTC or JPY!'

    jpy_rates = normalized_currency_pair({from_unit: from_amount, to_unit: to_amount}, at)
    return {'from': jpy_rates[from_unit], 'to': jpy_rates[to_unit]}
    pass



def process_buys():
    process_simple_buysells('buys')

def process_sells():
    process_simple_buysells('sells')

def process_simple_buysells(side_string):
    table = get_table_for_scheme(side_string)
    for row in table:
        time_local = parser.parse(row['Time'])
        time_utc = time_local.astimezone(timezone('UTC'))
        coins = float(row['Amount'])
        price = float(row['Price'])
        from_amount, to_amount = (price, coins) if side_string == 'buys' else (coins, price)
        from_currency, to_currency = (row['Original Currency'], row['Trading Currency']) if side_string == 'buys' else (row['Trading Currency'], row['Original Currency'])
        jpy_rates = jpy_rate_from_pair(from_amount, from_currency,
                                       to_amount, to_currency, time_utc)

        add_trade("%s-%s" % (side_string, row['ID']), side_string, time_utc,
                  from_amount, from_currency, jpy_rates['from'],
                  to_amount, to_currency, jpy_rates['to'],
                  0, ''
                  )

def process_send():
    process_transmission('send')

def process_deposit_bitcoin():
    process_transmission('deposit_bitcoin')

def process_transmission(direction):
    table = get_table_for_scheme(direction)
    for row in table:
        if row['Status'] == 'confirmed':
            time_local = parser.parse(row['Date'])
            time_utc = time_local.astimezone(timezone('UTC'))
            from_amount, to_amount = (0, row['Amount']) if direction <> 'send' else (row['Amount'], 0)
            from_cur, to_cur = ('', row['Currency']) if direction <> 'send' else (row['Currency'], '')
            add_trade("%s-%s" % (direction, row['ID']), direction, time_utc,
                      from_amount, from_cur, 0,
                      to_amount, to_cur, 0,
                      row['Fee'], ''
                      )

create_main_table()
process_buys()
process_sells()
process_send()
process_deposit_bitcoin()