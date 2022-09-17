from flask import request
from flask_restx import Resource
import hashlib
import logging

min_sats = 10 ** 2
max_sats = 10 ** 6

# Following https://github.com/andrerfneves/lightning-address/blob/master/DIY.md


def add_ln_address_decorators(app, api, node):
    description = node.config['lightning_address_comment']
    address = node.config['lightning_address']
    if description is None:
        description = "Thank you for your support <3"

    metadata = '[["text/plain", "{}"], ["text/identifier", "{}"]]'.format(
        description, address.split("@")[0]
    )

    class get_ln_address(Resource):
        def get(self):
            try:
                logging.info(
                    "Someone requested our ln address: {}!".format(
                        address
                    )
                )
                resp = {
                    "callback": "https://{}/lnaddr".format(
                        address.split("@")[1]
                    ),
                    "maxSendable": max_sats * 10 ** 3,
                    "minSendable": min_sats * 10 ** 3,
                    "metadata": metadata,
                    "tag": "payRequest",
                }
                return resp

            except Exception as e:
                logging.error(e)
                return {"status": "ERROR", "reason": e}

    class init_ln_addr_payment(Resource):
        def get(self):
            if request.args.get("amount") is None:
                return {
                    "status": "ERROR",
                    "reason": "You need to request an ?amount=MSATS",
                }

            amount_msats = int(request.args.get("amount"))
            amount_btc = amount_msats / 10 ** (3 + 8)

            logging.info(
                "Received payment request from ln address for {} msats...".format(
                    amount_msats
                )
            )

            description_hash = hashlib.sha256(metadata.encode()).digest()

            try:
                invoice, _ = node.create_lnd_invoice(
                    amount_btc,
                    memo="lightning address payment",
                    description_hash=description_hash,
                )
                logging.info("Responding with invoice {}".format(invoice))
                return {"pr": invoice, "routes": []}
            except Exception as e:
                logging.error(e)
                return {"status": "ERROR", "reason": e}

    api.add_resource(
        get_ln_address,
        "/.well-known/lnurlp/{}".format(address.split("@")[0]),
    )
    api.add_resource(init_ln_addr_payment, "/lnaddr")
    return
