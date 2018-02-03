import re

import sys
import mechanize

import sqlite3
import pandas as pd

import os

COINCHECK_DB = "maindata.db"
CSV_FOLDER = "temp/"
CSV_FILE_PREFIX = "cc_"

def download_files():
    argvs = sys.argv
    argc = len(argvs)
    if argc != 2:
        print 'Usage: # python %s passcode' % argvs[0]
        raise Exception('Passcode not found')

    passcode = argvs[1]

    print('Logging in to Coincheck...')

    br = mechanize.Browser()
    br.open('https://coincheck.com/sessions/signin?account_type=consumer')
    # print(br.title())

    br.form = br.forms()[0]
    br['email'] = os.getenv("CC_EMAIL", "")
    br['password'] = os.getenv("CC_PASSWORD", "")
    print("%s %s" % (os.getenv("CC_EMAIL", ""), os.getenv("CC_PASSWORD", "")))
    response = br.submit()
    # print(br.title())

    br.form = br.forms()[0]
    br['two_factor_password'] = passcode
    br.submit()
    # print(br.title())
    if br.title() != 'Bitcoin and cryptocurrency exchange. Buy, sell, and margin trade cryptocurrency. | Coincheck':
        print('Login failed. Aborting')
        quit()

    print('Seems like login succeeded. Downloading files.')

    # res = br.retrieve('https://coincheck.com/deposits/download.csv', 'deposits.csv')
    # res = br.retrieve('https://coincheck.com/withdraws/download.csv', 'withdraws.csv')
    res = br.retrieve('https://coincheck.com/sells/download.csv', CSV_FOLDER + CSV_FILE_PREFIX + 'sells.csv')
    res = br.retrieve('https://coincheck.com/buys/download.csv', CSV_FOLDER + CSV_FILE_PREFIX + 'buys.csv')
    res = br.retrieve('https://coincheck.com/send/download.csv', CSV_FOLDER + CSV_FILE_PREFIX + 'send.csv')
    res = br.retrieve('https://coincheck.com/deposit_bitcoin/download.csv', CSV_FOLDER + CSV_FILE_PREFIX + 'deposit_bitcoin.csv')

    orders_url = 'https://coincheck.com/exchange/orders/download_my_complete_order.csv?'
    orders_url_start_date = 'start_date=%222015-01-01T00:00:00.000Z%22&'
    orders_url_end_date = 'end_date=%222018-12-31T23:59:59.999Z%22'

    res = br.retrieve(orders_url + orders_url_start_date + orders_url_end_date, CSV_FOLDER + CSV_FILE_PREFIX + 'orders.csv')

    print('5 files download.')


def fetch_a_file_and_store_db(filename, prefix='cc_'):
    df_raw = pd.read_csv(CSV_FOLDER + CSV_FILE_PREFIX + filename)
    df = df_raw.rename(columns=lambda s: s.replace(" ", "_").lower())
    dbname = COINCHECK_DB
    tablename = prefix + re.findall('(.*?)\.csv', filename)[0]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    df.to_sql(tablename, conn, if_exists="replace")

    select_sql = 'select * from %s' % tablename
    for row in c.execute(select_sql):
        print(row)

    conn.close()


def store_data_to_db():
    # fetch_a_file_and_store_db('deposits.csv')
    # fetch_a_file_and_store_db('withdraws.csv')
    fetch_a_file_and_store_db('sells.csv')
    fetch_a_file_and_store_db('buys.csv')
    fetch_a_file_and_store_db('card_payments.csv')
    fetch_a_file_and_store_db('send.csv')
    fetch_a_file_and_store_db('deposit_bitcoin.csv')
    fetch_a_file_and_store_db('orders.csv')


# download_files()
store_data_to_db()
