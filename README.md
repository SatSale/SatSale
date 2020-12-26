# BTCPyment
Widely used non-custodial Bitcoin payment processors are bloated and difficult for the average person to install. BtcPyment strives to exist as an easily deployable, highly customisable, lightweight Bitcoin payment processor that keeps your coins belonging to your keys. Almost purely written in Python and Javascript, BtcPyment makes donation buttons simple for your website; via a simple embedded iframe that talks to your own Bitcoin node via Flask websockets.

# Installation
This should be easy to install.

# Features
* Lightweight, python and javascript talk to your own bitcoin node via websockets and ssh.
* Direct peer-to-peer payments without any middleman. No KYC, and greater privacy than donation systems with reused Bitcoin addresses.
* Natively supports all bitcoind node features through RPC.
* QR codes, customisable payment confirmations and payment expiry duration.
* No shitcoin bloat.
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
BtcPyment is in early development, as such we are not responsible for any loss of funds or vulnerabilities.
