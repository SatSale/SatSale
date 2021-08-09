import time
import uuid
import qrcode
import json

import config
from invoice.price_feed import get_btc_value

if config.tor_bitcoinrpc_host is not None:
    from gateways.tor import session


def call_tor_bitcoin_rpc(method, params):
    url = "{}:{}".format(config.tor_bitcoinrpc_host, config.rpcport)
    payload = json.dumps({"method": method, "params": params})
    headers = {"content-type": "application/json", "cache-control": "no-cache"}
    response = session.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=(config.username, config.password),
    )
    return json.loads(response.text)


class btcd:
    def __init__(self):
        from bitcoinrpc.authproxy import AuthServiceProxy

        for i in range(config.connection_attempts):
            if config.tor_bitcoinrpc_host is None:
                self.tor = False
                connection_str = "http://{}:{}@{}:{}/wallet/{}".format(
                    config.username,
                    config.password,
                    config.host,
                    config.rpcport,
                    config.wallet,
                )
                print("Attempting to connect to {}.".format(connection_str))
            else:
                self.tor = True
                print(
                    "Attempting to contact bitcoind rpc tor hidden service: {}:{}".format(
                        config.tor_bitcoinrpc_host, config.rpcport
                    )
                )

            try:
                # Normal Connection
                if config.tor_bitcoinrpc_host is None:
                    self.rpc = AuthServiceProxy(connection_str)
                    info = self.rpc.getblockchaininfo()
                # Tor Connection
                else:
                    info = call_tor_bitcoin_rpc("getblockchaininfo", None)

                print(info)
                print("Successfully contacted bitcoind.")
                break

            except Exception as e:
                print(e)
                time.sleep(config.pollrate)
                print(
                    "Attempting again... {}/{}...".format(
                        i + 1, config.connection_attempts
                    )
                )
        else:
            raise Exception(
                "Could not connect to bitcoind. \
                Check your RPC / port tunneling settings and try again."
            )

    def create_qr(self, uuid, address, value):
        qr_str = "{}?amount={}&label={}".format(address.upper(), value, uuid)

        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))
        return

    def check_payment(self, address):
        if not self.tor:
            transactions = self.rpc.listtransactions()
        else:
            transactions = call_tor_bitcoin_rpc("listtransactions", None)["result"]

        relevant_txs = [tx for tx in transactions if tx["address"] == address]

        conf_paid = 0
        unconf_paid = 0
        for tx in relevant_txs:
            if tx["confirmations"] >= config.required_confirmations:
                conf_paid += tx["amount"]
            else:
                unconf_paid += tx["amount"]

        return conf_paid, unconf_paid

    def get_address(self, amount, label):
        for i in range(config.connection_attempts):
            try:
                if not self.tor:
                    address = self.rpc.getnewaddress(label)
                else:
                    address = call_tor_bitcoin_rpc("getnewaddress", [label])["result"]

                return address, None

            except Exception as e:
                print(e)
                print(
                    "Attempting again... {}/{}...".format(
                        i + 1, config.connection_attempts
                    )
                )
            if config.connection_attempts - i == 1:
                print("Reconnecting...")
                self.__init__()
        return None
