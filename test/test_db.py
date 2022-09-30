import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from payments.database import *


def test_create_database():
    test_db_name = "test.db"
    if os.path.exists(test_db_name):
        os.remove(test_db_name)

    create_database(test_db_name)
    assert(os.path.exists(test_db_name))

    # Migrate database
    migrate_database(test_db_name)
    print("FUCK")

    with sqlite3.connect(test_db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

    table_names = [row[0] for row in rows]
    assert("payments" in table_names)
    assert("addresses" in table_names)
    assert("schema_version" in table_names)