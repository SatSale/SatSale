from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, emit, disconnect
from markupsafe import escape
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
if os.path.exists("BTCPyment_API_key"):
    with open("BTCPyment_API_key", 'r') as f:
        app.config['SECRET_KEY'] = f.read().strip()
else:
    with open("BTCPyment_API_key", 'w') as f:
        app.config['SECRET_KEY'] = os.urandom(64).hex()
        f.write(app.config['SECRET_KEY'])

print("Initialised Flask with secret key: {}".format(app.config['SECRET_KEY']))
socket_ = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")

# Basic return on initialisation
@socket_.on('initialise')
def test_message(message):
    emit('payresponse', {'time_left': -1, 'response': message['data']})

# Render index page
# This is currently a donation page that submits to /pay
@app.route('/')
def index():
    return render_template('donate.html', async_mode=socket_.async_mode)

# /pay is the main payment method for initiating a payment websocket.
@app.route('/pay')
def payment_page():
    params = dict(request.args)
    return render_template('index.html', params=params, async_mode=socket_.async_mode)

# Main payment method called by the websocket client
# make_payment recieves form amount and initiates invoice and payment processing.
@socket_.on('make_payment')
def make_payment(payload):
    # Check the amount is a float
    amount = payload['amount']
    try:
        amount = float(amount)
    except:
        payment.status = 'Invalid amount.'
        payment.response = 'Invalid amount.'
        update_status(payment)
        amount = None
        return

    # Validate amount is a positive float
    if not (isinstance(amount, float) and amount >= 0):
        # Give response?
        amount = None
        return

    # Return if label missing
    if 'id' in payload.keys():
        label = payload['id']
    else:
        label = "noid"

    # Initialise this payment
    payment = create_invoice(amount, "USD", label)

    # Wait for amount to be sent to the address
    process_payment(payment)

    if payment.paid:
        payment.status = 'Payment finalised. Thankyou!'
        payment.response = 'Payment finalised. Thankyou!'
        update_status(payment)

        # Call webhook if woocommerce webhook url has been provided.
        if 'w_url' in payload.keys():
            response = woo_webhook.hook(app.config['SECRET_KEY'], payload, payment)

            if response.status_code != 200:
                print('Failed to confirm order payment via webhook {}, the response is: {}'.format(response.status_code, response.text))
                payment.status = response.text
                payment.response = response.text
            else:
                print("Successfully confirmed payment via webhook.")
                payment.status = 'Order confirmed.'
                payment.response = 'Order confirmed.'

            update_status(payment)

        # Redirect after payment
        if config.redirect is not None:
            print("Redirecting to {}".format(config.redirect))
            return redirect(config.redirect)
        else:
            print("No redirect, closing.")

        return

# Return feedback via the websocket, updating the status and time remaining.
def update_status(payment, console_status=True):
    if console_status:
        print(payment.status)

    emit('payresponse', {
        'status' : payment.status,
        'address' : payment.address,
        'amount' : payment.value,
        'time_left' : payment.time_left,
        'uuid' : payment.uuid,
        'response': payment.response})
    return

def call_update_status(payment, status, console_status=True):
    payment.status = status
    payment.response = status
    update_status(payment, console_status=console_status)

# Initialise the payment via the payment method (bitcoind / lightningc / etc),
# create qr code for the payment.
def create_invoice(dollar_amount, currency, label):
    if config.pay_method == "bitcoind":
        payment = bitcoind.btcd(dollar_amount, currency, label)
    elif config.pay_method == "lnd":
        payment = lnd.lnd(dollar_amount, currency, label)
    else:
        print("Invalid payment method")
        return

    payment.get_address()
    payment.create_qr()
    return payment

# Payment processing function.
# Handle payment logic.
def process_payment(payment):
    call_update_status(payment, 'Payment intialised, awaiting payment.')

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
            call_update_status(payment, "Payment successful! {} BTC".format(payment.confirmed_paid))
            break

        # Display unconfirmed transaction info
        elif payment.unconfirmed_paid > 0:
            call_update_status(payment, "Discovered payment. \
                Waiting for {} confirmations...".format(config.required_confirmations), console_status=False)
            socket_.sleep(config.pollrate)

        # Continue waiting for transaction...
        else:
            call_update_status(payment, "Waiting for payment...".format(payment.value))
            socket_.sleep(config.pollrate)
    else:
        call_update_status(payment, "Payment expired.")
    return

# Test Bitcoind connection on startup:
print("Checking node connectivity...")
if config.pay_method == "bitcoind":
    bitcoind.btcd(1, 'USD', 'Init test.')
elif config.pay_method == "lnd":
    lnd.lnd(1, 'USD', 'Init test')
print("Connection successful.")


if __name__ == '__main__':
    socket_.run(app, debug=False)
