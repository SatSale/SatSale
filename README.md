# BTCPyment
Existing non-custodial Bitcoin payment processors are bloated, difficult to install, and not easily customisable. BTCPyment strives to serve as an easily deployable, lightweight Bitcoin payment processor that keeps your coins with your keys by connecting to your own Bitcoin node.

Donation Button             |  Bitcoin Payment Gateway
:-------------------------:|:-------------------------:
[![Donate demo](https://nickfarrow.com/assets/btcpyment.png)](https://node.nickfarrow.com/) <br />(Click for demo)
  |  [![Donate demo](https://user-images.githubusercontent.com/24557779/105261068-10a6c200-5be3-11eb-85cb-fb459a7694f3.png)](https://node.nickfarrow.com/) <br />(Click for demo)

BTCPyment currently serves as
1. Donation button for your website
2. A Bitcoin payment gateway, including a Woocommerce plugin that easily turns ANY Wordpress site into a Bitcoin accepting store.

BTCPyment makes donation buttons simple; with a simple Python backend to talk to your own Bitcoin node. BTCPyment uses RPC to generate new addresses from your Bitcoin node, and monitors the payment status with your own copy of the blockchain.

# Features
* Process payments with your own Bitcoin node via RPC and SSH. Bitcoin core, or any other node software that supports RPC calls.
* Direct peer-to-peer payments without any middleman. No KYC, and greater privacy than donation systems wher Bitcoin addresses are reused multiple times.
* Lightweight and highly extendable (for noobs too!)- Python backend with Javascript websockets. Take a [look at the code](server.py)!
* Natively supports all bitcoind node features (e.g. segwit) through RPC.
* QR codes, customizable required payment confirmations and payment expiry time.
* No shitcoin bloat. Bitcoin only.

# Installation (short!)
You require a server to host an instance of BTCPyment on, and a connection to a Bitcoin node. If you don't have a Bitcoin node, you should [install one](https://bitcoincore.org/en/download/).
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
Changing `YOUR_SERVER_IP` to the IP address of the machine you're running BTCPyment through. Optionally, you can redirect a domain to that IP and use that instead.

### Using HTTPS & Domains
Embedded iframes are easy if your site only uses HTTP. But if your site uses HTTPS, then you can see your donation button at `http://YOUR_SERVER_IP:8000/` but will not be able to in an embedded iframe. See [HTTPS instructions](docs/HTTPS.md).

## Payment Gateway (Woocommerce)
Currently we only support Woocommerce via Wordpress, with plans to extend to others in the future. BTCPyment acts as a custom payment gateway for Woocommerce via the plugin found in `/gateways`. Please click here for installation instructions.

## Security
For maximum security, we recommend hosting on a machine where your node only has access to a **watch-only** wallet.

# Developers
### You only need a little python!
The main code can be found in `server.py`. The client logic for the donation button sits in `static/server_connection.js`, invoice structure and bitcoind interface in `invoice/`, button appearance in `template/index.html`. Please have ago at implementing some of the things below!

More documentation will be added in the near future.

# Coming soon:
* Payment API to process payments from any desired point of sale or web shop (woocommerce, shopify)
* Lightning support
* **Better UI** with more variety of size and theme.
* Handle unconfirmed payments. RBF?
* More readily customisable donation button (text/color/QR code)
* Database integration for payment invoices
* Multiple choice of price feeds

# Disclaimer
BTCPyment is in very early development. As such, we are not responsible for any loss of funds, vulnerabilities with software, or any other grievances which may arise.

# Sponsor
Please consider [supporting me](https://btcpyment.nickfarrow.com) via my own instance of BTCPyment :). Corporate/whale support would greatly assist my ability to give 100% of my attention to BTCPyment and other Bitcoin projects, please email `baseddepartment@nickfarrow.com`.
