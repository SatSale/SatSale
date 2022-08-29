import requests
import logging

import config


def get_currency_provider(currency, currency_provider):
    # Define some currency_provider-specific settings
    if currency_provider == "COINDESK":
        return {
            "price_feed": "https://api.coindesk.com/v1/bpi/currentprice.json",
            "result_root": "bpi",
            "value_attribute": "rate_float",
            "ticker": currency.upper(),
        }
    else:
        return {
            "price_feed": "https://api.coingecko.com/api/v3/exchange_rates",
            "result_root": "rates",
            "value_attribute": "value",
            "ticker": currency.lower(),
        }


def get_price(currency, currency_provider=config.currency_provider, bitcoin_rate_multiplier=config.bitcoin_rate_multiplier):
    provider = get_currency_provider(currency, currency_provider)
    for i in range(config.connection_attempts):
        try:
            r = requests.get(provider["price_feed"])
            price_data = r.json()
            prices = price_data[provider["result_root"]]
            break

        except Exception as e:
            logging.error(e)
            logging.info(
                "Attempting again... {}/{}...".format(i + 1, config.connection_attempts)
            )

    else:
        raise ("Failed to reach {}.".format(provider["price_feed"]))

    try:
        price = prices[provider["ticker"]][provider["value_attribute"]]
        if bitcoin_rate_multiplier != 1.00:
            logging.debug("Adjusting BTC price from {} to {} because of rate multiplier {}.".format(
                price, price * bitcoin_rate_multiplier, bitcoin_rate_multiplier))
            price = price * bitcoin_rate_multiplier
        return price

    except Exception:
        logging.error(
            "Failed to find currency {} from {}.".format(currency, provider["price_feed"])
        )
        return None


def get_btc_value(base_amount, currency):
    if currency == "BTC":
        return float(base_amount)
    elif currency == "sats":
        return float(base_amount) / 10**8

    price = get_price(currency)

    if price is not None:
        try:
            float_value = float(base_amount) / float(price)
            if not isinstance(float_value, float):
                raise Exception("Fiat value should be a float.")
        except Exception as e:
            logging.error(e)

        return float_value

    raise Exception("Failed to get base currency value.")
