import json
import logging
import os
import qrcode
import requests
import time
from typing import Tuple

import config
from node.bip21 import encode_bip21_uri
from utils import btc_amount_format


class btcd:
    def __init__(self, node_config: dict) -> None:
        self.config = node_config
        self.is_onchain = True

        if self.config['tor_bitcoinrpc_host'] is not None:
            from gateways.tor import session
            self.session = session
            self.host = self.config['tor_bitcoinrpc_host']
        else:
            self.session = requests
            self.host = self.config['host']

        if self.config['rpc_cookie_file']:
            if os.path.isfile(self.config['rpc_cookie_file']):
                rpc_credentials_str = open(
                    self.config['rpc_cookie_file'], "r").read()
                (self.username, self.password) = rpc_credentials_str.split(":")
            else:
                raise RuntimeError(
                    "rpc_cookie_file {} not found".format(
                        self.config['rpc_cookie_file'])
                )
        else:
            self.username = self.config['username']
            self.password = self.config['password']

        for i in range(config.connection_attempts):
            if self.config['tor_bitcoinrpc_host'] is None:
                logging.info(
                    "Attempting to connect to Bitcoin node RPC to {}:{} with user {}.".format(
                        self.config['host'], self.config['rpcport'], self.config['username']
                    )
                )
            else:
                logging.info(
                    "Attempting to contact bitcoind rpc tor hidden service: {}:{}".format(
                        self.config['tor_bitcoinrpc_host'], self.config['rpcport']
                    )
                )

            try:
                info = self.call_bitcoin_rpc("getblockchaininfo")

                logging.info(info)
                logging.info("Successfully contacted bitcoind.")
                break

            except Exception as e:
                logging.error(e)
                if i < 5:
                    time.sleep(2)
                else:
                    time.sleep(60)
                logging.info(
                    "Attempting again... {}/{}...".format(
                        i + 1, config.connection_attempts
                    )
                )
        else:
            raise Exception(
                "Could not connect to bitcoind. \
                Check your RPC / port tunneling settings and try again."
            )

    def call_bitcoin_rpc(self, method: str, params: list = None) -> dict:
        payload = json.dumps({"method": method, "params": params})
        logging.debug(payload)
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache"
        }
        url = "http://{}:{}".format(self.host, self.config["rpcport"])
        if self.config["wallet"] is not None:
            url = url + "/wallet/{}".format(self.config["wallet"])
        response = self.session.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=(self.username, self.password),
        )
        response_data = json.loads(response.text)
        if response_data["error"] is not None:
            raise RuntimeError("Bitcoin RPC failed: {}".format(response_data["error"]))
        return response_data["result"]

    def create_qr(self, uuid: str, address: str, value: float) -> None:
        qr_str = encode_bip21_uri(address, {
            "amount": btc_amount_format(value),
            "label": uuid
        })
        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))
        return

    def check_payment(self, uuid: str) -> Tuple[float, float]:
        transactions = self.call_bitcoin_rpc("listtransactions", [uuid])

        conf_paid = 0
        unconf_paid = 0
        for tx in transactions:
            if tx["confirmations"] >= config.required_confirmations:
                conf_paid += tx["amount"]
            else:
                unconf_paid += tx["amount"]

        return conf_paid, unconf_paid

    def get_address(self, amount: float, label: str,
                    expiry: int) -> Tuple[str, str]:
        for i in range(config.connection_attempts):
            try:
                address = self.call_bitcoin_rpc("getnewaddress", [label])

                return address, None

            except Exception as e:
                logging.error(e)
                if i < 5:
                    time.sleep(2)
                else:
                    time.sleep(60)
                logging.info(
                    "Attempting again... {}/{}...".format(
                        i + 1, config.connection_attempts
                    )
                )
            if config.connection_attempts - i == 1:
                logging.info("Reconnecting...")
                self.__init__()
        return None
