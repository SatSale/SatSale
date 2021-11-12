import requests

import config

# import config

quote_url = "https://sideshift.ai/api/v1/quotes"
swap_url = "https://sideshift.ai/api/v1/orders"
affiliate = "eK590V1Mh"

def get_quote(amount_lnbtc):
    quote_data = {
        "depositMethod": "ln",
        "settleMethod": "usdtla",
        "affiliateId": affiliate,
        "depositAmount": str(amount_lnbtc)
    }
    print("Getting quote to swap {:.8f} LN-BTC to USDT".format(amount_lnbtc))
    resp = requests.post(quote_url, json=quote_data)

    if resp.status_code != 201:
        print("Failed quote request:")
        print(resp.json())
        return False

    return resp.json()


def get_swap(quote, amount_lnbtc, liquid_address):
    swap_url = "https://sideshift.ai/api/orders"
    data = {
        "type": "fixed",
        "quoteId": quote['id'],
        "settleAddress": liquid_address,
        "affiliateId": affiliate,
    }
    print("Creating order to swap {:.8f} LN-BTC to USDT (liquid: {})".format(amount_lnbtc, liquid_address))

    resp = requests.post(swap_url, json=data)

    if resp.status_code != 201:
        print("Failed to create order:")
        print(resp.json())
        return False

    return resp.json()

def pay_swap(node, swap):
    payment_req = swap['depositAddress']['paymentRequest']
    print("Paying invoice: {}".format(payment_req))
    node.pay_invoice(payment_req)
    return True

def swap_lnbtc_for_lusdt(node, amount_lnbtc, liquid_address):
    try:
        quote = get_quote(amount_lnbtc)
        if not quote:
            print("Quote failed, not swapping this order.")
            return False

        swap = get_swap(quote, amount_lnbtc, liquid_address)
        if not swap:
            print("Creating order failed, not swapping this payment.")
            return False

        pay_swap(node, swap)
        print("Paid invoice! Swapped ")

    except Exception as e:
        print("Error encountered during swap: {}".format(e))

    return
