from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
import time
import os

import ssh_tunnel
import config
import invoice
from pay import bitcoind
from pay import lnd
from gateways import woo_webhook

# Begin websocket
async_mode = None
app = Flask(__name__)

# Load an API key or create a new one
if os.path.exists("SatSale_API_key"):
    with open("SatSale_API_key", "r") as f:
        app.config["SECRET_KEY"] = f.read().strip()
else:
    with open("SatSale_API_key", "w") as f:
        app.config["SECRET_KEY"] = os.urandom(64).hex()
        f.write(app.config["SECRET_KEY"])

print("Initialised Flask with secret key: {}".format(app.config["SECRET_KEY"]))

# cors_allowed_origins * allows for webhooks to be initiated from iframes.
socket_ = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")


# Basic return on initialisation
@socket_.on("initialise")
def test_message(message):
    emit(
        "payresponse",
        {
            "status": "Initialising payment...",
            "time_left": 0,
            "response": "Initialising payment...",
        },
    )


# Render index page
# This is currently a donation page that submits to /pay
@app.route("/")
def index():
    # Render donation page
    return render_template("donate.html", async_mode=socket_.async_mode)


# /pay is the main payment method for initiating a payment websocket.
@app.route("/pay")
def payment_page():
    params = dict(request.args)
    params['lnd_enabled'] = (config.pay_method == "lnd")
    # Render payment page with the request arguments (?amount= etc.)
    return render_template("index.html", params=params, async_mode=socket_.async_mode)


# Websocket payment processing method called by client
# initiate_payment recieves amount and initiates invoice and payment processing.
@socket_.on("initiate_payment")
def initiate_payment(payload):
    # Check the amount is a float
    amount = payload["amount"]
    try:
        amount = float(amount)
    except Exception as e:
        update_status(payment, "Invalid amount.")
        amount = None
        return

    # Label as a donation if the id is missing
    if "id" in payload.keys():
        label = payload["id"]
    else:
        label = "donation"

    # Get payment method, use one specified in query string if provided
    if "method" in payload.keys():
            payment_method = payload['method']
    else:
        payment_method = config.pay_method

    # Initialise the payment invoice
    payment = create_invoice(amount, "USD", label, payment_method)

    # Wait for the amount to be sent to the address
    process_payment(payment)

    # On successful payment
    if payment.paid:
        update_status(payment, "Payment finalised. Thankyou!")

        # If a w_url for woocommerce webhook has been provided, then we need
        # to take some additional steps to confirm the order.
        if "w_url" in payload.keys():
            # Call webhook
            response = woo_webhook.hook(app.config["SECRET_KEY"], payload, payment)

            if response.status_code != 200:
                print(
                    "Failed to confirm order payment via webhook {}, please contact the store to ensure the order has been confirmed, error response is: {}".format(
                        response.status_code, response.text
                    )
                )
                update_status(payment, response.text)
            else:
                print("Successfully confirmed payment via webhook.")
                update_status(payment, "Order confirmed.")

        # Redirect after payment
        # TODO: add a delay here. Test.
        if config.redirect is not None:
            print("Redirecting to {}".format(config.redirect))
            return redirect(config.redirect)
        else:
            print("No redirect, closing.")

    return


# Return feedback via the websocket, updating the payment status and time remaining.
def update_status(payment, status, console_status=True):
    payment.status = status
    payment.response = status
    # Log to python stdout also
    if console_status:
        print(payment.status)

    # Send status & response to client
    emit(
        "payresponse",
        {
            "status": payment.status,
            "address": payment.address,
            "amount": payment.value,
            "time_left": payment.time_left,
            "uuid": payment.uuid,
            "response": payment.response,
        },
    )
    return


# Initialise the payment via the payment method (bitcoind / lightningc / etc),
def create_invoice(dollar_amount, currency, label, payment_method=config.pay_method):
    if payment_method == "bitcoind":
        payment = bitcoin_node
    elif payment_method == "lnd":
        payment = lightning_node
    else:
        print("Invalid payment method")
        return

    # Load invoice information
    payment.invoice(dollar_amount, currency, label)

    # Get payment address and generate qr code.
    payment.get_address()
    payment.create_qr()
    return payment


# Payment processing function.
# Handle payment logic.
def process_payment(payment):
    update_status(payment, "Payment intialised, awaiting payment.")

    # Track start_time so we can detect payment timeouts
    payment.start_time = time.time()
    while (config.payment_timeout - (time.time() - payment.start_time)) > 0:
        # Not using := for compatability reasons..
        payment.time_left = config.payment_timeout - (time.time() - payment.start_time)
        # Check progress of the payment
        payment.confirmed_paid, payment.unconfirmed_paid = payment.check_payment()
        print()
        print(payment.__dict__)

        # Debugging and demo mode which auto confirms payments after 5 seconds
        dbg_free_mode_cond = config.free_mode and (time.time() - payment.start_time > 5)
        # If payment is paid
        if (payment.confirmed_paid > payment.value) or dbg_free_mode_cond:
            payment.paid = True
            payment.time_left = 0
            update_status(
                payment, "Payment successful! {} BTC".format(payment.confirmed_paid)
            )
            break

        # Display unconfirmed transaction info
        elif payment.unconfirmed_paid > 0:
            update_status(
                payment,
                "Discovered payment. \
                Waiting for {} confirmations...".format(
                    config.required_confirmations
                ),
                console_status=False,
            )
            socket_.sleep(config.pollrate)

        # Continue waiting for transaction...
        else:
            update_status(payment, "Waiting for payment...")
            socket_.sleep(config.pollrate)
    else:
        update_status(payment, "Payment expired.")
    return


# Test connections on startup:
print("Connecting to node...")
bitcoin_node = bitcoind.btcd()
print("Connection to bitcoin node successful.")
if config.pay_method == "lnd":
    lightning_node = lnd.lnd()
    print("Connection to lightning node successful.")


if __name__ == "__main__":
    socket_.run(app, debug=False)
