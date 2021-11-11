from flask import request
from flask_restplus import Resource, Api, Namespace, fields
import hashlib

import config

min_sats = 10**2
max_sats = 10**6

# Following https://github.com/andrerfneves/lightning-address/blob/master/DIY.md

description = config.lightning_address_comment
if description is None:
    description = "Thank you for your support <3"

metadata =  "[[\"text/plain\", \"{}\"], [\"text/identifier\", \"{}\"]]".format(description, config.lightning_address.split("@")[0])

def add_ln_address_decorators(app, api, node):
    class get_ln_address(Resource):
        def get(self):
            try:
                print("Someone requested our ln address: {}!".format(config.lightning_address))
                resp = {
                    "callback": "http://{}/lnaddr".format(config.lightning_address.split("@")[1]),
                    "maxSendable": min_sats*10**3,
                    "minSendable": max_sats*10**3,
                    "metadata": metadata,
                    "tag": "payRequest"
                    }
                return resp

            except Exception as e:
                print(e)
                return {"status": "ERROR", "reason": e}



    class init_ln_addr_payment(Resource):
        def get(self):
            if request.args.get("amount") is None:
                return {"status": "ERROR", "reason": "You need to request an ?amount=MSATS"}

            amount_msats = int(request.args.get("amount"))
            amount_btc = amount_msats / 10**(3+8)

            print("Received payment request from ln address for {} msats...".format(amount_msats))

            description_hash = hashlib.sha256(metadata.encode()).digest()

            try:
                invoice, _ = node.create_lnd_invoice(amount_btc, memo="lightning address payment", description_hash=description_hash)
                print("Responding with invoice {}".format(invoice))
                return {
                    	"pr": invoice,
                    	"routes": []
                    }
            except Exception a e:
                print(e)
                return {"status": "ERROR", "reason": e}


    api.add_resource(get_ln_address, "/.well-known/lnurlp/{}".format(config.lightning_address.split("@")[0]))
    api.add_resource(init_ln_addr_payment, "/lnaddr")
    return
