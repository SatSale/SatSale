# Linux desktop notifications upon payment
# Run `python3 -c "from scripts import notification"` from SatSale/ directory
# This will load your config.toml and continually refresh for lightning payments (SatSale and others)
# 
# By default, a command `notify-send {node} {message}` is sent to give a desktop notification.
# You can change `do_this_with_invoice(node, invoice)` which called under a certain `condition(invoice)`.
import subprocess
import time

from node import lnd
from node import clightning
import config
from gateways import ssh_tunnel

SLEEP_TIME = 30

def condition(invoice):
    if "state" in invoice.keys() and invoice["state"] == "SETTLED":
        return True
    return False

def do_this_with_invoice(node, invoice):
    print("Found {}".format(invoice["memo"]))
    message = "Recieved payment: {} sats\n{}".format(invoice['value'], invoice['memo'])
    command = ["notify-send", node.config['name'], message]
    subprocess.run(command)
    return


ssh_tunnel.open_tunnels()
cfg = [node for node in config.payment_methods if node["name"] in ["lnd", "clightning"]]

for node_conf in config.payment_methods:
    print(node_conf)
    if node_conf["name"] == "lnd":
        node = lnd.lnd(node_conf)
        hash_key = "rHash"
        break
    elif node_conf["name"] == "clightning":
        node = clightning.clightning(node_conf)
        hash_key = "payment_hash"
        break
else:
    print("no lightning node")

alarmed_invoices = {}
i = 0
while True:
    invoices = node.list_invoices()
    for invoice in invoices['invoices']:
        if invoice[hash_key] not in alarmed_invoices.keys():
            if condition(invoice):
                if i != 0:
                    do_this_with_invoice(node, invoice)
                alarmed_invoices[invoice[hash_key]] = invoice

    time.sleep(SLEEP_TIME)
    i += 1

