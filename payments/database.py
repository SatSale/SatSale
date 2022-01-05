import sqlite3


def create_database(name="database.db"):
    with sqlite3.connect("database.db") as conn:
        logging.info("Creating new database.db...")
        conn.execute(
            "CREATE TABLE payments (uuid TEXT, fiat_value DECIMAL, btc_value DECIMAL, method TEXT, address TEXT, time DECIMAL, webhook TEXT, rhash TEXT)"
        )
    return


def write_to_database(invoice, name="database.db"):
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO payments (uuid,fiat_value,btc_value,method,address,time,webhook,rhash) VALUES (?,?,?,?,?,?,?,?)",
            (
                invoice["uuid"],
                invoice["fiat_value"],
                invoice["btc_value"],
                invoice["method"],
                invoice["address"],
                invoice["time"],
                invoice["webhook"],
                invoice["rhash"],
            ),
        )
    return


def load_invoice_from_db(uuid):
    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute(
            "select * from payments where uuid='{}'".format(uuid)
        ).fetchall()
    if len(rows) > 0:
        return [dict(ix) for ix in rows][0]
    else:
        return None
