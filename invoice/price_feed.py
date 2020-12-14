import requests

def get_price(currency):
    price_feed = "https://api.coindesk.com/v1/bpi/currentprice.json"
    r = requests.get(price_feed)
    
    try:
        price_data = r.json()
        prices = price_data['bpi']
    except:
        print("Failed to reach {}.".format(price_feed))
        return None

    try:
        price = prices[currency]['rate'].replace(',', '')
    except:
        print("Failed to find currency {} from {}.".format(currency, price_feed))
        return None

    return price


def get_btc_value(dollar_value, currency):
    if (price := get_price(currency)) is not None:
        
        try:
            float_value = dollar_value / float(price)
            if not isinstance(float_value, float):
                raise Exception("Dollar value should be a float.")
        except Exception as e:
            print(e)
            raise

        return float_value

    raise Exception("Failed to get dollar value.")
