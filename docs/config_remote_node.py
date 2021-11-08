# In this example config, we have two machines
# The first machine is our bitcoin node
# and the second remote machine hosts SatSale (perhaps same server you host your website on)

# Bitcoin Lightning Node    1.1.1.1     8332, 10009, 22 (bitcoind, lnd, SSH)
# SatSale                   2.2.2.2

# In this config we will tell SatSale to connect to our node,
# tunneling the required ports over SSH.
# SatSale can then talk to our node via localhost on 127.0.0.1
host = "127.0.0.1"
rpcport = "8332"
# If connections get kicked back, you may also need to set `rpcallowip=YOUR_SERVER_IP` in your `~/.bitcoin/bitcoin.conf`.

# From ~/.bitcoin/bitcoin.conf
username = "bitcoinrpc"
password = "rpcpassword"

# Wallet (empty "" if your node has a single wallet, OR wallet name/path as shown in `biitcoin-cli listwallets`)
wallet = ""

# File in which API key will be stored
api_key_path = "SatSale_API_key"


#### Connect To Remote Node ####
# Can use SSH or TOR
# to tunnel/relay ports required to talk to the node via RPC (gRPC for lightning)

# Telling SatSale to use SSH to tunnel the required ports
# Make sure this command works `ssh HOST@IP -q -N -L 8332:localhost:8332`
tunnel_host = "pi@1.1.1.1"

# We don't need to connect over tor if we're using SSH.
# or tor hidden service for RPC (see docs for how to set up), need onion:
tor_bitcoinrpc_host = None # e.g. "http://if...dwr.onion"
# and a tor proxy, default 127.0.0.1:9050 (for Tor Browser use "127.0.0.1:9150")
tor_proxy = None


#### Payment method ####
pay_method = "bitcoind"

#### Lightning ####
# Payment method has been switched to lnd
pay_method = "lnd"

# Specify lightning directory and port
lnd_dir = "~/.lnd/"
lnd_rpcport = "10009"


# Check for payment every xx seconds
pollrate = 15

# Payment expires after xx seconds
payment_timeout = 60*60

# Required confirmations for a payment
required_confirmations = 2

# Global connection attempts
connection_attempts = 3

# Generic redirect url after payment
redirect = "https://github.com/nickfarrow/satsale"

# DO NOT CHANGE THIS TO TRUE UNLESS YOU WANT ALL PAYMENTS TO AUTOMATICALLY
# BE CONSIDERED AS PAID.
free_mode = False
