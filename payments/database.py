import sqlite3
import logging


DEFAULT_DATABASE = "database.db"


def create_database(name: str = DEFAULT_DATABASE) -> None:
    with sqlite3.connect(name) as conn:
        logging.info("Creating new {}...".format(name))
        conn.execute(
            "CREATE TABLE payments (uuid TEXT, fiat_value DECIMAL, btc_value DECIMAL, method TEXT, address TEXT, time DECIMAL, webhook TEXT, rhash TEXT)"
        )
    return


def _get_database_schema_version(name: str = DEFAULT_DATABASE) -> int:
    with sqlite3.connect(name) as conn:
        return int(conn.execute(
            "SELECT version FROM schema_version").fetchone()[0])


def _set_database_schema_version(version: int,
                                 name: str = DEFAULT_DATABASE) -> None:
    with sqlite3.connect(name) as conn:
        conn.execute("UPDATE schema_version SET version = {}".format(
            version))


def _log_migrate_database(from_version: int, to_version: int,
                          message: str) -> None:
    logging.info(
        "Migrating database from {} to {}: {}".format(
            from_version, to_version, message)
    )


def migrate_database(name: str = DEFAULT_DATABASE) -> None:
    with sqlite3.connect(name) as conn:
        version_table_exists = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name = 'schema_version'"
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

    if schema_version < 2:
        _log_migrate_database(1, 2, "Creating new table for generated addresses")
        with sqlite3.connect(name) as conn:
            conn.execute("CREATE TABLE addresses (n INTEGER, address TEXT, xpub TEXT)")
        _set_database_schema_version(2, name)

    if schema_version < 3:
        _log_migrate_database(2, 3, "Adding base currency column to payments table")
        with sqlite3.connect(name) as conn:
            conn.execute("ALTER TABLE payments ADD fiat_currency TEXT")
        _set_database_schema_version(3, name)

    if schema_version < 4:
        _log_migrate_database(3, 4, "Renaming fiat to base in payments table")
        with sqlite3.connect(name) as conn:
            conn.execute("ALTER TABLE payments RENAME fiat_value TO base_value")
            conn.execute("ALTER TABLE payments RENAME fiat_currency TO base_currency")
        _set_database_schema_version(4, name)

    if schema_version < 5:
        _log_migrate_database(4, 5, "Split off bolt11_invoice from address in payments table")
        rows = load_invoices_from_db("1", name)
        lightning_uuids = []
        for row in rows:
            if row["method"] in ["lightning", "clightning", "lnd"]:
                lightning_uuids.append(row["uuid"])
        with sqlite3.connect(name) as conn:
            conn.execute("ALTER TABLE payments ADD bolt11_invoice TEXT")
            # Could use batch UPDATE here maybe.
            # Assume number of rows will be small enough for this to be
            # good enough.
            for uuid in lightning_uuids:
                conn.execute(
                    "UPDATE payments "
                    "SET bolt11_invoice = address, address = NULL "
                    "WHERE uuid = '{}'".format(uuid))
        _set_database_schema_version(5, name)

    if schema_version < 6:
        _log_migrate_database(4, 5, "Add message column to payments table")
        with sqlite3.connect(name) as conn:
            conn.execute("ALTER TABLE payments ADD message TEXT")
        _set_database_schema_version(6, name)

    #if schema_version < 7:
    #   do next migration

    new_version = _get_database_schema_version(name)
    if schema_version != new_version:
        logging.info(
            "Finished migrating database schema from version {} to {}".format(
                schema_version, new_version
            )
        )


def write_to_database(invoice: dict, name: str = DEFAULT_DATABASE) -> None:
    with sqlite3.connect(name) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO payments (uuid, base_currency, base_value, "
            "btc_value, method, address, time, webhook, rhash, "
            "bolt11_invoice, message) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                invoice["uuid"],
                invoice["base_currency"],
                invoice["base_value"],
                invoice["btc_value"],
                invoice["method"],
                invoice["address"],
                invoice["time"],
                invoice["webhook"],
                invoice["rhash"],
                invoice["bolt11_invoice"],
                invoice["message"]
            ),
        )
    return


def load_invoices_from_db(where: str, name: str = DEFAULT_DATABASE) -> list:
    with sqlite3.connect(name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT * FROM payments WHERE {}".format(where)).fetchall()
    return rows


def load_invoice_from_db(uuid: str, name: str = "database.db") -> dict:
    rows = load_invoices_from_db("uuid='{}'".format(uuid), name)
    if len(rows) > 0:
        return [dict(ix) for ix in rows][0]
    else:
        return None


def add_generated_address(index: int, address: str, xpub: str,
                          name: str = DEFAULT_DATABASE) -> None:
    with sqlite3.connect(name) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO addresses (n, address, xpub) VALUES (?,?,?)",
            (
                index,
                address,
                xpub,
            ),
        )
    return


def get_next_address_index(xpub: str, name: str = DEFAULT_DATABASE) -> int:
    with sqlite3.connect(name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        addresses = cur.execute(
            "SELECT n FROM addresses WHERE xpub='{}' "
            "ORDER BY n DESC LIMIT 1".format(xpub)
        ).fetchall()

    if len(addresses) == 0:
        return 0
    else:
        return max([dict(addr)["n"] for addr in addresses]) + 1
