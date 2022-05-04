import logging

import config
import requests


class PriceFeed:
    def __init__(self):
        self.currency_provider_data = self.get_currency_provider_data()
        self.api_results = self.call_api()

    def get_currency_provider_data(self):
        # Define some currency_provider-specific settings
        if config.currency_provider == "COINDESK":
            return {
                "price_feed": "https://api.coindesk.com/v1/bpi/currentprice.json",
                "result_root": "bpi",
                "value_attribute": "rate_float",
                "ticker_case": "upper",
            }
        elif config.currency_provider == "COINGECKO":
            return {
                "price_feed": "https://api.coingecko.com/api/v3/exchange_rates",
                "result_root": "rates",
                "value_attribute": "value",
                "ticker_case": "lower",
            }

    def call_api(self):
        for i in range(config.connection_attempts):
            try:
                r = requests.get(self.currency_provider_data["price_feed"])
                price_data = r.json()
                prices = price_data[self.currency_provider_data["result_root"]]
                break

            except Exception as e:
                logging.error(e)
                logging.info(
                    "Attempting again... {}/{}...".format(i + 1, config.connection_attempts)
                )
        return prices

    def get_btc_price(self, currency):
        ticker_case = self.currency_provider_data['ticker_case']
        value_attribute = self.currency_provider_data['value_attribute']
        if ticker_case == 'lower':
            btc_price = self.api_results[currency.lower()][value_attribute]
        elif ticker_case == 'upper':
            btc_price = self.api_results[currency.upper()][value_attribute]
        return btc_price

    def get_price(self, amount, currency_from, currency_to='btc'):
        currency_from_price = self.get_btc_price(currency_from)
        currency_to_price = self.get_btc_price(currency_to)
        if not isinstance(amount, float):
            raise ValueError('Base input needs to be a float')
        exchange_rate = currency_to_price / currency_from_price
        new_amount = amount * exchange_rate
        return new_amount
