import mock
import pytest
from payments.price_feed import PriceFeed


def test_call_api():
    price_feed = PriceFeed()
    assert len(price_feed.api_results) > 0

def test_invalid_currency():
    with pytest.raises(KeyError):
        price_feed = PriceFeed()
        result = price_feed.get_btc_price('xxx')

def test_usd_btc_price():
    expected = 40000.0
    price_feed = PriceFeed()
    price_feed.api_results = {"btc":{"name":"Bitcoin","unit":"BTC","value":1.0,"type":"crypto"}, "usd":{"name":"US Dollar","unit":"$","value":40000.0,"type":"fiat"}, "aud":{"name":"Australian Dollar","unit":"A$","value":60000.0,"type":"fiat"}}
    actual = price_feed.get_btc_price('usd')
    assert expected == actual

def test_fiat_conversion():
    expected = 10.0
    price_feed = PriceFeed()
    price_feed.api_results = {"btc":{"name":"Bitcoin","unit":"BTC","value":1.0,"type":"crypto"}, "usd":{"name":"US Dollar","unit":"$","value":40000.0,"type":"fiat"}, "aud":{"name":"Australian Dollar","unit":"A$","value":60000.0,"type":"fiat"}}
    actual = price_feed.get_price(15.0, 'aud', 'usd')
    assert expected == actual
