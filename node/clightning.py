import subprocess
import pathlib
import time
import os
import json
from base64 import b64decode
from google.protobuf.json_format import MessageToJson
import uuid
import qrcode


from payments.price_feed import get_btc_value
import config

if False:  # config.tor_clightningrpc_host is not None:
    from gateways.tor import session
else:
    import requests

    session = None


def call_clightning_rpc(method, params):
    url = "http://{}:{}@{}:{}".format(
        config.clightning_username,
        config.clightning_password,
        config.clightning_host,
        config.clightning_rpcport,
    )
    payload = json.dumps({"id": "satsale", "method": method, "params": params})
    if session is None:
        response = requests.request(
            "POST",
            url,
            data=payload,
            auth=(config.clightning_username, config.clightning_password),
        )
    else:
        response = session.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=(config.clightning_username, config.clightning_password),
        )
    return json.loads(response.text)


class clightning:
    def __init__(self):

        for i in range(config.connection_attempts):
            try:
                print("Attempting to connect to clightning...")

                print("Getting clightning info...")
                info = call_clightning_rpc("getinfo", [])
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
        sats_amount = int(btc_amount * 10 ** 8)
        res = call_clightning_rpc(
            "invoice", [sats_amount, label, "SatSale-{}".format(label)]
        )
        lnd_invoice = res["result"]

        return lnd_invoice["bolt11"], lnd_invoice["payment_hash"]

    def get_address(self, amount, label):
        address, r_hash = self.create_clightning_invoice(amount, label)
        return address, r_hash

    # Check whether the payment has been paid
    def check_payment(self, uuid):
        res = call_clightning_rpc("listinvoices", [uuid])

        if len(res["result"]["invoices"]) == 0:
            print("Could not look up invoice on node")
            print(res)
            return 0, 0

        invoice_status = res["result"]["invoices"][0]

        if invoice_status["status"] != "paid":
            conf_paid = 0
            unconf_paid = 0
        else:
            # Store amount paid and convert to BTC units
            conf_paid = (int(invoice_status["msatoshi"]) / 10 ** 3) / (10 ** 8)
            unconf_paid = 0

        return conf_paid, unconf_paid
