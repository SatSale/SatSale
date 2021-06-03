import time
import uuid
import qrcode

import config
from invoice.price_feed import get_btc_value


class btcd:
    def __init__(self):
        from bitcoinrpc.authproxy import AuthServiceProxy

        connection_str = "http://{}:{}@{}:{}/wallet/{}".format(
            config.username, config.password, config.host, config.rpcport, config.wallet
        )
        print("Attempting to connect to {}.".format(connection_str))

        for i in range(config.connection_attempts):
            try:
                self.rpc = AuthServiceProxy(connection_str)

                info = self.rpc.getblockchaininfo()
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
    
    def create_qr(self):
        qr_str = "{}?amount={}&label={}".format(
            self.address.upper(), self.value, self.label
        )

        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(self.uuid))
        return

    def check_payment(self, address):
        transactions = self.rpc.listtransactions()
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
                address = self.rpc.getnewaddress(label)
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
