# In this example config, we have two machines
# The first machine is our bitcoin node
# and the second remote machine hosts SatSale (perhaps same server you host your website on)

# Bitcoin Lightning Node    1.1.1.1     8332, 10009, 22 (bitcoind, lnd, SSH)
# SatSale                   2.2.2.2           

# In this config we will tell SatSale to connect to our node
# and tunnel the required ports over SSH.
# SatSale can then talk to our node on localhost 127.0.0.1
host = "127.0.0.1"
rpcport = "8332"
# If connections get kicked back, you may also need to set `rpcallowip=YOUR_SERVER_IP` in your `~/.bitcoin/bitcoin.conf`.

# From ~/.bitcoin/bitcoin.conf
username = "bitcoinrpc"
password = "RPAPASSWORD"

# Wallet ("" if single-wallet node, OR wallet name/path as shown in `biitcoin-cli listwallets`)
wallet = ""

# File in which API key will be stored
api_key_path = "BTCPyment_API_key"

# Telling SatSale to use SSH to tunnel the required ports
# Make sure SSHing into your node via command line works
tunnel_host = "pi@1.1.1.1"

# Check for payment every xx seconds
pollrate = 15

# Payment expires after xx seconds
payment_timeout = 60*60

# Required confirmations for a payment
required_confirmations = 2

# Global connection attempts
connection_attempts = 3

# Redirect url after payment
redirect = "https://github.com/nickfarrow/satsale"

# Payment method has been switched to lnd
#pay_method = "bitcoind"
pay_method = "lnd"

# Specify lightning directory and port
lnd_dir = "~/.lnd/"
lnd_rpcport = "10009"

# Login certificates automatically pulled from ~/.lnd/ and ~/.lnd/data/chain/bitcoin/mainnet/
lnd_macaroon = "invoice.macaroon"
lnd_cert = "tls.cert"

# DO NOT CHANGE THIS TO TRUE UNLESS YOU WANT ALL PAYMENTS TO AUTOMATICALLY
# BE CONSIDERED AS PAID.
free_mode = False
