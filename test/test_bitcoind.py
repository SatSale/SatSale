import os
import subprocess
import sys
import tempfile
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from node.bitcoind import bitcoind
from node.invoices import encode_bitcoin_invoice, InvoiceType


TEST_RPC_WALLET_NAME = "SatSale-test"
bitcoin_datadir = tempfile.TemporaryDirectory().name
os.mkdir(bitcoin_datadir)
bitcoin_args = [
    "-regtest",
    "-conf=" + os.path.join(os.path.dirname(__file__), "bitcoin.conf"),
    "-datadir=" + bitcoin_datadir
]


def _start_bitcoind() -> None:
    subprocess.call(["bitcoind"] + bitcoin_args + ["-daemon"])
    time.sleep(1)
    subprocess.run(["bitcoin-cli"] + bitcoin_args + [
        "createwallet", TEST_RPC_WALLET_NAME])


def _stop_bitcoind() -> None:
    subprocess.run(["bitcoin-cli"] + bitcoin_args + ["stop"])


def test_bitcoind_payment_flow() -> None:
    _start_bitcoind()
    # We don't specify these in test/config.toml, as this is unnecessary
    # for other tests.
    node_config = {
        "host": "localhost",
        "rpcport": 18443,
        "rpc_cookie_file": None,
        "username": "SatSale",
        "password": "12345678",
        "tor_bitcoinrpc_host": None,
        "wallet": TEST_RPC_WALLET_NAME
    }
    node = bitcoind(node_config)
    coinbase_address, _, _ = node.get_address(1, "", 0)
    node.mine_coins(121, coinbase_address)
    invoice_uuid = "test-invoice"
    invoice_address, _, _ = node.get_address(1, invoice_uuid, 0)
    invoice_amount = 1.23456789
    # no payment made, should be no incoming UTXOs
    conf_paid, unconf_paid = node.check_payment(invoice_uuid)
    assert (conf_paid == 0)
    assert (unconf_paid == 0)
    # generate BIP21 invoice and pay
    invoice_str = encode_bitcoin_invoice(invoice_uuid, {
        "address": invoice_address,
        "btc_value": invoice_amount
    }, InvoiceType.BIP21)
    node.pay_invoice(invoice_str)
    # payment made, should have 0 confirmed, invoice amount unconfirmed
    conf_paid, unconf_paid = node.check_payment(invoice_uuid)
    assert (conf_paid == 0)
    assert (unconf_paid == invoice_amount)
    # mine some more blocks
    node.mine_coins(50, coinbase_address)
    # more blocks mined, should have all invoice amount confirmed
    conf_paid, unconf_paid = node.check_payment(invoice_uuid)
    assert (conf_paid == invoice_amount)
    assert (unconf_paid == 0)
    _stop_bitcoind()
