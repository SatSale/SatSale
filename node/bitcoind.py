import json
import os
import qrcode
import time
import logging
logger = logging.getLogger(__name__)

import config
from utils import btc_amount_format


class btcd:
    def __init__(self, node_config):
        from bitcoinrpc.authproxy import AuthServiceProxy
        self.config = node_config

        if self.config['tor_bitcoinrpc_host'] is not None:
            from gateways.tor import session
            self.session = session
        self.is_onchain = True

        if self.config['rpc_cookie_file']:
            if os.path.isfile(self.config['rpc_cookie_file']):
                rpc_credentials_str = open(self.config['rpc_cookie_file'], "r").read()
                (username, password) = rpc_credentials_str.split(":")
            else:
                raise Exception(
                    "rpc_cookie_file {} not found".format(self.config['rpc_cookie_file'])
                )
        else:
            username = self.config['username']
            password = self.config['password']

        for i in range(config.connection_attempts):
            if self.config['tor_bitcoinrpc_host'] is None:
                self.tor = False
                connection_str = "http://{}:{}@{}:{}/wallet/{}".format(
                    username,
                    password,
                    self.config['host'],
                    self.config['rpcport'],
                    self.config['wallet'],
                )
                logging.info(
                    "Attempting to connect to Bitcoin node RPC to {}:{} with user {}.".format(
                        self.config['host'], self.config['rpcport'], self.config['username']
                    )
                )
            else:
                self.tor = True
                logging.info(
                    "Attempting to contact bitcoind rpc tor hidden service: {}:{}".format(
                        self.config['tor_bitcoinrpc_host'], self.config['rpcport']
                    )
                )

            try:
                # Normal Connection
                if self.config['tor_bitcoinrpc_host'] is None:
                    self.rpc = AuthServiceProxy(connection_str)
                    info = self.rpc.getblockchaininfo()
                # Tor Connection
                else:
                    info = self.call_tor_bitcoin_rpc("getblockchaininfo", None)

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

    def call_tor_bitcoin_rpc(self, method, params):
        url = "{}:{}".format(self.config['tor_bitcoinrpc_host'], config.rpcport)
        payload = json.dumps({"method": method, "params": params})
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
        response = self.session.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=(config.username, config.password),
        )
        return json.loads(response.text)

    def create_qr(self, uuid, address, value):
        qr_str = "bitcoin:{}?amount={}&label={}".format(
            address, btc_amount_format(value), uuid
        )

        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))
        return

    def check_payment(self, uuid):
        if not self.tor:
            transactions = self.rpc.listtransactions(uuid)
        else:
            transactions = self.call_tor_bitcoin_rpc("listtransactions", [uuid])["result"]

        conf_paid = 0
        unconf_paid = 0
        for tx in transactions:
            if tx["confirmations"] >= config.required_confirmations:
                conf_paid += tx["amount"]
            else:
                unconf_paid += tx["amount"]

        return conf_paid, unconf_paid

    def get_address(self, amount, label, expiry):
        for i in range(config.connection_attempts):
            try:
                if not self.tor:
                    address = self.rpc.getnewaddress(label)
                else:
                    address = self.call_tor_bitcoin_rpc("getnewaddress", [label])["result"]

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
