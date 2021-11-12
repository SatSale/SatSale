import subprocess
import pathlib
import time
import os
import json
import uuid
import qrcode


from payments.price_feed import get_btc_value
import config

# if False:  # config.tor_clightningrpc_host is not None:
#     from gateways.tor import session
# else:
#     import requests
#
#     session = None

class clightning:
    def __init__(self):
        from pyln.client import LightningRpc

        for i in range(config.connection_attempts):
            try:
                print("Attempting to connect to clightning...")
                self.clightning = LightningRpc(config.clightning_rpc_file)

                print("Getting clightning info...")
                info = self.clightning.getinfo()
                print(info)

                print("Successfully clightning lnd.")
                break

            except Exception as e:
                print(e)
                time.sleep(config.pollrate)
                print(
                    "Attempting again... {}/{}...".format(
                        i + 1, config.connection_attempts
                    )
                )
        else:
            raise Exception(
                "Could not connect to clightning. Check your port tunneling settings and try again."
            )

        print("Ready for payments requests.")
        return

    def create_qr(self, uuid, address, value):
        qr_str = "{}".format(address.upper())
        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(uuid))
        return

    # Create lightning invoice
    def create_clightning_invoice(self, btc_amount, label):
        # Multiplying by 10^8 to convert to satoshi units
        msats_amount = int(btc_amount * 10 ** (3+8))
        lnd_invoice = self.clightning.invoice(msats_amount, label, "SatSale-{}".format(label))
        return lnd_invoice["bolt11"], lnd_invoice["payment_hash"]

    def get_address(self, amount, label):
        address, r_hash = self.create_clightning_invoice(amount, label)
        return address, r_hash

    # Check whether the payment has been paid
    def check_payment(self, uuid):
        invoices = self.clightning.listinvoices(uuid)['invoices']

        if len(invoices) == 0:
            print("Could not find invoice on node. Something's wrong.")
            return 0, 0

        invoice = invoices[0]

        if invoice["status"] != "paid":
            conf_paid = 0
            unconf_paid = 0
        else:
            # Store amount paid and convert to BTC units
            conf_paid = int(invoice["msatoshi_received"]) / 10**(3+8)
            unconf_paid = 0

        return conf_paid, unconf_paid
