import time
import uuid
import qrcode
import json
import logging
from google.protobuf.json_format import MessageToJson


import config
from payments.price_feed import get_btc_value
from node.lnd import lnd

if config.tor_bitcoinrpc_host is not None:
    from gateways.tor import session


class btcd(lnd):
    def __init__(self):
        super().__init__()
    # def invoice(self, dollar_value, currency, label):
    #     self.dollar_value = dollar_value
    #     self.currency = currency
    #     self.value = round(get_btc_value(dollar_value, currency), 8)
    #     self.uuid = str(uuid.uuid4())
    #     self.label = self.uuid
    #     self.status = "Payment initialised."
    #     self.response = ""
    #     self.time_left = config.payment_timeout
    #     self.confirmed_paid = 0
    #     self.unconfirmed_paid = 0
    #     self.paid = False
    #     self.txid = ""
    #     self.get_address()
    #     self.create_qr()
    #     return

    def create_qr(self, uuid, address, value):
        qr_str = "bitcoin:{}?amount={}&label={}".format(address, value, uuid)

        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))
        return

    def check_payment(self, address):
        transactions_req = json.loads(
            MessageToJson(self.lnd.list_transactions())
            )

        if 'transactions' not in transactions_req.keys():
            return 0, 0
        else:
            transactions = transactions_req['transactions']

        print(transactions)
        relevant_txs = [tx for tx in transactions if address in tx["destAddresses"]]

        conf_paid = 0
        unconf_paid = 0
        for tx in relevant_txs:

            if "numConfirmations" in tx.keys():
                if tx["numConfirmations"] >= config.required_confirmations:
                    conf_paid += float(tx["amount"]) * 10**-8
                else:
                    unconf_paid += float(tx["amount"]) * 10**-8
            else:
                unconf_paid += float(tx["amount"]) * 10**-8

        return conf_paid, unconf_paid

    def get_address(self, amount, label):
        for i in range(config.connection_attempts):
            try:
                self.address = json.loads(
                    MessageToJson(self.lnd.new_address())
                    )['address']
                # self.address = str(self.address).split('"')[1]
                print(self.address)
                return self.address, None

            except Exception as e:
                logging.error(e)
                logging.info(
                    "Attempting again... {}/{}...".format(
                        i + 1, config.connection_attempts
                    )
                )
            if config.connection_attempts - i == 1:
                logging.info("Reconnecting...")
                self.__init__()

        return self.address, None
