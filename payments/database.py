from multiprocessing import connection
import sqlite3
import logging

db = sqlite3.connect('invoice.db')
cur = db.cursor()

CREATE_PAYMENTS_TABLE = "CREATE TABLE payments (uuid TEXT, fiat_value DECIMAL, btc_value DECIMAL, method TEXT, address TEXT, time DECIMAL, webhook TEXT, rhash TEXT)"
LOAD_INVOICES_FROM_DB = "SELECT * FROM payments WHERE {}"
INSERT_INTO_PAYMENTS_TABLE = """
INSERT INTO payments (uuid,fiat_value,btc_value,method,address,time,webhook,rhash) VALUES (?,?,?,?,?,?,?,?)", 
(
    invoice["uuid"],
    invoice["fiat_value"],
    invoice["btc_value"],
    invoice["method"],
    invoice["address"],
    invoice["time"],
    invoice["webhook"],
    invoice["rhash"],
    )
    """
#INSERT_INTO_PAYMENTS_TABLE = """
#INSERT INTO payments VALUES (:uuid, :fiat_value, :btc_value, :method,address, :time, :webhook, :rhash)",
#{'uuid': invoice.uuid, 'fiat_value': invoice.fiat_value, 'btc_value': invoice.btc_value, 'method': invoice.method, 'address': invoice.address, 'time': invoice.time, 'webhook': invoice.webhook, 'rhash': invoice.rhash'})"""

def create_database():
        logging.info("Initializing DB...")
        cur.execute(CREATE_PAYMENTS_TABLE)

def write_to_database(invoice):
        cur.executemany(INSERT_INTO_PAYMENTS_TABLE)
db.commit()

def load_invoices_from_db(where, db):
        cur.row_factory = sqlite3.Row
        cur.execute(LOAD_INVOICES_FROM_DB.format(where)).fetchall()

def load_invoice_from_db(uuid):
    rows = load_invoices_from_db("uuid='{}'".format(uuid), db)
    if len(rows) > 0:
        return [dict(ix) for ix in rows][0]
    else:
        return None
