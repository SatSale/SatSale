import time
import uuid
import qrcode
import json
import os
import logging
import requests
from btclib import bip32, slip132

import config
from payments.price_feed import get_btc_value
from payments import database

if config.tor_bitcoinrpc_host is not None:
    from gateways.tor import session


class pseudonode:
    def __init__(self):
        self.is_onchain = True
        self.api = "https://mempool.space/api"
        self.address_counter_file = "address_counter"
        if not database.check_address_table_exists():
            database.create_address_table()

        logging.info("Fetching blockchain info from {}".format(self.api))
        logging.info(
            "Next address shown to users is #{}".format(self.get_next_address_index())
        )

    def create_qr(self, uuid, address, value):
        qr_str = "{}?amount={}&label={}".format(address.upper(), value, uuid)

        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))
        return

    def check_payment(self, address):
        conf_paid, unconf_paid = 0, 0
        try:
            r = requests.get(self.api + "/address/{}".format(address))
            r.raise_for_status()
            stats = r.json()
            conf_paid = stats["chain_stats"]["funded_txo_sum"] / (10 ** 8)
            unconf_paid = stats["mempool_stats"]["funded_txo_sum"] / (10 ** 8)
            time.sleep(2)
            return conf_paid, unconf_paid

        except Exception as e:
            logging.error(
                "Failed to fetch address information from mempool: {}".format(e)
            )

        return 0, 0

    def get_next_address_index(self):
        n = database.get_next_address_index()
        return n

    def get_address(self, amount, label):
        n = self.get_next_address_index()
        xpub = bip32.derive(xkey=config.zpub, der_path="m/84'/0'/0'/0/{}".format(n))
        address = slip132.address_from_xpub(xpub)

        database.add_generated_address(n, address)

        return address, None
