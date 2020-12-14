from .price_feed import get_btc_value

class invoice():
    def __init__(self, dollar_value, currency, label):
        self.dollar_value = dollar_value
        self.currency = currency
        self.value = get_btc_value(dollar_value, currency)
        self.label = label
