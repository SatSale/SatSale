import sys
import toml


for i, arg in enumerate(sys.argv):
    if arg == "--conf":
        print("Using config file {}".format(sys.argv[i + 1]))
        conf_path = sys.argv[i + 1]
        break
else:
    if "pytest" in sys.modules:
        conf_path = "test/config.toml"
    else:
        conf_path = "config.toml"

with open(conf_path, "r") as config_file:
    config = toml.load(config_file)


def get_opt(name, default):
    if name in config["satsale"]:
        return config["satsale"][name]
    else:
        return default


def check_set_node_conf(name, default, node_conf):
    if name not in node_conf:
        if default is not None and default != "":
            print("using default {}: {}".format(name, default))
        node_conf[name] = default
    return


payment_methods = []
# This could be cleaned up into a single function that takes args, defaults, and required args.
for method_name in config["payment_methods"]:
    method_config = config[method_name]
    if method_name == "bitcoind":
        method_config["name"] = "bitcoind"
        check_set_node_conf("rpcport", "8332", method_config)
        check_set_node_conf("username", "bitcoinrpc", method_config)
        check_set_node_conf("password", "", method_config)
        check_set_node_conf("rpc_cookie_file", "", method_config)
        check_set_node_conf("wallet", "", method_config)
        check_set_node_conf("tor_bitcoinrpc_host", None, method_config)
        if (method_config["password"] == "" or method_config["password"] is None) and (
            method_config["rpc_cookie_file"] == ""
            or method_config["rpc_cookie_file"] is None
        ):
            raise KeyError(
                "Mising {} config: {} or {}".format(
                    method_name, "password", "rpc_cookie_file"
                )
            )

    elif method_name == "lnd":
        method_config["name"] = "lnd"
        check_set_node_conf("lnd_dir", "~/.lnd/", method_config)
        check_set_node_conf("lnd_rpcport", "10009", method_config)
        check_set_node_conf("lnd_macaroon", "invoice.macaroon", method_config)
        check_set_node_conf("lightning_address", None, method_config)
        check_set_node_conf("lightning_address_comment", None, method_config)

    elif method_name == "lndhub":
        method_config["name"] = "lndhub"
        check_set_node_conf("bw_login", None, method_config)
        check_set_node_conf("bw_password", None, method_config)
        check_set_node_conf("backend_url", "https://lndhub.herokuapp.com", method_config)
        check_set_node_conf("lightning_address", None, method_config)
        check_set_node_conf("lightning_address_comment", None, method_config)

    elif method_name == "clightning":
        method_config["name"] = "clightning"
        check_set_node_conf("clightning_rpc_file", None, method_config)
        check_set_node_conf("lightning_address", None, method_config)
        check_set_node_conf("lightning_address_comment", None, method_config)
        if (
            method_config["clightning_rpc_file"] == ""
            or method_config["clightning_rpc_file"] is None
        ):
            raise KeyError(
                "Mising {}: config {}".format(method_name, "clightning_rpc_file")
            )

    elif method_name == "xpub":
        method_config["name"] = "xpub"
        check_set_node_conf("xpub", None, method_config)
        if method_config["xpub"] == "" or method_config["xpub"] is None:
            raise KeyError("Mising {}: config {}".format(method_name, "xpub"))
        check_set_node_conf("api_url", "https://mempool.space/api", method_config)

    else:
        raise Exception("Unknown payment method: {}".format(method_name))

    payment_methods.append(method_config)

supported_currencies = get_opt("supported_currencies", ["USD"])
if "BTC" in supported_currencies:
    supported_currencies.append("sats")

base_currency = get_opt("base_currency", "USD")
if base_currency not in supported_currencies:
    raise Exception("base_currency must be one of supported_currencies")

currency_provider = get_opt("currency_provider", "COINGECKO")
if currency_provider not in ["COINDESK", "COINGECKO"]:
    raise Exception("Unsupported currency price feed provider: {}".format(
        currency_provider))

host = get_opt("host", "127.0.0.1")
api_key_path = get_opt("api_key_path", "SatSale_API_key")
tunnel_host = get_opt("tunnel_host", None)
tunnel_port = get_opt("tunnel_port", 22)
tor_proxy = get_opt("tor_proxy", None)
onchain_dust_limit = get_opt("onchain_dust_limit", 0.00000546)
ln_upper_limit = get_opt("ln_upper_limit", 0.10000000)
node_info = get_opt("node_info", None)
pollrate = get_opt("pollrate", 15)
payment_timeout = get_opt("payment_timeout", 60 * 60)
required_confirmations = get_opt("required_confirmations", 2)
connection_attempts = get_opt("connection_attempts", 3)
store_name = get_opt("store_name", "SatSale")
redirect = get_opt("redirect", "https://github.com/nickfarrow/satsale")
bitcoin_rate_multiplier = get_opt("bitcoin_rate_multiplier", 1.00)
allowed_underpay_amount = get_opt("allowed_underpay_amount", 0.00000001)
liquid_address = get_opt("liquid_address", None)
paynym = get_opt("paynym", None)
free_mode = get_opt("free_mode", False)
loglevel = get_opt("loglevel", "DEBUG")

if allowed_underpay_amount < 0:
    raise Exception("allowed_underpay_amount cannot be negative")

#print(config)
#print(tunnel_host)
