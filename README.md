# BTCPyment
Existing non-custodial Bitcoin payment processors are bloated, difficult to install, and not easily customisable. BTCPyment strives to serve as an easily deployable, lightweight Bitcoin payment processor that keeps your coins with your keys by connecting to your own Bitcoin node.

[![demo](https://nickfarrow.com/assets/btcpyment.png)](https://node.nickfarrow.com/)

Currently, BTCPyment only provides donation buttons, but we plan to soon extend BTCPyment to handle payments from common webstores (shopify, woocommerce, etc).

 BTCPyment makes donation buttons simple; using Python and Javascript to talk to your own Bitcoin node, with an easy iframe embed install. BTCPyment uses RPC to generate new addresses from your Bitcoin node, and monitors the payment status with your own copy of the blockchain. Soon, we hope to support lightning payments as well as function as a payment processor for a variety of web shops (woocommerce, shopify).

# Features
* Lightweight, Python and Javascript talk to your own Bitcoin node via websockets and SSH.
* Direct peer-to-peer payments without any middleman. No KYC, and greater privacy than donation systems with reused Bitcoin addresses.
* Natively supports all bitcoind node features (e.g. segwit) through RPC.
* QR codes, user decided minimum payment confirmations and payment expiry duration.
* Highly extendable, just take a look at the code! Optional code execution upon payment.
* No shitcoin bloat. Bitcoin only.

# Installation (short!)
BTCPyment requires a connection to a Bitcoin node. If you don't have one, you should [install one](https://bitcoincore.org/en/download/)!
### Install
Clone and install dependencies
```
git clone https://github.com/nickfarrow/BTCPyment
cd BTCPyment/
pip3 install -r requirements.txt
```
### Connect to your Bitcoin Node
Edit the `config.py` configuration and point to your Bitcoin node:
```python
host = "127.0.0.1"
rpcport = "8332"
username = "bitcoinrpc"
password = "RPCPASSWORD"
```
(You can find these in `~/.bitcoin/bitcoin.conf`). If your node is remote to your website, you can specify an SSH `tunnel_host = "pi@192.168.0.252"` that will forward `rpcport`. You may also need to set `rpcallowip=YOUR_SERVER_IP` in your `~/.bitcoin/bitcoin.conf`.

### Run BTCPyment
Run BTCPyment with
```
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:8000 server:app
```
That's it! You should now be able to view your BTCPyment server at `http://YOUR_SERVER_IP:8000/`. If running locally, this will be `127.0.0.1:8000`. You might have to allow gunicorn through your firewall with `sudo ufw allow 8000`. You will want to run with nohup so it continues serving in the background:
```
nohup gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:8000 server:app > log.txt 2>&1 &
tail -f log.txt
```

## Embed Donation Button
Now embed the donation button into your website:
```html
<iframe src="http://YOUR_SERVER_IP:8000/" style="margin: 0 auto;display:block;height:320px;border:none;overflow:hidden;" scrolling="no"></iframe>
```

## Using HTTPS
Embedded iframes are easy if your site only uses HTTP. But if your site uses HTTPS, then you can likely see your donation button at `http://YOUR_SERVER_IP:8000/` but not in the embeded iframe. See [HTTPS instructions](docs/HTTPS.md).

# Developers
### You only need a little python!
The main code can be found in `server.py`. The client logic for the donation button sits in `static/server_connection.js`, invoice structure and bitcoind interface in `invoice/`, button appearance in `template/index.html`. Please have ago at implementing some of the things below!

More documentation will be added in the near future.

# Coming soon:
* Payment API to process payments from any desired point of sale or web shop (woocommerce, shopify)
* Lightning support
* **Better UI** with more variety of size and theme.
* More readily customisable donation button (text/color/QR code)
* Database integration for payment invoices
* Multiple choice of price feeds

# Disclaimer
BTCPyment is in very early development. As such, we are not responsible for any loss of funds, vulnerabilities with software, or any other grievances which may arise.

# Sponsors
Please consider [supporting me](https://btcpyment.nickfarrow.com) via my own instance of BTCPyment :). Corporate/whale support would greatly assist my ability to give 100% of my attention to BTCPyment and other Bitcoin projects, please email `baseddepartment@nickfarrow.com`.
