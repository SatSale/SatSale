from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
from markupsafe import escape
import time
import os
import requests

import ssh_tunnel
import config
import invoice
from pay import bitcoind
from pay import lnd

# Begin websocket
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
print("Initialised Flask with secret key: {}".format(app.config['SECRET_KEY']))
socket_ = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")

# Render index pages
# To-do, this will be a donation form page that submits to /pay
@app.route('/')
def index():
    return render_template('donate.html', async_mode=socket_.async_mode)

@app.route('/pay')
def payment_page():
    #
    # # Label is blank if not supplied
    # params = {'label':''}
    # for key, value in dict(request.args).items():
    #     params[key] = value
    params = dict(request.args)
    return render_template('index.html', params=params, async_mode=socket_.async_mode)

# Basic return on initialisation
@socket_.on('initialise')
def test_message(message):
    emit('payresponse', {'time_left': -1, 'response': message['data']})

# Main payment method for websocket
# Recieves form amount and initiates invoice and payment processing.
@socket_.on('make_payment')
def make_payment(payload):
    # Check the amount is a float
    amount = payload['amount']
    try:
        amount = float(amount)
    except:
        # Give response?
        amount = None
        return

    # Validate amount is a positive float
    if not (isinstance(amount, float) and amount >= 0):
        # Give response?
        amount = None
        return

    # Return if label missing
    if 'id' not in payload.keys():
        return
    #     label = payload['label']
    # else:
    #     label = "undefined"

    # Initialise this payment
    payment = create_invoice(amount, "USD", payload['id'])

    process_payment(payment)

    if payment.paid:
        payment.status = 'Payment finalised. Thankyou!'
        payment.response = 'Payment finalised. Thankyou!'
        update_status(payment)

        # Call webhook
        if config.gateway is not None and config.gateway:
            response = requests.get(
                payload['w_url'], params={'id' : payload['id']},
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                print('Failed to confirm payment via webhook {}, the response is: {}'.format(response.status_code, response.text))
                payment.status = response.text
                payment.response = response.text
            else:
                print("Successfully confirmed payment via webhook.")
                payment.status = 'Payment confirmed.'
                payment.response = 'Payment confirmed.'

            update_status(payment)

        ### DO SOMETHING
        # Depends on config
        # Get redirected?
        # Nothing?
        # Run custom script?

# Initialise the payment via the payment method (bitcoind / lightningc / etc),
# create qr code for the payment.
def create_invoice(dollar_amount, currency, label):
    if config.pay_method == "bitcoind":
        print("AHHHHHhhhhhhh")
        payment = bitcoind.btcd(dollar_amount, currency, label)
    elif config.pay_method == "lnd":
        payment = lnd.lnd(dollar_amount, currency, label)
    else:
        # There probably should be config checking code within main.py
        print("Invalid payment method")
        return

    payment.get_address()
    payment.create_qr()
    return payment

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

# Payment processing function.
# Handle payment logic.
def process_payment(payment):
    payment.status = 'Payment intialised, awaiting payment.'
    payment.response = 'Payment intialised, awaiting payment.'
    update_status(payment)

    # Track start_time for payment timeouts
    payment.start_time = time.time()
    while (config.payment_timeout - (time.time() - payment.start_time)) > 0:
        payment.time_left = config.payment_timeout - (time.time() - payment.start_time)
        payment.confirmed_paid, payment.unconfirmed_paid = payment.check_payment()
        print()
        print(payment.__dict__)

        if payment.confirmed_paid > payment.value:
            payment.paid = True
            payment.time_left = 0
            payment.status = "Payment successful! {} BTC".format(payment.confirmed_paid)
            payment.response = "Payment successful! {} BTC".format(payment.confirmed_paid)
            update_status(payment)
            break

        elif payment.unconfirmed_paid > 0:
            payment.status = "Discovered payment. \
                Waiting for {} confirmations...".format(config.required_confirmations)
            payment.response = "Discovered payment. \
                Waiting for {} confirmations...".format(config.required_confirmations)
            # console_status=False to reduce console spam
            update_status(payment, console_status=False)
            socket_.sleep(config.pollrate)
        else:
            payment.status = "Waiting for payment...".format(payment.value)
            payment.response = "Waiting for payment...".format(payment.value)
            update_status(payment)
            socket_.sleep(config.pollrate)
    else:
        payment.status = "Payment expired."
        payment.status = "Payment expired."
        update_status(payment)

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
