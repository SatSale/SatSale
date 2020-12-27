from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, disconnect
from markupsafe import escape
import time

import ssh_tunnel
import config
import invoice
from pay import bitcoind

# Render html
@app.route('/')
def index():
    return render_template('index.html', async_mode=socket_.async_mode)

# Basic return on initialisation
@socket_.on('initialise', namespace='/pay')
def test_message(message):
    emit('payresponse', {'time_left': -1, 'response': message['data']})

# Main payment method for websocket
# Recieves form amount and initiates invoice and payment processing.
@socket_.on('payment', namespace='/pay')
def make_payment(payload):
    print("Requesting payment for {}".format(payload['amount']))

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

    # Need to check this is safe!
    label = payload['label']

    # Initialise this payment
    payment = create_invoice(amount, "USD", label)

    process_payment(payment)

    if payment.paid:
        payment.status = 'Payment finalised. Thankyou!'
        payment.response = 'Payment finalised. Thankyou!'
        update_status(payment)

        invoice.success.success()

        ### DO SOMETHING
        # Depends on config
        # Get redirected?
        # Nothing?
        # Run custom script?

# Initialise the payment via the payment method (bitcoind / lightningc / etc),
# create qr code for the payment.
def create_invoice(dollar_amount, currency, label):
    payment = bitcoind.btcd(dollar_amount, currency, label)
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
    payment.status = 'Awaiting payment.'
    payment.response = 'Awaiting payment.'
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
            payment.status = "Discovered {} BTC payment. \
                Waiting for {} confirmations...".format(payment.unconfirmed_paid, config.required_confirmations)
            payment.response = "Discovered {} BTC payment. \
                Waiting for {} confirmations...".format(payment.unconfirmed_paid, config.required_confirmations)
            update_status(payment)
            socket_.sleep(config.pollrate)
        else:
            payment.status = "Awaiting payment...".format(payment.value)
            payment.response = "Awaiting payment...".format(payment.value)
            update_status(payment)
            socket_.sleep(config.pollrate)
    else:
        payment.status = "Payment expired."
        payment.status = "Payment expired."
        update_status(payment)

    return


# Begin websocket
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode)

# Test Bitcoind connection on startup:
print("Checking node connectivity...")
bitcoind.btcd('1', 'USD', 'Init test.')
print("Connection successful.")


if __name__ == '__main__':
    socket_.run(app, debug=True)
