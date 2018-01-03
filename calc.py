import sqlite3
import sys

COINCHECK_DB = "coincheck.db"

def get_table_for_scheme(currency):
    dbname = COINCHECK_DB
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    select_sql = u"""select * from main_trades WHERE
        from_unit = ? or to_unit = ?
        order by time asc"""
    data = c.execute(select_sql, (currency, currency))
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

avg_price = 0
total_bch = 0
total_bch_raw = 0
earning = 0

argvs = sys.argv
argc = len(argvs)
if argc != 2:
    print 'Usage: # python %s passcode' % argvs[0]
    raise 'Passcode not found'

currency = argvs[1]

if currency == 'BCH':
    total_bch = total_bch_raw = 6

def trade_summary(row):
    from_info = "%s %s [%s]" % (row['from_amount'], row['from_unit'], row['from_rate_jpy'])
    to_info = "%s %s [%s]" % (row['to_amount'], row['to_unit'], row['to_rate_jpy'])
    return "%s %s -> %s at %s" % (row['category'], from_info, to_info, row['time'])

for row in get_table_for_scheme(currency):
    print trade_summary(row)
    if row['to_unit'] == currency:
        if row['category'] == 'buys':
            avg_price = (avg_price * total_bch + row['to_rate_jpy'] * row['to_amount']) / (total_bch + row['to_amount'])
        total_bch += row['to_amount']
        total_bch_raw = total_bch
    elif row['from_unit'] == currency:
        total_bch = max(0, total_bch - row['from_amount'])
        total_bch_raw = total_bch_raw - row['from_amount']
        if row['category'] == 'sells':
            earning_by_this_sell = row['from_amount'] * (row['from_rate_jpy'] - avg_price)
            earning += earning_by_this_sell
    print "  -- Avg %s price is %s, total %s %s. Total earning is %s" % (currency, str(avg_price), currency, str(total_bch_raw), str(earning))