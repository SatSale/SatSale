import config
import invoice
from pay import bitcoind

import time
import subprocess

# If tunnel is required (might make things easier)
try:
    if config.tunnel_host is not None:
        command = ['ssh', config.tunnel_host, '-L', '{}:localhost:{}'.format(config.rpcport, config.rpcport), '-q']
        print("Opening tunnel to {}.".format(' '.join(command)))
        tunnel_proc = subprocess.Popen(['ssh', config.tunnel_host, '-L', '{}:localhost:{}'.format(config.rpcport, config.rpcport)])
    else:
        tunnel_proc = None
except Exception:
    tunnel_proc = None
    pass


inv = invoice.invoice(1.8, "USD", "test invoice232")
payment = bitcoind.btcd()
payment.load_invoice(inv)
payment.get_address()

start_time = time.time()
while time.time() - start_time < config.payment_timeout: 
    conf_paid, unconf_paid = payment.check_payment()
    print(conf_paid, unconf_paid)
    
    if conf_paid > payment.value:
        print("Invoice {} paid! {} BTC.".format(payment.label, conf_paid))
        payment.paid = True
        break
    else:
        time.sleep(15)
else:
    print("Invoice {} expired.".format(payment.label))

if payment.paid:
    print("Returning paid to site.")
else:
    print("Reload page, etc. need to create new invoice")

if tunnel_proc is not None:
    tunnel_proc.kill()

