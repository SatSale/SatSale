import config
import subprocess
import time
import os
import json
from base64 import b64decode
from google.protobuf.json_format import MessageToJson

from invoice.payment_invoice import invoice

class lnd(invoice):
    def __init__(self, dollar_value, currency, label):
        super().__init__(dollar_value, currency, label)
        print(self.__dict__)

        from lndgrpc import LNDClient

        # Copy admin macaroon and tls cert to local machine
        try:
            tls_file = os.path.join(config.lnd_dir, "tls.cert")
            macaroon_file = os.path.join(config.lnd_dir, "data/chain/bitcoin/mainnet/admin.macaroon")
            subprocess.run(["scp", "{}:{}".format(config.tunnel_host, tls_file), "."])
            subprocess.run(["scp", "-r", "{}:{}".format(config.tunnel_host, macaroon_file), "."])

        except Exception as e:
            print(e)
            print("Failed to copy tls and macaroon files to local machine.")

        connection_str = "{}:{}".format(config.host, config.rpcport)
        print("Attempting to connect to {}. This may take a few minutes...".format(connection_str))

        for i in range(config.connection_attempts):
            try:
                # Require admin=True for creating invoices
                print("Attempting to initialise lnd rpc client...")
                self.lnd = LNDClient("{}:{}".format(config.host, config.rpcport),
                                    admin=True,
                                    macaroon_filepath="admin.macaroon",
                                    cert_filepath="tls.cert")

                # print("Getting lnd info...")
                # info = self.lnd.get_info()
                # print(info)

                print("Successfully contacted lnd.")
                break

            except Exception as e:
                print(e)
                time.sleep(config.pollrate)
                print("Attempting again... {}/{}...".format(i+1, config.connection_attempts))
        else:
            raise Exception("Could not connect to lnd. Check your gRPC / port tunneling settings and try again.")


    def create_lnd_invoice(self, btc_amount):
        # Multiplying by 10^8 to convert to satoshi units
        sats_amount = int(btc_amount*10**8)
        self.lnd_invoice = json.loads(MessageToJson(self.lnd.add_invoice(sats_amount)))
        print(self.lnd_invoice)
        print("printed")

        self.hash = str(b64decode(self.lnd_invoice['r_hash']).hex())
        # self.hash = str(b64decode(self.lnd_invoice['rHash']).hex())

        print("Created invoice: {}".format(self.hash))
        return self.lnd_invoice['payment_request']
        # return self.lnd_invoice['paymentRequest']


    def get_address(self):
        for i in range(config.connection_attempts):
            try:
                self.address = self.create_lnd_invoice(self.value)
            except Exception as e:
                print(e)
                print("Attempting again... {}/{}...".format(i+1, config.connection_attempts))

        return

    def check_payment(self):
        print("Looking up...")
        # For some reason this does not work, I think lookup_invoice() may be broken
        # as it does not return the correct response that includes the amount paid among other fields.
        print(self.lnd.lookup_invoice(self.hash))
        # invoice_status = json.loads(MessageToJson(self.lnd.lookup_invoice(self.hash)))
        # print(invoice_status)
        # print(self.lnd.lookup_invoice("8893044a07c2c5e2a50252f044224f297487242e05758a970d5ba28ece75f66d"))
        # subprocess.run([""])

        conf_paid = 0 #invoice_status['amt_paid']
        unconf_paid = 0
        return conf_paid, unconf_paid
