import logging
import qrcode
import requests
import sys
import time
from bip_utils import Bip84, Bip44Changes, Bip84Coins, Bip44, Bip44Coins

from utils import btc_amount_format
from payments import database


class xpub:
    def __init__(self, node_config):
        self.is_onchain = True
        self.config = node_config
        self.api = "https://mempool.space/api"

        if "pytest" not in sys.modules:
            next_n = self.get_next_address_index(self.config["xpub"])
            # Warning will be printed for production runs, but not when running tests.
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

    def get_address(self, amount, label, expiry):
        while True:
            n = self.get_next_address_index(self.config["xpub"])
            address = self.get_address_at_index(n)
            database.add_generated_address(n, address, self.config["xpub"])
            conf_paid, unconf_paid = self.check_payment(address, slow=False)
            if conf_paid == 0 and unconf_paid == 0:
                break
        return address, None
