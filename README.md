# BTCPyment
Existing non-custodial Bitcoin payment processors are bloated and difficult for the average person to install. BTCPyment strives to exist as an easily deployable, highly customisable, lightweight Bitcoin payment processor that keeps your coins with your keys. Almost purely written in Python and Javascript, BTCPyment makes donation buttons simple; via a simple embedded iframe that talks to your own Bitcoin node via Flask websockets.

# Installation
## Install
Clone and install dependencies
```
git clone https://github.com/nickfarrow/BTCPyment
pip install -r requirements.txt
```
## Connect to your Bitcoin Node
Edit the `config.py` configuration and point to your Bitcoin node:
```python
host = "127.0.0.1"
rpcport = "8332"
username = "bitcoinrpc"
password = "RPCPASSWORD"
```
(You can find these in `~/.bitcoin/bitcoin.conf`). If your node is remote to your website, you can specify an ssh `tunnel_host = "pi@192.168.0.252"`.

## Run BTCPyment
Run server with
```
cd BTCPyment/
gunicorn --worker-class eventlet -w 1 server:app
```
That's it! You should now be able to view your BTCPyment server at http://YOUR_SERVER_IP:8000/. If running locally, this will be `127.0.0.1:8000`.

## Embed Donation Button
Now embed the donation button into your website
```html
<iframe src="http://YOUR_SERVER_IP:8000/" style="margin: 0 auto;display:block;height:300px;border:none;overflow:hidden;" scrolling="no"></iframe>
```

# Features
* Lightweight, Python and Javascript talk to your own bitcoin node via websockets and ssh.
* Direct peer-to-peer payments without any middleman. No KYC, and greater privacy than donation systems with reused Bitcoin addresses.
* Natively supports all bitcoind node features through RPC.
* QR codes, customisable payment confirmations and payment expiry duration.
* No shitcoin bloat. Bitcoin only.
* Highly extendable, just take a look at the code! Optional code excecution upon payment.

# Developers
## You only need a little python!
The main code can be found in `server.py`. invoice and bitcoind handling in `invoice/`, donation button javascript logic in `static/`, button appearance in `template/`. Please have ago at implementing some of the things below!

# Coming soon:
* Payment API to process payments from any desired point of sale or web shop (woocommerce, shopify)
* Lightning support
* More readily customisable donation button (text/color/QR code)
* Database integration for payment invoices
* Multiple choice of price feeds

# Disclaimer
BTCPyment is in early development, as such we are not responsible for any loss of funds or vulnerabilities.

# Sponsors
