from flask import Flask, request, url_for, jsonify, render_template
from markupsafe import escape

import main

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('payment.html')

@app.route('/pay', methods=['GET', 'POST'])
def pay():
    if True: #request.method == 'POST':
        print("CALLING BITCOIND MAIN")
        
        amount = request.values.get('amount')

        try:
            amount = float(amount)
        except:
            print("Amount could not be interpreted as float")
            amount = None
            return

        if (isinstance(amount, float) and amount >= 0):
            print("Calling main payment function for {}".format(amount))
            main.payment(amount, "USD", "wee")
            
        else:
            return "BROKE"
 
        print("Passing amount : {}".format(amount))
        return jsonify(amount=amount)

    else:
        return "INVALID PAYMENT POST"

#with app.test_client() as c:
#    resp = c.post('/pay', data=dict(amount=69))
#    print(resp.data)
