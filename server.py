from flask import Flask, request, url_for, jsonify, render_template
from markupsafe import escape
import time

import main
import config
import invoice
from pay import bitcoind

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('payment.html')


app.route('/invoice', methods=['GET'])
def invoice():
    amount = request.values.get('amount')

    try:
        amount = float(amount)
    except:
        print("Amount could not be interpreted as float {}".format(amount))
        amount = None
        return

    payment = create_invoice(amount, currency, label)



@app.route('/pay', methods=['GET', 'POST'])
def pay():
    start_time = time.time()

    if True: #request.method == 'POST':
        print("CALLING BITCOIND MAIN")

        amount = request.values.get('amount')

        try:
            amount = float(amount)
        except:
            print("Amount could not be interpreted as float {}".format(amount))
            amount = None
            return

        if (isinstance(amount, float) and amount >= 0):
            print("Calling main payment function for {}".format(amount))

            if payment(amount, "USD", "wee"):
                print("PAID")
                return jsonify(paid=True)

        else:
            return jsonify(paid=False)

    else:
        return jsonify(paid=False)


def create_invoice(amount, currency, label):
    inv = invoice.invoice(amount, currency, label)

    payment = bitcoind.btcd()
    payment.load_invoice(inv)
    payment.get_address()
    return payment


def payment(amount, currency, label):
    payment = create_invoice(amount, currency, label)

    start_time = time.time()
    while time.time() - start_time < config.payment_timeout:
        conf_paid, unconf_paid = payment.check_payment()
        print(conf_paid, unconf_paid)

        if conf_paid > payment.value:
            print("Invoice {} paid! {} BTC.".format(payment.label, conf_paid))
            payment.paid = True
            return True
        else:
            time.sleep(15)
    else:
        print("Invoice {} expired.".format(payment.label))

    if payment.paid:
        print("Returning paid to site.")
    else:
        print("Reload page, etc. need to create new invoice")

    return False


#with app.test_client() as c:
#    resp = c.post('/pay', data=dict(amount=69))
#    print(resp.data)
