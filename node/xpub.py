import logging
import requests
import sys
import time
from base58 import b58decode_check, b58encode_check
from bip_utils import \
    Bip44, Bip44Changes, Bip44Coins, \
    Bip84, Bip84Coins, \
    Bip86, Bip86Coins
from typing import Tuple

from node import node
from payments import database


class InvalidExtendedPublicKeyError(RuntimeError):

    def __init__(self, xpub: str, bip: str) -> None:
        self.message = "Invalid extended public key {} for {}".format(
            xpub, bip)
        super().__init__(self.message)


class xpub(node.node):

    def __init__(self, node_config: dict) -> None:

        super().__init__(node_config, True)

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

            logging.info("Fetching blockchain info from {}".format(
                self.config["api_url"]))
            logging.info("Next address shown to users is #{}".format(next_n))

    def get_info(self):
        return self.config["api_url"]

    def check_payment(self, address: str, slow: bool = True) -> Tuple[float, float]:
        conf_paid, unconf_paid = 0, 0
        try:
            r = requests.get("{}/address/{}".format(
                self.config["api_url"], address))
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

    def get_next_address_index(self, xpub: str) -> int:
        n = database.get_next_address_index(xpub)
        return n

    # Converts xpub/tpub to zpub/vpub (for BIP84).
    # Some wallets (JoinMarket, Wasabi Wallet, descriptor wallets) will show
    # xpub/tpub instead of zpub/vpub for BIP84.
    def _zpub_from_xpub(self, xpub: str) -> str:
        zpub_prefix = b"\x04\xb2\x47\x46"
        vpub_prefix = b"\x04\x5f\x1c\xf6"
        if xpub.startswith("xpub"):
            return b58encode_check(zpub_prefix +
                                   b58decode_check(xpub)[4:]).decode("ascii")
        elif xpub.startswith("tpub"):
            return b58encode_check(vpub_prefix +
                                   b58decode_check(xpub)[4:]).decode("ascii")
        else:
            raise InvalidExtendedPublicKeyError(xpub, "BIP84")

    def get_address_at_index(self, index: int) -> str:
        if self.config["bip"] == "BIP44":
            if self.config["xpub"].startswith("xpub"):
                bip44_acc = Bip44.FromExtendedKey(self.config["xpub"],
                                                  Bip44Coins.BITCOIN)
            elif self.config["xpub"].startswith("tpub"):
                bip44_acc = Bip44.FromExtendedKey(self.config["xpub"],
                                                  Bip44Coins.BITCOIN_TESTNET)
            else:
                raise InvalidExtendedPublicKeyError(
                    self.config["xpub"], self.config["bip"])
            child_key = bip44_acc.Change(Bip44Changes.CHAIN_EXT).AddressIndex(index)
        elif self.config["bip"] == "BIP84":
            if self.config["xpub"].startswith("zpub"):
                bip84_acc = Bip84.FromExtendedKey(self.config["xpub"],
                                                  Bip84Coins.BITCOIN)
            elif self.config["xpub"].startswith("vpub"):
                bip84_acc = Bip84.FromExtendedKey(self.config["xpub"],
                                                  Bip84Coins.BITCOIN_TESTNET)
            elif self.config["xpub"].startswith("xpub"):
                bip84_acc = Bip84.FromExtendedKey(self._zpub_from_xpub(self.config["xpub"]),
                                                  Bip84Coins.BITCOIN)
            elif self.config["xpub"].startswith("tpub"):
                bip84_acc = Bip84.FromExtendedKey(self._zpub_from_xpub(self.config["xpub"]),
                                                  Bip84Coins.BITCOIN_TESTNET)
            else:
                raise InvalidExtendedPublicKeyError(
                    self.config["xpub"], self.config["bip"])
            child_key = bip84_acc.Change(Bip44Changes.CHAIN_EXT).AddressIndex(index)
        elif self.config["bip"] == "BIP86":
            if self.config["xpub"].startswith("xpub"):
                bip86_acc = Bip86.FromExtendedKey(self.config["xpub"],
                                                  Bip86Coins.BITCOIN)
            elif self.config["xpub"].startswith("tpub"):
                bip86_acc = Bip86.FromExtendedKey(self.config["xpub"],
                                                  Bip86Coins.BITCOIN_TESTNET)
            else:
                raise InvalidExtendedPublicKeyError(
                    self.config["xpub"], self.config["bip"])
            child_key = bip86_acc.Change(Bip44Changes.CHAIN_EXT).AddressIndex(index)
        else:
            raise NotImplementedError(
                "{} is not yet implemented!".format(self.config["bip"])
            )

        address = child_key.PublicKey().ToAddress()
        return address

    def get_address(self, amount: float, label: str,
                    expiry: int) -> Tuple[str, str, str]:
        while True:
            n = self.get_next_address_index(self.config["xpub"])
            address = self.get_address_at_index(n)
            database.add_generated_address(n, address, self.config["xpub"])
            conf_paid, unconf_paid = self.check_payment(address, slow=False)
            if conf_paid == 0 and unconf_paid == 0:
                break
        return address, None, None
