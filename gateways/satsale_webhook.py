import hmac
import hashlib
import json
import codecs
import time
import requests
import logging

# Rough example of how you can implement a custom webhook using satsale
# See the woocommerce plugin php for an example of a recieving endpoint
def my_custom_webhook(satsale_secret, invoice, order_id):
    # Webhooks can have several security concerns depending on what they do
    # Outsiders must not be able to arbitrarily call the webhook without paying
    # Users must not be able to replay webhook calls (unique & one-time-use)

    # We're going to create two HMACs:
    # One using payment info for a secret_seed, which becomes the webhook secret
    # The other HMAC is on the webhook parameters, forming the webhook signature

    # This pattern must be repeated on the recieving end of the webhook, such that
    # the HMACs can be compared and verified as legitimately called from satsale.
    key = codecs.decode(satsale_secret, "hex")

    # Create a secret_seed for this payment, ensuring amount is not modified
    secret_seed = str(int(100 * float(invoice["fiat_value"]))).encode("utf-8")
    logging.info("Secret seed: {}".format(secret_seed))

    # HMAC this secret seed using satsale api key
    secret = hmac.new(key, secret_seed, hashlib.sha256).hexdigest()

    # Create webhook parameters and HMAC them
    paid_time = int(time.time())
    params = {"my_webhook_params": "pollofeedfan", "id": order_id}
    message = (str(paid_time) + "." + json.dumps(params, separators=(",", ":"))).encode(
        "utf-8"
    )
    hash = hmac.new(key, message, hashlib.sha256).hexdigest()

    # Include HMACs in webhook for verification on the other end
    headers = {
        "Content-Type": "application/json",
        "X-Signature": hash,
        "X-Secret": secret,
    }

    # Call the webhook with it's parameters and HMACs
    response = requests.get(invoice["webhook"], params=params, headers=headers)

    # SatSale likes response code 200
    return response


def woo_hook(satsale_secret, invoice, order_id):
    key = codecs.decode(satsale_secret, "hex")

    # Calculate a secret that is required to send back to the
    # woocommerce gateway, proving we did not modify id nor amount.
    secret_seed = str(int(100 * float(invoice["fiat_value"]))).encode("utf-8")
    logging.info("Secret seed: {}".format(secret_seed))

    secret = hmac.new(key, secret_seed, hashlib.sha256).hexdigest()

    # The main signature  which proves we have paid, and very recently!
    paid_time = int(time.time())
    params = {"wc-api": "wc_satsale_gateway", "time": str(paid_time), "id": order_id}
    message = (str(paid_time) + "." + json.dumps(params, separators=(",", ":"))).encode(
        "utf-8"
    )

    # Calculate the hash
    hash = hmac.new(key, message, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Signature": hash,
        "X-Secret": secret,
    }

    # Send the webhook response, confirming the payment with woocommerce.
    response = requests.get(invoice["webhook"], params=params, headers=headers)

    return response
