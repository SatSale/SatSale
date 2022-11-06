import time
import logging
from typing import Tuple

import config
from node import node

# if False:  # config.tor_clightningrpc_host is not None:
#     from gateways.tor import session
# else:
#     import requests
#
#     session = None


class clightning(node.node):

    def __init__(self, node_config: dict):
        from pyln.client import LightningRpc

        super().__init__(node_config, False)

        for i in range(config.connection_attempts):
            try:
                if config.tunnel_host is None:
                    rpc_file = self.config['clightning_rpc_file']
                else:
                    rpc_file = "lightning-rpc"

                logging.info(
                    "Attempting to connect to clightning with unix domain socket: {}".format(
                        rpc_file
                    )
                )
                self.clightning = LightningRpc(rpc_file)

                logging.info("Getting clightning info...")
                info = self.clightning.getinfo()
                logging.info(info)

                logging.info("Successfully connected to clightning.")
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
                "Could not connect to clightning. Check your port tunneling settings and try again."
            )

        logging.info("Ready for payments requests.")
        return

    def get_info(self):
        return self.clightning.getinfo()

    def get_uri(self) -> str:
        info = self.get_info()
        address = info["address"][0]
        return info["id"] + "@" + address["address"] + ":" + str(address["port"])

    # Create lightning invoice
    def _create_clightning_invoice(self, btc_amount, label, expiry):
        # Multiplying by 10^8 to convert to satoshi units
        msats_amount = int(float(btc_amount) * 10 ** (3 + 8))
        lnd_invoice = self.clightning.invoice(
            msats_amount, label, label, expiry
        )
        return lnd_invoice["bolt11"], lnd_invoice["payment_hash"]

    def get_address(self, amount: float, label: str,
                    expiry: int) -> Tuple[str, str, str]:
        address, r_hash = self._create_clightning_invoice(amount, label, expiry)
        return None, address, r_hash

    # Check whether the payment has been paid
    def check_payment(self, uuid: str) -> Tuple[float, float]:
        invoices = self.clightning.listinvoices(uuid)["invoices"]

        if len(invoices) == 0:
            logging.error("Could not find invoice on node. Something's wrong.")
            return 0, 0

        invoice = invoices[0]

        if invoice["status"] != "paid":
            conf_paid = 0
            unconf_paid = 0
        else:
            # Store amount paid and convert to BTC units
            conf_paid = int(invoice["msatoshi_received"]) / 10 ** (3 + 8)
            unconf_paid = 0

        return conf_paid, unconf_paid
