from .price_feed import get_btc_value

class invoice():
    def __init__(self, dollar_value, currency):
        self.value = get_btc_value(dollar_value, currency)
