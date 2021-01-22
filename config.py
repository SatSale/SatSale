# Bitcoin node connection settings
# Connecting through local host, or via forwarded ssh port
host = "127.0.0.1"
rpcport = "8332"
# From ~/.bitcoin/bitcoin.conf
username = "bitcoinrpc"
password = "RPAPASSWORD"

# SSH tunnel to node (raspberry pi!)
# Make sure this command works `ssh HOST@IP -q -N -L 8332:localhost:8332`
# This forwards the ports required to talk to the node via RPC (or gRPC in the case of lightning)
tunnel_host = "HOST@IP"

# Check for payment every xx seconds
pollrate = 15

# Payment expires after xx seconds
payment_timeout = 60*60

# Required confirmations for a payment
required_confirmations = 2

# Global connection attempts
connection_attempts = 3

# Payment method
pay_method = "bitcoind"
# Switch payment_method to lnd if you want to use lightning payments instead. And uncomment lnd_dir.
#pay_method = "lnd"
#lnd_dir = "~/.lnd/"

# DO NOT CHANGE THIS TO TRUE UNLESS YOU WANT ALL PAYMENTS TO AUTOMATICALLY
# BE CONSIDERED AS PAID.
config.free_mode = False
