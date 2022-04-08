import sys
import toml


for i, arg in enumerate(sys.argv):
    if arg == "--conf":
        print("Using config file {}".format(sys.argv[i + 1]))
        conf_path = sys.argv[i + 1]
        break
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

    else:
        Exception("Unknown payment method: {}".format(method_name))

    payment_methods.append(method_config)

host = get_opt("host", "127.0.0.1")
api_key_path = get_opt("api_key_path", "SatSale_API_key")
tunnel_host = get_opt("tunnel_host", None)
tunnel_port = get_opt("tunnel_port", 22)
tor_proxy = get_opt("tor_proxy", None)
onchain_dust_limit = get_opt("onchain_dust_limit", 0.00000546)
node_info = get_opt("node_info", None)
pollrate = get_opt("pollrate", 15)
payment_timeout = get_opt("payment_timeout", 60 * 60)
required_confirmations = get_opt("required_confirmations", 2)
connection_attempts = get_opt("connection_attempts", 3)
redirect = get_opt("redirect", "https://github.com/nickfarrow/satsale")
base_currency = get_opt("base_currency", "USD")
currency_provider = get_opt("currency_provider", "COINGECKO")
liquid_address = get_opt("liquid_address", None)
paynym = get_opt("paynym", None)
free_mode = get_opt("free_mode", False)
loglevel = get_opt("loglevel", "DEBUG")

#print(config)
#print(tunnel_host)
