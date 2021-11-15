import requests
import config


def get_price(currency):

    # Define some currency_provider-specific settings 
    if config.currency_provider == "COINDESK":
        price_feed  = "https://api.coindesk.com/v1/bpi/currentprice.json"  # url to get the pricefeed 
        result_root = "bpi"               # name of the outer json tag
        value_attribute   = "rate_float"  # attribute in which the float fx is located in json reposnse
        ticker      = currency.upper()                     
    else:
        price_feed  = "https://api.coingecko.com/api/v3/exchange_rates"
        result_root = "rates"         # name of the outer json tag
        value_attribute   = "value"   # attribute in which the float fx is located in json reposnse
        ticker      = currency.lower() 

    r = requests.get(price_feed)

    for i in range(config.connection_attempts):
        try:
            price_data = r.json()
            prices = price_data[result_root]
            break

        except Exception as e:
            print(e)
            print(
                "Attempting again... {}/{}...".format(i + 1, config.connection_attempts)
            )

    else:
        raise ("Failed to reach {}.".format(price_feed))

    try:
        price = prices[ticker][value_attribute]
        return price

    except:
        print("Failed to find currency {} from {}.".format(currency, price_feed))
        return None


def get_btc_value(base_amount, currency):
    price = get_price(currency)
    
    if price:
        try:
            float_value = float(base_amount) / float(price)
            if not isinstance(float_value, float):
                raise Exception("Fiat value should be a float.")
        except Exception as e:
            print(e)

        return float_value

    raise Exception("Failed to get fiat value.")
