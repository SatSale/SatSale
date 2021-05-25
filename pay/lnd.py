import subprocess
import pathlib
import time
import os
import json
from base64 import b64decode
from google.protobuf.json_format import MessageToJson
import uuid
import qrcode


from invoice.price_feed import get_btc_value
import config

class lnd():
    def __init__(self):
        from lndgrpc import LNDClient

        # Copy admin macaroon and tls cert to local machine
        self.copy_certs()

        # Conect to lightning node
        connection_str = "{}:{}".format(config.host, config.lnd_rpcport)
        print(
            "Attempting to connect to lightning node {}. This may take a few minutes...".format(
                connection_str
            )
        )

        for i in range(config.connection_attempts):
            try:
                print("Attempting to initialise lnd rpc client...")
                time.sleep(3)
                self.lnd = LNDClient(
                    "{}:{}".format(config.host, config.lnd_rpcport),
                    macaroon_filepath=self.certs['macaroon'],
                    cert_filepath=self.certs['tls'],
                )


                print("Getting lnd info...")
                info = self.lnd.get_info()
                print(info)

                print("Successfully contacted lnd.")
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
                "Could not connect to lnd. Check your gRPC / port tunneling settings and try again."
            )

        print("Ready for payments requests.")
        return

    def invoice(self, dollar_value, currency, label):
        self.dollar_value = dollar_value
        self.currency = currency
        self.value = round(get_btc_value(dollar_value, currency), 8)
        self.uuid = str(uuid.uuid4())
        self.label = self.uuid
        self.status = "Payment initialised."
        self.response = ""
        self.time_left = config.payment_timeout
        self.confirmed_paid = 0
        self.unconfirmed_paid = 0
        self.paid = False
        self.txid = ""
        return

    def create_qr(self):
        qr_str = "{}".format(self.address.upper())
        img = qrcode.make(qr_str)
        img.save("static/qr_codes/{}.png".format(self.uuid))
        return

    # Copy tls and macaroon certs from remote machine.
    def copy_certs(self):
        self.certs = {'tls' : 'tls.cert', 'macaroon' : 'admin.macaroon'}

        if (not os.path.isfile("tls.cert")) or (not os.path.isfile("admin.macaroon")):
            try:
                tls_file = os.path.join(config.lnd_dir, "tls.cert")
                macaroon_file = os.path.join(
                    config.lnd_dir, "data/chain/bitcoin/mainnet/admin.macaroon"
                )

                # SSH copy
                if config.tunnel_host is not None:
                    print(
                        "Could not find tls.cert or admin.macaroon in SatSale folder. \
                         Attempting to download from remote lnd directory."
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
                    self.certs = {'tls' : os.path.expanduser(tls_file),
                                    'macaroon' : os.path.expanduser(macaroon_file)}

            except Exception as e:
                print(e)
                print("Failed to copy tls and macaroon files to local machine.")
        else:
            print("Found tls.cert and admin.macaroon.")
        return

    # Create lightning invoice
    def create_lnd_invoice(self, btc_amount):
        # Multiplying by 10^8 to convert to satoshi units
        sats_amount = int(btc_amount * 10 ** 8)
        res = self.lnd.add_invoice(value=sats_amount)
        self.lnd_invoice = json.loads(MessageToJson(res))
        self.hash = self.lnd_invoice["r_hash"]

        print("Created lightning invoice:")
        print(self.lnd_invoice)

        return self.lnd_invoice["payment_request"]

    def get_address(self):
        self.address = self.create_lnd_invoice(self.value)
        return

    # Check whether the payment has been paid
    def check_payment(self):
        print("Looking up invoice")

        invoice_status = json.loads(
            MessageToJson(
                self.lnd.lookup_invoice(r_hash_str=b64decode(self.hash).hex())
            )
        )

        if "amt_paid_sat" not in invoice_status.keys():
            conf_paid = 0
            unconf_paid = 0
        else:
            # Store amount paid and convert to BTC units
            conf_paid = int(invoice_status["amt_paid_sat"]) * 10 ** 8
            unconf_paid = 0

        return conf_paid, unconf_paid
