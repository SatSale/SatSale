# Incomplete

import sys

sys.path.append("..")

import os
import logging

import config
from payments import database
from payments.price_feed import get_btc_value
from node import bitcoind
from node import lnd
from node import clightning

# Clean test environment:
for rm_file in ["database.db", "tls.cert", "invoice.macaroon", "SatSale_API_key"]:
    if os.path.exists(rm_file):
        os.remove(rm_file)
        print("deleted {}".format(rm_file))

try:
    import satsale

    satsale_boot_success = True
except Exception as e:
    satsale_boot_success = False
    print(e)
    print("Failed to boot SatSale. Check config and try again.")

print(3 * "\n")
assert satsale_boot_success


# Try get invoice from nodes
bitcoin_node = bitcoind.btcd()
print("Connection to bitcoin node successful.")
if config.pay_method == "lnd":
    lightning_node = lnd.lnd()
    print("Connection to lightning node successful.")
