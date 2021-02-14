# Lightning Support
Recently we have added support for Lightning Network Daemon, with plans to extend support to clightning in the near future.

You will need to install the additional dependency lndgrpc:
```
pip3 install lndgrpc==0.2.0
```
If it fails to build or is taking a while, see this [solution](https://stackoverflow.com/questions/56357794/unable-to-install-grpcio-using-pip-install-grpcio#comment113013007_62500932).

To use lightning, you need to change your `pay_method` in `config.py`, and set your lightning directory on your node.
```python
pay_method = "lnd"
lnd_dir = "~/.lnd/"
lnd_rpcport = "10009"
```

Your lnd directory is used to find your `.tls` and `.macaroon` files that are required to talk to your lightning node. They are copied over SSH into your BTCPyment folder. If this copy fails, perhaps copy them manually and they will be identified on start up.

Your node will require sufficient liquidity and connection to receive payments.

You may also need a taller iframe for the longer address:
```
<iframe src="http://YOUR_SERVER_IP:8000/" style="margin: 0 auto;display:block;width:420px;height:360px;border:none;overflow:hidden;" scrolling="no"></iframe>
```
