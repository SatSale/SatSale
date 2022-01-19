import sqlite3
import logging


def create_database(name="database.db"):
    with sqlite3.connect(name) as conn:
        logging.info("Creating new {}...".format(name))
        conn.execute(
            "CREATE TABLE payments (uuid TEXT, fiat_value DECIMAL, btc_value DECIMAL, method TEXT, address TEXT, time DECIMAL, webhook TEXT, rhash TEXT)"
        )
    return


def _get_database_schema_version(name="database.db"):
    with sqlite3.connect(name) as conn:
        return conn.execute("SELECT version FROM schema_version").fetchone()[0]


def _set_database_schema_version(version, name="database.db"):
    with sqlite3.connect(name) as conn:
        conn.execute("UPDATE schema_version SET version = {}".format(version))


def _log_migrate_database(from_version, to_version, message):
    logging.info("Migrating database from {} to {}: {}".format(
        from_version, to_version, message))


def migrate_database(name="database.db"):
    with sqlite3.connect(name) as conn:
        version_table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_version'"
        ).fetchone()
        if version_table_exists:
            schema_version = _get_database_schema_version(name)
        else:
            schema_version = 0

    if schema_version < 1:
        _log_migrate_database(0, 1, "Creating new table for schema version")
        with sqlite3.connect(name) as conn:
            conn.execute("CREATE TABLE schema_version (version INT)")
            conn.execute("INSERT INTO schema_version (version) VALUES (1)")

    #if schema_version < 2:
    #   do next migration

    new_version = _get_database_schema_version(name)
    if schema_version != new_version:
        logging.info(
            "Finished migrating database schema from version {} to {}".format(
                schema_version, new_version))


def write_to_database(invoice, name="database.db"):
    with sqlite3.connect(name) as conn:
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


def load_invoices_from_db(where, name="database.db"):
    with sqlite3.connect(name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute("SELECT * FROM payments WHERE {}".format(where)).fetchall()
    return rows


def load_invoice_from_db(uuid, name="database.db"):
    rows = load_invoices_from_db("uuid='{}'".format(uuid), name)
    if len(rows) > 0:
        return [dict(ix) for ix in rows][0]
    else:
        return None


def check_address_table_exists():
    with sqlite3.connect("database.db") as conn:
        exists = conn.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='addresses'"
        ).fetchall()
        if len(exists) == 0:
            return False

    return exists


def create_address_table():
    with sqlite3.connect("database.db") as conn:
        logging.info("Creating new table for generated addresses")
        conn.execute("CREATE TABLE addresses (n INTEGER, address TEXT)")
    return


def add_generated_address(index, address):
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO addresses (n, address) VALUES (?,?)",
            (
                index,
                address,
            ),
        )
    return


def get_next_address_index():
    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        addresses = cur.execute("SELECT * FROM addresses").fetchall()

    if len(addresses) == 0:
        return 0
    else:
        return max([dict(addr)["n"] for addr in addresses]) + 1
