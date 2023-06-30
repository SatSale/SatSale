import subprocess
import time
import os
import json
from base64 import b64decode
from google.protobuf.json_format import MessageToJson
from typing import Tuple

import config
import logging
from node import node


class lnd(node.node):

    def __init__(self, node_config: dict) -> None:
        from lndgrpc import LNDClient

        super().__init__(node_config, False)

        # Copy admin macaroon and tls cert to local machine
        self._copy_certs()

        # Conect to lightning node
        connection_str = "{}:{}".format(self.config['host'], self.config['lnd_rpcport'])
        logging.info(
            "Attempting to connect to lightning node {}. This may take a few seconds...".format(
                connection_str
            )
        )

        for i in range(config.connection_attempts):
            try:
                logging.info("Attempting to initialise lnd rpc client...")
                time.sleep(3)
                self.lnd = LNDClient(
                    "{}:{}".format(self.config['host'], self.config['lnd_rpcport']),
                    macaroon_filepath=self.certs["macaroon"],
                    cert_filepath=self.certs["tls"],
                )

                if "invoice" in self.certs["macaroon"]:
                    logging.info("Testing we can fetch invoices...")
                    inv, _ = self.create_lnd_invoice(0)
                    logging.info(inv)
                else:
                    logging.info("Getting lnd info...")
                    info = self.get_info()
                    logging.info(info)

                logging.info("Successfully contacted lnd.")
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
                "Could not connect to lnd. Check your gRPC / port tunneling settings and try again."
            )

        logging.info("Ready for payments requests.")
        return

    # Copy tls and macaroon certs from remote machine.
    def _copy_certs(self) -> None:
        self.certs = {"tls": "tls.cert", "macaroon": self.config['lnd_macaroon']}

        if (not os.path.isfile("tls.cert")) or (
            not os.path.isfile(self.config['lnd_macaroon'])
        ):
            try:
                tls_file = os.path.join(self.config['lnd_dir'], "tls.cert")
                macaroon_file = os.path.join(
                    self.config['lnd_dir'],
                    "data/chain/bitcoin/mainnet/{}".format(self.config['lnd_macaroon']),
                )

                # SSH copy
                if config.tunnel_host is not None:
                    logging.warning(
                        "Could not find tls.cert or {} in SatSale folder. \
                         Attempting to download from remote lnd directory.".format(
                            self.config['lnd_macaroon']
                        )
                    )

                    subprocess.run(
                        ["scp", "{}:{}".format(config.tunnel_host, tls_file), "."]
                    )
                    subprocess.run(
                        [
                            "scp",
                            "-r",
                            "{}:{}".format(config.tunnel_host, macaroon_file),
                            ".",
                        ]
                    )

                else:
                    self.certs = {
                        "tls": os.path.expanduser(tls_file),
                        "macaroon": os.path.expanduser(macaroon_file),
                    }

            except Exception as e:
                logging.error(e)
                logging.error("Failed to copy tls and macaroon files to local machine.")
        else:
            logging.info("Found tls.cert and admin.macaroon.")
        return

    # Create lightning invoice
    def create_lnd_invoice(
        self,
        btc_amount: float,
        memo: str = None,
        description_hash: str = None,
        expiry: int = 3600,
    ) -> Tuple[str, str]:
        # Multiplying by 10^8 to convert to satoshi units
        sats_amount = int(float(btc_amount) * 10 ** 8)
        res = self.lnd.add_invoice(
            value=sats_amount, memo=memo, description_hash=description_hash, expiry=expiry
        )
        lnd_invoice = json.loads(MessageToJson(res))

        return lnd_invoice["paymentRequest"], lnd_invoice["rHash"]

    def get_address(self, amount: float, label: str,
                    expiry: int) -> Tuple[str, str, str]:
        address, r_hash = self.create_lnd_invoice(
            amount, memo=label, expiry=expiry)
        return None, address, r_hash

    def pay_invoice(self, bolt11_invoice: str) -> None:
        ret = json.loads(
            MessageToJson(self.lnd.send_payment(bolt11_invoice, fee_limit_msat=20 * 1000))
        )
        logging.info(ret)
        return

    def get_info(self):
        return json.loads(MessageToJson(self.lnd.get_info()))

    def get_uri(self) -> str:
        info = self.get_info()
        return info["uris"][0]

    # Check whether the payment has been paid
    def check_payment(self, rhash: str) -> Tuple[float, float]:
        invoice_status = json.loads(
            MessageToJson(self.lnd.lookup_invoice(r_hash_str=b64decode(rhash).hex()))
        )

        if "amtPaidSat" not in invoice_status.keys():
            conf_paid = 0
            unconf_paid = 0
        else:
            # Store amount paid and convert to BTC units
            conf_paid = (int(invoice_status["amtPaidSat"]) + 1) / (10 ** 8)
            unconf_paid = 0

        return conf_paid, unconf_paid
