import uuid

import config
from .price_feed import get_btc_value


class invoice():
    def __init__(self, dollar_value, currency, label):
        self.dollar_value = dollar_value
        self.currency = currency
        self.value = get_btc_value(dollar_value, currency)
        self.label = label
        self.id = str(uuid.uuid4)
        self.status = 'Payment initialised.'
        self.response = ''
        self.time_left = config.payment_timeout
        self.confirmed_paid = 0
        self.unconfirmed_paid = 0
