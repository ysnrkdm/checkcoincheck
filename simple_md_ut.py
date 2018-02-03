import sys
import market_data
import dateutil.parser

def print_md(time_str):
    answer = market_data.btc_price_query_day_close(dateutil.parser.parse(time_str))
    print "%s\t%f" % (time_str, answer)
    sys.stdout.flush()

def print_md_m(currency, time_str):
    answer = market_data.coin_price_at(currency, dateutil.parser.parse(time_str))
    print "%s\t%f" % (time_str, answer)

print_md_m('BCH', '2017-10-01 02:50:06 +0900')
print_md_m('ETH', '2017-03-16 15:20:14 +0900')