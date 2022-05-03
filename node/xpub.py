import time
import uuid
import qrcode
import json
import os
import logging
import requests
from bip_utils import Bip84, Bip44Changes, Bip84Coins, Bip44, Bip44Coins

import config
from payments.price_feed import get_btc_value
from utils import btc_amount_format
from payments import database


class xpub:
    def __init__(self, node_config):
        self.is_onchain = True
        self.config = node_config
        self.api = "https://mempool.space/api"

        next_n = self.get_next_address_index(self.config["xpub"])
        if next_n == 0:
            logging.info(
                "Deriving addresses for first time from xpub: {}".format(
                    self.config["xpub"]
                )
            )
            logging.warn(
                "YOU MUST CHECK THIS MATCHES THE FIRST ADDRESS IN YOUR WALLET:"
            )
            logging.warn(self.get_address_at_index(next_n))
            time.sleep(10)

        logging.info("Fetching blockchain info from {}".format(self.api))
        logging.info("Next address shown to users is #{}".format(next_n))

    def create_qr(self, uuid, address, value):
        qr_str = "bitcoin:{}?amount={}&label={}".format(
            address, btc_amount_format(value), uuid
        )

        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))

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

    def get_next_address_index(self, xpub):
        n = database.get_next_address_index(xpub)
        return n

    def get_address_at_index(self, index):
        if self.config["bip"] == "BIP84":
            bip84_acc = Bip84.FromExtendedKey(self.config["xpub"], Bip84Coins.BITCOIN)
            child_key = bip84_acc.Change(Bip44Changes.CHAIN_EXT).AddressIndex(index)
        elif self.config["bip"] == "BIP44":
            bip44_acc = Bip44.FromExtendedKey(self.config["xpub"], Bip44Coins.BITCOIN)
            child_key = bip44_acc.Change(Bip44Changes.CHAIN_EXT).AddressIndex(index)
        else:
            raise NotImplementedError(
                "{} is not yet implemented!".format(self.config["bip"])
            )

        address = child_key.PublicKey().ToAddress()
        return address

    def get_address(self):
        while True:
            n = self.get_next_address_index(self.config["xpub"])
            address = self.get_address_at_index(n)
            database.add_generated_address(n, address, self.config["xpub"])
            conf_paid, unconf_paid = self.check_payment(address, slow=False)
            if conf_paid == 0 and unconf_paid == 0:
                break
        return address, None


def test():
    # Account 0, root = m/84'/0'/0'
    test_zpub = "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
    pseudonode = xpub({"xpub": test_zpub, "bip": "BIP84"})
    assert (
        pseudonode.get_address_at_index(0)
        == "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"
    )
    assert (
        pseudonode.get_address_at_index(1)
        == "bc1qnjg0jd8228aq7egyzacy8cys3knf9xvrerkf9g"
    )
    print("BIP84 test succeded")

    test_xpub = "xpub6C5uh2bEhmF8ck3LSnNsj261dt24wrJHMcsXcV25MjrYNo3ZiduE3pS2Xs7nKKTR6kGPDa8jemxCQPw6zX2LMEA6VG2sypt2LUJRHb8G63i"
    pseudonode2 = xpub({"xpub": test_xpub, "bip": "BIP44"})
    assert pseudonode2.get_address_at_index(0) == "1LLNwhAMsS3J9tZR2T4fFg2ibuZyRSxFZg"
    assert pseudonode2.get_address_at_index(1) == "1EaEuwMRVKdWBoKeJZzJ8abUzVbWNhGhtC"
    print("BIP44 test succeded")