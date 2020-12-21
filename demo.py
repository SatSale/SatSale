from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, disconnect
from markupsafe import escape
import time

import main
import config
import invoice
from pay import bitcoind


async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode)
# thread = None
# thread_lock = Lock()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socket_.async_mode)

@socket_.on('initialise', namespace='/pay')
def test_message(message):
    emit('my_response', {'time_left': config.payment_timeout, 'response': message['data']})

@socket_.on('payment', namespace='/pay')
def make_payment(message):
    print("Requesting payment for {}".format(message['amount']))

    # Check the amount is a float
    amount = message['amount']
    try:
        amount = float(amount)
    except:
        emit('my_response', {'status' : '', 'address' : '', 'amount' : '', 'time_left': 0, 'response': "Invalid payment mount.".format(unconf_paid)})
        amount = None
        return

    # Validate amount is a positive float
    if not (isinstance(amount, float) and amount >= 0):
        emit('my_response', {'status' : '', 'address' : '', 'amount' : '', 'time_left': 0, 'response': "Invalid payment mount.".format(unconf_paid)})
        amount = None
        return

    # Initialise this payment
    payment = create_invoice(amount, "USD", "wee")
    emit('my_response', {'status' : 'Awaiting payment.', 'address' : payment.address, 'amount' : payment.value, 'time_left': config.payment_timeout, 'response' : 'Awaiting payment.'})

    # Track start_time for payment timeouts
    start_time = time.time()
    while (time_left := config.payment_timeout - (time.time() - start_time)) > 0:
        conf_paid, unconf_paid = payment.check_payment()
        print(conf_paid, unconf_paid)

        if conf_paid > payment.value:
            print("Invoice {} paid! {} BTC.".format(payment.label, conf_paid))
            payment.paid = True
            break

        elif unconf_paid > 0:
            emit('my_response', {'status' : 'Discovered {} BTC payment... Waiting for {} confirmations.'.format(config.required_confirmations), 'address' : payment.address, 'amount' : payment.value, 'time_left': time_left, 'response': "Discovered {} BTC payment, waiting for {} confirmations.".format(unconf_paid, config.required_confirmations)})
            socket_.sleep(15)
        else:
            emit('my_response', {'status' : 'Awaiting payment.', 'address' : payment.address, 'amount' : payment.value, 'time_left': time_left, 'response': 'Awaiting {} BTC payment...'.format(payment.value)})
            socket_.sleep(15)
    else:
        emit('my_response', {'status' : 'EXPIRED', 'address' : payment.address, 'amount' : payment.value, 'time_left': 0, 'response':'INVOICE EXPIRED'})
        print("Invoice {} expired.".format(payment.label))
        payment.paid = False

    if payment.paid:
        print("PAID")
        emit('my_response', {'status' : 'Paid!', 'address' : payment.address, 'amount' : payment.value, 'time_left': time_left, 'response': 'Payment finalised.'})

def create_invoice(amount, currency, label):
    inv = invoice.invoice(amount, currency, label)

    payment = bitcoind.btcd()
    payment.load_invoice(inv)
    payment.get_address()
    return payment


if __name__ == '__main__':
    socket_.run(app, debug=True)
