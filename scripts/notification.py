# Notifications Upon Payment
# Run with `python3 -c "from scripts import notification"` from SatSale/ directory
# 
# This will load your config.toml and continually refresh for lightning payments (SatSale and others)
# 
# This script can either give Telegram notifications from a bot, or linux desktop notifications.
# Or you can set a custom `do_this_with_invoice(node, invoice)` which called under a certain `condition(invoice)`.
#
# By default, desktop notifications run with command `notify-send {node} {message}`.
# 
# If you want to recieve telegram notifications from a bot you need to create 
# a one with the BotFather in telegram and fill out these settings
TELEGRAM_API_KEY = ""
# Add your bot to a group, message them and check their for a chat id
# https://api.telegram.org/bot<TELEGRAM_KEY>/getUpdates
TELEGRAM_CHAT_ID = ""
#
SLEEP_TIME = 30
#
import subprocess
import time

from node import lnd
from node import clightning
import config
from gateways import ssh_tunnel


def condition(invoice):
    if "state" in invoice.keys() and invoice["state"] == "SETTLED":
        return True
    return False

def do_this_with_invoice(node, invoice):
    print("Found {}".format(invoice["memo"]))
    
    if TELEGRAM_API_KEY != "" and TELEGRAM_CHAT_ID != "":
        telegram_message(node, invoice)
    linux_notify_send(node, invoice)
    return

def telegram_message(node, invoice):
    import urllib, requests
    message = "Recieved payment: {} sats\n{}".format(invoice['value'], invoice['memo'])
    url = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (
        TELEGRAM_API_KEY,
        TELEGRAM_CHAT_ID,
        urllib.parse.quote_plus(message),
    )
    _ = requests.get(url, timeout=10)
    return

def linux_notify_send(node, invoice):
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

