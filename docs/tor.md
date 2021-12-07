# SatSale over tor
Currently you can use Tor in two ways
1) Connect SatSale to your Bitcoin node over a tor hidden service
2) Host SatSale as a Tor onion

## Bitcoin Node RPC Hidden Service
On your Bitcoin node machine install tor and in `/etc/tor/torrc`:
```
HiddenServiceDir /var/lib/tor/node_rpc/
HiddenServicePort 8332 127.0.0.1:8332
```
then
```
sudo systemctl restart tor
cat /var/lib/tor/node_rpc/hostname
```
to get the onion URL for your tor hidden service. Add this in `config.toml` like `tor_bitcoinrpc_host = "http://u7...bid.onion"`

On your SatSale machine, install tor and in `/etc/tor/torrc` (thanks @x_y:matrix.org):
```
SocksPort 127.0.0.1:9050 IsolateClientProtocol IsolateDestPort IsolateDestAddr ExtendedErrors IPv6Traffic PreferIPv6 KeepAliveIsolateSOCKSAuth
SocksPolicy accept 127.0.0.1
SocksPolicy reject *
```
Now start the tor proxy on your SatSale machine with `sudo tor` and SatSale is now configured to connect to your node over tor.


## SatSale Tor .Onion
On your SatSale machine, install tor and in `/etc/tor/torrc`:
```
HiddenServiceDir /var/lib/tor/satsale/
HiddenServiceVersion 3
HiddenServicePort 80 127.0.0.1:8000
```
then
```
sudo systemctl restart tor
cat /var/lib/tor/satsale/hostname
```
to get your onion URL. Go visit!

Note that this will only work in some Tor browsers, and often not in the official Tor Browser unless you fully enable javascript etc.
