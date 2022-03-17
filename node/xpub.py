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
from utils import btc_amount_format
from payments import database

if config.tor_bitcoinrpc_host is not None:
    from gateways.tor import session


class xpub:
    def __init__(self, xpub):
        self.xpub_key = xpub
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
        qr_str = "bitcoin:{}?amount={}&label={}".format(
            address, btc_amount_format(value), uuid)


        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))
        return

    def check_payment(self, address, slow=True):
        conf_paid, unconf_paid = 0, 0
        try:
            r = requests.get(self.api + "/address/{}".format(address))
            r.raise_for_status()
            stats = r.json()
            conf_paid = stats["chain_stats"]["funded_txo_sum"] / (10 ** 8)
            unconf_paid = stats["mempool_stats"]["funded_txo_sum"] / (10 ** 8)

            # Don't request too often
            if slow and (conf_paid == 0):
                time.sleep(1)

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
        while True:
            n = self.get_next_address_index()
            # xpub = bip32.derive(xkey=config.xpub, der_path="m/84'/0/0/0/{}".format(n))        
            xpub = bip32.derive(xkey=config.xpub, der_path="0/{}".format(n))        
            address = slip132.address_from_xpub(xpub)
            database.add_generated_address(n, address)
            conf_paid, unconf_paid = self.check_payment(address, slow=False)
            if conf_paid == 0 and unconf_paid == 0:
                break
        return address, None
