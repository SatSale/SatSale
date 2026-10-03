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
    add_generated_address, get_next_address_index, \
    _get_database_schema_version


def _create_test_db() -> str:
    fd, name = tempfile.mkstemp()
    os.close(fd)
    create_database(name)
    migrate_database(name)
    return name


def _drop_test_db(name: str) -> None:
    os.remove(name)


def test_database_addresses() -> None:
    db_name = _create_test_db()
    test_xpub = "xpub6C5uh2bEhmF8ck3LSnNsj261dt24wrJHMcsXcV25MjrYNo3ZiduE3pS2Xs7nKKTR6kGPDa8jemxCQPw6zX2LMEA6VG2sypt2LUJRHb8G63i"
    pseudonode = xpub({"xpub": test_xpub, "bip": "BIP44"})
    assert (get_next_address_index(test_xpub, db_name) == 0)
    add_generated_address(
        0, pseudonode.get_address_at_index(0), test_xpub, db_name)
    assert (get_next_address_index(test_xpub, db_name) == 1)
    _drop_test_db(db_name)


def test_database_schema_version() -> None:
    db_name = _create_test_db()
    assert (_get_database_schema_version(db_name) == 7)
    _drop_test_db(db_name)


def test_database_invoices() -> None:
    db_name = _create_test_db()
    assert (len(load_invoices_from_db("1", name=db_name)) == 0)
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
        "message": "Keep BUIDLing!",
        "type": "invoice",
        "min_btc_value": None,
        "expires_at": None,
    }, db_name)
    invoices = load_invoices_from_db("1", name=db_name)
    invoice0 = load_invoice_from_db(invoice_uuid, db_name)
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
    assert (invoices[0]["type"] == "invoice")
    assert (invoice0["type"] == "invoice")
    _drop_test_db(db_name)


def test_database_deposits() -> None:
    db_name = _create_test_db()
    deposit_uuid = str(uuid.uuid4().hex)
    write_to_database({
        "uuid": deposit_uuid,
        "base_currency": "BTC",
        "base_value": None,
        "btc_value": None,
        "method": "bitcoind",
        "time": time.time(),
        "webhook": None,
        "onchain_dust_limit": 0.00000546,
        "address": "testdepositaddr",
        "rhash": None,
        "bolt11_invoice": None,
        "message": "Deposit test",
        "type": "deposit",
        "min_btc_value": 0.001,
        "expires_at": None,
    }, db_name)
    deposit0 = load_invoice_from_db(deposit_uuid, db_name)
    assert (deposit0 is not None)
    assert (deposit0["uuid"] == deposit_uuid)
    assert (deposit0["type"] == "deposit")
    assert (deposit0["btc_value"] is None)
    assert (deposit0["min_btc_value"] == 0.001)
    assert (deposit0["address"] == "testdepositaddr")
    _drop_test_db(db_name)
