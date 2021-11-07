from lightning import LightningRpc
from pprint import pprint

import random


def inv_label():
    return "invoice_" + str(random.randint(1, 1000000))


l1 = LightningRpc("/home/nick/.lightning/regtest/lightning-rpc")
print(l1)

info1 = l1.getinfo()
pprint(info1)

print()
print()


deposit_address = l1.newaddr()
print("Deposit address: {}".format(deposit_address))

# Interesting C lightning appears to be using msatoshi as base unit
# 10**(-8) * 10**(-3)??

# Label and description??
# amount, label, description

# You can not have duplicate labels!
# Invoice will fail to create. Descriptions can be duplicate.

amount, label, description = 1000, "test invoice2", "description_here"
invoice1 = l1.invoice(amount, inv_label(), description)
print(invoice1)


# When I generate 500 blocks, one client registers them like 5 seconds before the other. Why?


# Why does listchannels show two channels? I thought dual was funding a single channel from both sides?
#

# BUG
# When changing match
# 2021-08-19T09:43:24.508Z DEBUG   gossipd: Bad gossip order: WIRE_NODE_ANNOUNCEMENT before announcement 03ea851ddb18030226f18babbfd9e997cc4dee4b47e51f5f7a87c990b892643eb5
