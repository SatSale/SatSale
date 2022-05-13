import sqlite3
import logging

db = sqlite3.connect('invoice.db')
cur = db.cursor()

def create_database():
        logging.info("Initializing DB...")
        cur.execute("CREATE TABLE payments (uuid TEXT, fiat_value DECIMAL, btc_value DECIMAL, method TEXT, address TEXT, time DECIMAL, webhook TEXT, rhash TEXT)")

def _get_database_schema_version():
        return cur.execute("SELECT version FROM schema_version").fetchone()[0]

def _set_database_schema_version(version):
        cur.execute("UPDATE schema_version SET version = '%s'", (version))

def _log_migrate_database(from_version, to_version, message):
    logging.info(
        "Migrating database from {} to {}: {}".format(from_version, to_version, message)
    )

def migrate_database():
        version_table_exists = cur.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_version'"
        ).fetchone()
        if version_table_exists:
            schema_version = _get_database_schema_version()
        else:
            schema_version = 0

        if schema_version < 1:
            _log_migrate_database(0, 1, "Creating new table for schema version")
            cur.execute("CREATE TABLE schema_version (version INT)")
            cur.execute("INSERT INTO schema_version (version) VALUES (1)")

        if schema_version < 2:
            _log_migrate_database(1, 2, "Creating new table for generated addresses")
            cur.execute("CREATE TABLE addresses (n INTEGER, address TEXT, xpub TEXT)")
            _set_database_schema_version(2)

        new_version = _get_database_schema_version()
        if schema_version != new_version:
            logging.info(
            "Finished migrating database schema from version {} to {}".format(
                schema_version, new_version
            )
        )

def write_to_database(invoice):
        cur.executemany(
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
db.commit()

def load_invoices_from_db(where):
        cur.row_factory = sqlite3.Row
        rows = cur.execute("SELECT * FROM payments WHERE '%s'", (where)).fetchall()
        return rows

def load_invoice_from_db(uuid):
    rows = load_invoices_from_db("uuid='{}'".format(uuid))
    if len(rows) > 0:
        return [dict(ix) for ix in rows][0]
    else:
        return None

def add_generated_address(index, address, xpub):
        cur.execute(
            "INSERT INTO addresses (n, address, xpub) VALUES (?,?,?)",
            (
                index,
                address,
                xpub,
            ),
        )
def get_next_address_index(xpub):
        cur.row_factory = sqlite3.Row
        addresses = cur.execute(
            "SELECT n FROM addresses WHERE xpub='%s' ORDER BY n DESC LIMIT 1", (xpub)
        ).fetchall()

        if len(addresses) == 0:
            return 0
        else:
            return max([dict(addr)["n"] for addr in addresses]) + 1        
