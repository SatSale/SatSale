import os
import sys
import tempfile
import time
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from node.xpub import xpub
from payments.database import \
    create_database, migrate_database, write_to_database, \
    load_invoice_from_db, load_invoices_from_db, \
    add_generated_address, get_next_address_index


DB_NAME = tempfile.NamedTemporaryFile().name


def _create_test_db() -> None:
    create_database(DB_NAME)
    migrate_database(DB_NAME)


def _drop_test_db() -> None:
    os.remove(DB_NAME)


def test_database_addresses() -> None:
    _create_test_db()
    test_xpub = "xpub6C5uh2bEhmF8ck3LSnNsj261dt24wrJHMcsXcV25MjrYNo3ZiduE3pS2Xs7nKKTR6kGPDa8jemxCQPw6zX2LMEA6VG2sypt2LUJRHb8G63i"
    pseudonode = xpub({"xpub": test_xpub, "bip": "BIP44"})
    assert (get_next_address_index(test_xpub, DB_NAME) == 0)
    add_generated_address(
        0, pseudonode.get_address_at_index(0), test_xpub, DB_NAME)
    assert (get_next_address_index(test_xpub, DB_NAME) == 1)
    _drop_test_db()


def test_database_invoices() -> None:
    _create_test_db()
    assert (len(load_invoices_from_db("1", DB_NAME)) == 0)
    invoice_uuid = str(uuid.uuid4().hex)
    write_to_database({
        "uuid": invoice_uuid,
        "base_currency": "USD",
        "base_value": 1,
        "btc_value": 0.00004856,
        "method": "lightning",
        "time": time.time(),
        "webhook": None,
        "onchain_dust_limit": 0.00000546,
        "address": "testaddr",
        "rhash": None,
        "bolt11_invoice": None,
        "message": "Keep BUIDLing!"
    }, DB_NAME)
    invoices = load_invoices_from_db("1", DB_NAME)
    invoice0 = load_invoice_from_db(invoice_uuid, DB_NAME)
    assert (len(invoices) == 1)
    assert (invoice0 is not None)
    assert (invoices[0]["uuid"] == invoice_uuid)
    assert (invoice0["uuid"] == invoice_uuid)
    assert (invoices[0]["method"] == "lightning")
    assert (invoice0["method"] == "lightning")
    assert (invoices[0]["btc_value"] > 0)
    assert (invoice0["btc_value"] > 0)
    assert (invoices[0]["address"] == "testaddr")
    assert (invoice0["address"] == "testaddr")
    assert (invoices[0]["rhash"] is None)
    assert (invoice0["rhash"] is None)
    assert (invoices[0]["bolt11_invoice"] is None)
    assert (invoice0["bolt11_invoice"] is None)
    _drop_test_db()
