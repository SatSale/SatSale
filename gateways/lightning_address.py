from flask import request
from flask_restplus import Resource, Api, Namespace, fields
import config
import hashlib

description = "ty for donations"

def add_ln_address_decorators(app, api, node):
    class get_ln_address(Resource):
        def get(self):
            print("Someone requested our ln address: {}!".format(config.lightning_address))
            resp = {
                "callback": "http://{}/lnaddr".format(config.lightning_address.split("@")[1]),
                "maxSendable": 10**(3+7),
                "minSendable": 1000*10**2,
                "metadata": "[[\"text/plain\", \"{}\"], [\"text/identifier\", \"{}\"]]".format(memo, config.lightning_address),
                "tag": "payRequest"
                }
            return resp



    class init_ln_addr_payment(Resource):
        def get(self):
            amount_msats = int(request.args.get("amount"))
            amount_btc = amount_msats / 10**(3+8)
            print("Received payment request from ln address for {} msats...".format(amount_msats))

            description_hash = hashlib.sha256(description.encode()).digest()

            invoice, _ = node.create_lnd_invoice(amount_btc, memo="lightning address payment", description_hash=description_hash)
            print("Responding with invoice {}".format(invoice))
            return {
                	"pr": invoice,
                	"routes": []
                }

    api.add_resource(get_ln_address, "/.well-known/lnurlp/{}".format(config.lightning_address.split("@")[0]))
    api.add_resource(init_ln_addr_payment, "/lnaddr")
    return
