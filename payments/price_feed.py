import requests

import config


def get_coindesk_price(currency):
    price_feed = "https://api.coindesk.com/v1/bpi/currentprice.json"
    r = requests.get(price_feed)

    for i in range(config.connection_attempts):
        try:
            price_data = r.json()
            prices = price_data["bpi"]
            break

        except Exception as e:
            print(e)
            print(
                "Attempting again... {}/{}...".format(i + 1, config.connection_attempts)
            )

    else:
        raise ("Failed to reach {}.".format(price_feed))

    try:
        price = prices[currency]["rate"].replace(",", "")
        return price

    except:
        print("Failed to find currency {} from {}.".format(currency, price_feed))
        return None


def get_coingecko_price(currency):
    price_feed = "https://api.coingecko.com/api/v3/exchange_rates"
    r = requests.get(price_feed)

    for i in range(config.connection_attempts):
        try:
            price_data = r.json()
            prices = price_data["rates"]
            break

        except Exception as e:
            print(e)
            print(
                "Attempting again... {}/{}...".format(i + 1, config.connection_attempts)
            )

    else:
        raise ("Failed to reach {}.".format(price_feed))

    try:
        price = prices[currency.lower()]["value"]
        return price

    except:
        print("Failed to find currency {} from {}.".format(currency, price_feed))
        return None


def get_btc_value(fiat_value, currency):
    
    if config.currency_provider == "COINDESK":
        price = get_coindesk_price(currency)
    else:
        price = get_coingecko_price(currency)
    
    if price is not None:

        try:
            float_value = float(fiat_value) / float(price)
            if not isinstance(float_value, float):
                raise Exception("Fiat value should be a float.")
        except Exception as e:
            print(e)

        return float_value

    raise Exception("Failed to get fiat value.")
