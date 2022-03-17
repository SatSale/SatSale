import sys
import toml


for i, arg in enumerate(sys.argv):
    if arg == "--conf":
        print("Using config file {}".format(sys.argv[i+1]))
        conf_path = sys.argv[i+1]
        break
else:
    conf_path = "config.toml"

with open(conf_path, "r") as config_file:
    config = toml.load(config_file)

def get_opt(name, default):
    if name in config:
        return config[name]
    else:
        return default

host = get_opt("host", "127.0.0.1")
rpcport = get_opt("rpcport", "8332")
username = get_opt("username", "bitcoinrpc")
password = get_opt("password", "rpcpassword")
rpc_cookie_file = get_opt("rpc_cookie_file", "")
wallet = get_opt("wallet", "")
api_key_path = get_opt("api_key_path", "SatSale_API_key")
tunnel_host = get_opt("tunnel_host", None)
tunnel_port = get_opt("tunnel_port", "22")
tor_bitcoinrpc_host = get_opt("tor_bitcoinrpc_host", None)
tor_proxy = get_opt("tor_proxy", None)
pay_method = get_opt("pay_method", "bitcoind")
onchain_dust_limit = get_opt("onchain_dust_limit", 0.00000546)
lnd_dir = get_opt("lnd_dir", "~/.lnd/")
lnd_rpcport = get_opt("lnd_rpcport", "10009")
lnd_macaroon = get_opt("lnd_macaroon", "admin.macaroon")
clightning_rpc_file = get_opt("clightning_rpc_file", None)
pollrate = get_opt("pollrate", 15)
payment_timeout = get_opt("payment_timeout", 60*60)
required_confirmations = get_opt("required_confirmations", 2)
connection_attempts = get_opt("connection_attempts", 3)
redirect = get_opt("redirect", "https://github.com/nickfarrow/satsale")
base_currency = get_opt("base_currency", "USD")
currency_provider = get_opt("currency_provider", "COINGECKO")
lightning_address = get_opt("lightning_address", None)
lightning_address_comment = get_opt("lightning_address_comment", None)
liquid_address = get_opt("liquid_address", None)
paynym = get_opt("paynym", None)
free_mode = get_opt("free_mode", False)
loglevel = get_opt("loglevel", "DEBUG")
