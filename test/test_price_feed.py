import json
import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from payments.price_feed import \
    CoinDeskPriceFeed, \
    CoinGeckoPriceFeed

testdir = os.path.dirname(os.path.realpath(__file__))


def read_price_feed_data(filename: str) -> dict:
    with open(os.path.join(testdir, filename), "r") as f:
        json_data = f.read()
    return json.loads(json_data)


@pytest.mark.parametrize(
    "price_feed",
    [
        {
            "class": CoinDeskPriceFeed,
            "data_file": "coindesk_price_data.json"
        },
        {
            "class": CoinGeckoPriceFeed,
            "data_file": "coingecko_price_data.json"
        }
    ])
def test_invalid_base_currency(price_feed: dict) -> None:
    provider = price_feed["class"](price_feed_url=None)
    provider.set_price_data(read_price_feed_data(price_feed["data_file"]))
    with pytest.raises(RuntimeError):
        provider.get_btc_value(1, "xxx")


@pytest.mark.parametrize(
    "price_feed",
    [
        {"class": CoinDeskPriceFeed},
        {"class": CoinGeckoPriceFeed}
    ])
def test_btc_btc_price(price_feed: dict) -> None:
    provider = price_feed["class"](price_feed_url=None)
    assert (provider.get_btc_value(1, "BTC") == 1)
    assert (provider.get_btc_value(1000000, "sats") == 0.01)


@pytest.mark.parametrize(
    "price_feed",
    [
        {
            "class": CoinDeskPriceFeed,
            "data_file": "coindesk_price_data.json",
            "conversions": [
                {
                    "base_value": 100, "base_currency": "USD", "btc_value": 0.00544072
                }
            ]
        },
        {
            "class": CoinGeckoPriceFeed,
            "data_file": "coingecko_price_data.json",
            "conversions": [
                {
                    "base_value": 100, "base_currency": "USD", "btc_value": 0.0052687
                }
            ]
        }
    ])
def test_fiat_btc_price(price_feed: dict) -> None:
    provider = price_feed["class"](price_feed_url=None)
    provider.set_price_data(read_price_feed_data(price_feed["data_file"]))
    for conv in price_feed["conversions"]:
        assert (
            provider.get_btc_value(conv["base_value"], conv["base_currency"]) ==
            conv["btc_value"]
        )
