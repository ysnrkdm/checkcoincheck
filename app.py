from flask import Flask, render_template, request, redirect, url_for, Markup
import sqlite3

app = Flask(__name__)

COINCHECK_DB = "coincheck.db"

@app.route("/")
def hello():
    return "Hello, world."

def table_html(headers, data_array):
    ret = "<table>"
    ret = ret + '<tr>'
    for header in headers:
        ret = ret + '<th>'
        ret = ret + header[0]
        ret = ret + '</th>'
    ret = ret + '</tr>'
    for row in data_array:
        ret = ret + '<tr>'
        for cell in row:
            ret = ret + '<td>'
            ret = ret + str(cell)
            ret = ret + '</td>'
        ret = ret + '</tr>'

    ret = ret + "</table>"
    return ret

def get_table_for_scheme(scheme):
    dbname = COINCHECK_DB
    tablename = scheme
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    select_sql = 'select * from %s' % tablename
    data = c.execute(select_sql)
    headers = c.description
    ret = table_html(headers, data)
    conn.close()
    return ret

@app.route("/buys")
def table_buys():
    table = get_table_for_scheme("buys")
    return render_template('index.html', table_here=Markup(table))

@app.route("/sells")
def table_sells():
    table = get_table_for_scheme("sells")
    return render_template('index.html', table_here=Markup(table))

@app.route("/send")
def table_send():
    table = get_table_for_scheme("send")
    return render_template('index.html', table_here=Markup(table))

@app.route("/deposit_bitcoin")
def table_deposit_bitcoin():
    table = get_table_for_scheme("deposit_bitcoin")
    return render_template('index.html', table_here=Markup(table))

@app.route("/orders")
def table_orders():
    table = get_table_for_scheme("orders")
    return render_template('index.html', table_here=Markup(table))

@app.route("/card_payments")
def table_card_payments():
    table = get_table_for_scheme("card_payments")
    return render_template('index.html', table_here=Markup(table))

if __name__ == "__main__":
    app.debug = True
    app.run()