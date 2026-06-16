import os
import shutil
import subprocess
import sys
import tempfile
import time
from decimal import Decimal

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from node.bitcoind import bitcoind
from node.invoices import encode_bitcoin_invoice, InvoiceType
from payments import database


TEST_RPC_WALLET_NAME = "SatSale-deposit-test"
TEST_RPC_PORT = "18500"
bitcoin_datadir = tempfile.mkdtemp()
bitcoin_args = [
    "-regtest",
    "-conf=" + os.path.join(os.path.dirname(__file__), "bitcoin.conf"),
    "-datadir=" + bitcoin_datadir,
    "-rpcport=" + TEST_RPC_PORT,
]
DB_NAME = tempfile.NamedTemporaryFile().name


def _start_bitcoind() -> None:
    subprocess.call(["bitcoind"] + bitcoin_args + ["-daemon"])
    time.sleep(2)
    subprocess.run(["bitcoin-cli"] + bitcoin_args + [
        "createwallet", TEST_RPC_WALLET_NAME])


def _stop_bitcoind() -> None:
    try:
        subprocess.run(["bitcoin-cli"] + bitcoin_args + ["stop"],
                       check=False, timeout=5)
    except Exception:
        pass
    time.sleep(1)
    if os.path.exists(bitcoin_datadir):
        shutil.rmtree(bitcoin_datadir)


def test_bitcoind_deposit_flow() -> None:
    _start_bitcoind()
    node_config = {
        "host": "localhost",
        "rpcport": TEST_RPC_PORT,
        "rpc_cookie_file": None,
        "username": "SatSale",
        "password": "12345678",
        "tor_bitcoinrpc_host": None,
        "wallet": TEST_RPC_WALLET_NAME
    }
    node = bitcoind(node_config)
    coinbase_address, _, _ = node.get_address(Decimal(1), "", 0)
    node.mine_coins(121, coinbase_address)

    database.create_database(DB_NAME)
    database.migrate_database(DB_NAME)

    deposit_uuid = "test-deposit"
    deposit_address, _, _ = node.get_address(None, deposit_uuid, 0)

    # Encode deposit BIP21 without an amount
    deposit_str = encode_bitcoin_invoice(deposit_uuid, {
        "address": deposit_address,
        "message": "Test deposit"
    }, InvoiceType.BIP21_DEPOSIT)
    assert ("amount=" not in deposit_str)

    # No payments yet
    conf_paid, unconf_paid = node.check_payment(deposit_uuid)
    assert (conf_paid == 0)
    assert (unconf_paid == 0)

    # Write deposit to database
    database.write_to_database({
        "uuid": deposit_uuid,
        "base_currency": "BTC",
        "base_value": None,
        "btc_value": None,
        "method": "onchain",
        "time": time.time(),
        "webhook": None,
        "onchain_dust_limit": 0.00000546,
        "address": deposit_address,
        "rhash": None,
        "bolt11_invoice": None,
        "message": "Test deposit",
        "type": "deposit",
        "min_btc_value": 1.0,
        "expires_at": None,
    }, DB_NAME)

    # Pay less than minimum
    partial_amount = Decimal("0.5")
    node._call_bitcoin_rpc("sendtoaddress", [deposit_address, float(partial_amount)])
    conf_paid, unconf_paid = node.check_payment(deposit_uuid)
    assert (unconf_paid == partial_amount)

    # Mine blocks to confirm partial payment
    node.mine_coins(2, coinbase_address)
    conf_paid, unconf_paid = node.check_payment(deposit_uuid)
    assert (conf_paid == partial_amount)

    # Pay remaining amount
    remaining_amount = Decimal("0.5")
    node._call_bitcoin_rpc("sendtoaddress", [deposit_address, float(remaining_amount)])
    node.mine_coins(2, coinbase_address)

    conf_paid, unconf_paid = node.check_payment(deposit_uuid)
    assert (conf_paid == partial_amount + remaining_amount)

    deposit = database.load_invoice_from_db(deposit_uuid, DB_NAME)
    assert (deposit is not None)
    assert (deposit["type"] == "deposit")
    assert (deposit["btc_value"] is None)
    assert (deposit["min_btc_value"] == 1.0)

    os.remove(DB_NAME)
    _stop_bitcoind()
