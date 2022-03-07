# Lightning Support
We support both Lightning Network Daemon (lnd) and clightning.
An example config for lnd can be found in [/docs/config_lightning.py](/docs/config_lightning.py).

If installing the python library lndgrpc requirement failed, see this [solution](https://stackoverflow.com/questions/56357794/unable-to-install-grpcio-using-pip-install-grpcio#comment113013007_62500932).


## LND
To connect to a LND node, you need to set `payment_methods = ["lnd", "bitcoind"]` in `config.toml`, and set your lightning directory on your node.
```toml
[lnd]
host = "127.0.0.1"
lnd_dir = "~/.lnd/"
lnd_rpcport = "10009"
lnd_macaroon = "invoice.macaroon"
```


## clightning
To use clightning,  you need to set `payment_methods = ["clightning", "bitcoind"]` in `config.toml`, and
```toml
[clightning]
clightning_rpc_file = "/home/user/.lightning/bitcoin/lightning-rpc"
```
If remote clightning, make sure `ssh -nNT -L {local_lightning-rpc}:{remote_lightning-rpc} {tunnel_host}` creates a lightning-rpc unix domain socket. (use full paths local: /home/install/satsale/lightning-rpc).

## Notes
Your lnd directory is used to find your `.tls` and `.macaroon` files that are required to talk to your lightning node. They are copied over SSH into your SatSale folder. If this copy fails, perhaps copy them manually and they will be identified on start up.

Your node will require sufficient liquidity and connection to receive payments.

You may also need a taller iframe for the longer address:
```
<iframe src="http://YOUR_SERVER_IP:8000/" style="margin: 0 auto;display:block;width:420px;height:380px;border:none;overflow:hidden;" scrolling="no"></iframe>
```
