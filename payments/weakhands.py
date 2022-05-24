import requests
import logging


quote_url = "https://sideshift.ai/api/v1/quotes"
swap_url = "https://sideshift.ai/api/v1/orders"
affiliate = "eK590V1Mh"


def get_quote(amount_lnbtc):
    quote_data = {
        "depositMethod": "ln",
        "settleMethod": "usdtla",
        "affiliateId": affiliate,
        "depositAmount": str(amount_lnbtc),
    }
    logging.info("Getting quote to swap {:.8f} LN-BTC to USDT".format(amount_lnbtc))
    resp = requests.post(quote_url, json=quote_data)

    if resp.status_code != 201:
        logging.error("Failed quote request:")
        logging.error(resp.json())
        return False

    return resp.json()


def get_swap(quote, amount_lnbtc, liquid_address):
    swap_url = "https://sideshift.ai/api/orders"
    data = {
        "type": "fixed",
        "quoteId": quote["id"],
        "settleAddress": liquid_address,
        "affiliateId": affiliate,
    }
    logging.info(
        "Creating order to swap {:.8f} LN-BTC to USDT (liquid: {})".format(
            amount_lnbtc, liquid_address
        )
    )

    resp = requests.post(swap_url, json=data)

    if resp.status_code != 201:
        logging.error("Failed to create order:")
        logging.error(resp.json())
        return False

    return resp.json()


def pay_swap(node, swap):
    payment_req = swap["depositAddress"]["paymentRequest"]
    logging.info("Paying invoice: {}".format(payment_req))
    node.pay_invoice(payment_req)
    return True


def swap_lnbtc_for_lusdt(node, amount_lnbtc, liquid_address):
    try:
        quote = get_quote(amount_lnbtc)
        if not quote:
            logging.error("Quote failed, not swapping this order.")
            return False

        swap = get_swap(quote, amount_lnbtc, liquid_address)
        if not swap:
            logging.error("Creating order failed, not swapping this payment.")
            return False

        pay_swap(node, swap)
        logging.info("Paid invoice! Swapped ")

    except Exception as e:
        logging.error("Error encountered during swap: {}".format(e))

    return
