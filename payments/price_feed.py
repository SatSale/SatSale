import requests
import logging
from abc import ABC, abstractmethod

import config


class PriceFeed(ABC):

    def __init__(self, price_feed_url: str = None) -> None:
        self._price_data = None
        self._price_feed_url = price_feed_url

    @abstractmethod
    def _get_rate(self, base_currency: str) -> float:
        pass

    def _fetch_price_data(self) -> None:
        if self._price_feed_url is not None:
            for i in range(config.connection_attempts):
                try:
                    r = requests.get(self._price_feed_url)
                    self._price_data = r.json()
                    return
                except Exception as e:
                    logging.error(e)
                logging.info(
                    "Attempting again... {}/{}...".format(
                        i + 1, config.connection_attempts)
                )

            else:
                raise RuntimeError("Failed to reach {}.".format(
                    self._price_feed_url))

    # used by tests
    def set_price_data(self, price_data: dict) -> None:
        self._price_data = price_data

    def _get_btc_exchange_rate(self, base_currency: str, bitcoin_rate_multiplier: float) -> float:
        self._fetch_price_data()
        try:
            rate = self._get_rate(base_currency)
            if bitcoin_rate_multiplier != 1.00:
                logging.debug(
                    "Adjusting BTC/{} exchange rate from {} to {} "
                    "because of rate multiplier {}.".format(
                        base_currency, rate, rate * bitcoin_rate_multiplier,
                        bitcoin_rate_multiplier))
                rate = rate * bitcoin_rate_multiplier
            return rate
        except Exception:
            logging.error(
                "Failed to find currency {} from {}.".format(
                    base_currency, self._price_feed_url)
            )
            return None

    def get_btc_value(self, base_amount: float, base_currency: str) -> float:
        if base_currency == "BTC":
            return float(base_amount)
        elif base_currency == "sats":
            return float(base_amount) / 10**8

        exchange_rate = self._get_btc_exchange_rate(
            base_currency, config.bitcoin_rate_multiplier)

        if exchange_rate is not None:
            try:
                float_value = float(base_amount) / exchange_rate
            except Exception as e:
                logging.error(e)

            return round(float_value, 8)

        raise RuntimeError("Failed to get base currency value.")


class CoinDeskPriceFeed(PriceFeed):

    def __init__(self, price_feed_url: str = "https://api.coindesk.com/v1/bpi/currentprice.json") -> None:
        super().__init__(price_feed_url)

    def _get_rate(self, base_currency: str) -> float:
        return float(self._price_data["bpi"][base_currency.upper()]["rate_float"])


class CoinGeckoPriceFeed(PriceFeed):

    def __init__(self, price_feed_url: str = "https://api.coingecko.com/api/v3/exchange_rates") -> None:
        super().__init__(price_feed_url)

    def _get_rate(self, base_currency: str) -> float:
        return float(self._price_data["rates"][base_currency.lower()]["value"])


def get_btc_value(base_amount: float, base_currency: str) -> float:
    if config.currency_provider == "COINDESK":
        provider = CoinDeskPriceFeed()
    elif config.currency_provider == "COINGECKO":
        provider = CoinGeckoPriceFeed()
    else:
        raise Exception(
            "Unsupported exchange rate provider (currency_provider): " +
            config.currency_provider
        )
    return provider.get_btc_value(base_amount, base_currency)
