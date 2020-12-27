# BTCPyment
Existing non-custodial Bitcoin payment processors are bloated and difficult for the average person to install. BTCPyment strives to serve as an easily deployable, lightweight Bitcoin payment processor that keeps your coins with your keys by connecting to your own Bitcoin node.

## Demonstration


BTCPyment makes donation buttons simple; using Python and Javascript to talk to your own Bitcoin node, with an easy embed install. BTCPyment uses RPC to generate new addresses from your Bitcoin node, and monitors the payment status with your own copy of the blockchain. Soon, we hope to support lightning payments as well as function as a payment processor for a variety of web shops (woocommerce, shopify).

# Installation (easy!)
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
That's it! You should now be able to view your BTCPyment server at http://YOUR_SERVER_IP:8000/. If running locally, this will be `127.0.0.1:8000`. You might have to allow gunicorn through your firewall with `sudo ufw allow 8000`. You will want to run with nohup so it continues serving in the background:
```
nohup gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:8000 server:app > log.txt &
tail -f log.txt
```

## Embed Donation Button
Now embed the donation button into your website
```html
<iframe src="http://YOUR_SERVER_IP:8000/" style="margin: 0 auto;display:block;height:300px;border:none;overflow:hidden;" scrolling="no"></iframe>
```

## Using a Subdomain with nginx & certbot (HTTPS)
If your website uses https, then you can see your donation button at `http://YOUR_SERVER_IP:8000/` but not in the embeded iframe. It is best that we create a new subdomain like `btcpyment.yoursite.com` from which we can serve payments. If you use nginx, you can create a new file `/etc/nginx/sites-enabled/BTCpyment`:
```
server {
    listen 80;
    server_name btcpyment.YOURWEBSITE.com;

    location / {
        proxy_pass http://localhost:8000;
    }
}
```
we can now point our domain `btcpyment.YOURWEBSITE.com` DNS to our server IP and create HTTPS certificates by runnining `certbot`.

You can try provide gunicorn your website's https certificate with the flags `--certfile=cert.pem --keyfile=key.key`. If you use certbot for SSL, your keys are probably in `/etc/letsencrypt/live/`.

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
