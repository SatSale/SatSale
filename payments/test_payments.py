import os
import unittest
from price_feed import *


class TestPayments(unittest.TestCase):

    def test_get_currency_provider_constants(self):
        self.assertEqual(get_currency_provider_constants('EUR')["COINDESK"]["result_root"], "bpi")
        self.assertEqual(get_currency_provider_constants('EUR')["COINDESK"]["ticker"], "EUR")
        self.assertEqual(get_currency_provider_constants('EUR')["COINGECKO"]["ticker"], "eur")        

    def test_get_price(self):
        self.assertGreater(get_price('EUR', "COINDESK"),0)


if __name__ == '__main__':
    unittest.main()