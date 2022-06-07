import time
import qrcode
import config
import logging
logger = logging.getLogger(__name__)

# if False:  # config.tor_clightningrpc_host is not None:
#     from gateways.tor import session
# else:
#     import requests
#
#     session = None


class clightning:
    def __init__(self, node_config):
        from pyln.client import LightningRpc

        self.config = node_config
        self.is_onchain = False

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

    def create_qr(self, uuid, address, value):
        qr_str = "{}".format(address.upper())
        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))
        return

    def get_info(self):
        return self.clightning.getinfo()

    def get_uri(self):
        info = self.get_info()
        address = info["address"][0]
        return info["id"] + "@" + address["address"] + ":" + str(address["port"])

    # Create lightning invoice
    def create_clightning_invoice(self, btc_amount, label, expiry):
        # Multiplying by 10^8 to convert to satoshi units
        msats_amount = int(float(btc_amount) * 10 ** (3 + 8))
        lnd_invoice = self.clightning.invoice(
            msats_amount, label, "SatSale-{}".format(label), expiry
        )
        return lnd_invoice["bolt11"], lnd_invoice["payment_hash"]

    def get_address(self, amount, label, expiry):
        address, r_hash = self.create_clightning_invoice(amount, label, expiry)
        return address, r_hash

    # Check whether the payment has been paid
    def check_payment(self, uuid):
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
