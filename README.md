# SatSale
## (previously satsale)
<!---Existing self-custody Bitcoin payment processors are bloated, difficult to install, and not easily customisable.--->
satsale is a simple, easily deployable, lightweight Bitcoin payment processor that connects to your own Dojo.

Donation Button     ----->  |  Bitcoin Payment Gateway
:-------------------------:|:-------------------------:
[![Donate demo](https://user-images.githubusercontent.com/24557779/119219951-5345c000-bb2b-11eb-8753-bf6fd80263df.png)](https://try.satsale.org/) <br />(Click for embed demo)<br /> Initiates payment -----> |  [![Store demo](https://user-images.githubusercontent.com/24557779/119220001-8b4d0300-bb2b-11eb-9a2d-0b8ba24ca8b1.png)](https://store.satsale.com/) <br />(Click for WordPress payments demo)

SatSale currently serves as
1. Donation button for your website that you can easily embed/link to anywhere.
2. Bitcoin payment gateway, including a Woocommerce plugin that easily turns ANY Wordpress site into a Bitcoin accepting store.

SatSale makes donation buttons simple - easy copy paste the one line HTML iframe into your site. With a simple Python backend to talk to your own Dojo, SatSale uses RPC to generate new addresses, and monitors the payment status with your own copy of the blockchain.

# Features
* Process payments with your own Bitcoin node via RPC and SSH using Dojo.
* Direct peer-to-peer payments without any middleman. No KYC, and greater privacy than donation systems wher Bitcoin addresses are reused multiple times.
* Lightweight and highly extendable, basic html and css stying. Modular Python backend, take a [look at the code](satsale.py) or [lnd.py](/pay/lnd.py)!* Natively extendable to all bitcoind node features (e.g. segwit) through RPC.
* QR codes, customizable required payment confirmations and payment expiry time.
* No shitcoin bloat. Bitcoin only.

# Installation (short!)
You require a Raspberry Pi / server (VPS) to host an instance of satsale on, and a Dojo full node. If you don't have a Dojo, you should [install one](https://code.samourai.io/dojo/samourai-dojo/).

### Configure Dojo
##### Edit the `docker-bitcoind.conf` file.
```
sudo nano ~/dojo/samourai-dojo-vX.X/docker/my-dojo/conf/docker-bitcoind.conf
```
##### Change RPC exposure variable.
```
BITCOIND_RPC_EXTERNAL=on
```
##### Edit relevant `restart.sh` file.
```
sudo nano ~/dojo/samourai-dojo-vX.X/docker/my-dojo/bitcoin/restart.sh
```
##### Change bitcoind_options variables. Mind the second `-rpcallowip=[Remote Server IP]` variable. If running satsale on the same machine as your Dojo, delete that line completely.
```
bitcoind_options=(
-datadir=/home/bitcoin/.bitcoin
-printtoconsole=1
-dbcache=$BITCOIND_DB_CACHE
-disablewallet=0
-dns=$BITCOIND_DNS
-dnsseed=$BITCOIND_DNSSEED
-maxconnections=$BITCOIND_MAX_CONNECTIONS
-maxmempool=$BITCOIND_MAX_MEMPOOL
-mempoolexpiry=$BITCOIND_MEMPOOL_EXPIRY
-minrelaytxfee=$BITCOIND_MIN_RELAY_TX_FEE
-port=8333
-proxy=172.28.1.4:9050
-rpcallowip=0.0.0.0/0
-rpcallowip=[Remote Server IP if Being Used](Optional)
-rpcbind=172.28.1.5
-rpcpassword=$BITCOIND_RPC_PASSWORD
-rpcport=28256
-rpcthreads=$BITCOIND_RPC_THREADS
-rpcworkqueue=$BITCOIND_PRC_WORK_QUEUE
-rpcuser=$BITCOIND_RPC_USER
-server=1
-txindex=1
-zmqpubhashblock=tcp://0.0.0.0/9502
-zmqpubrawtx=tcp://0.0.0.0/9501
)
```
##### Force rebuilding of Dojo Docker Containers.
```
cd ~/dojo/samourai-dojo-vX.X/docker/my-dojo
./dojo.sh stop
./dojo.sh upgrade --nocache
```
This will not actually upgrade your Dojo, as you should see a message asking if you are sure you want to upgrade to Dojo v1.9, which is already the current version. Choose `y` there and wait for the upgrade script to run its course and rebuild Docker containers with the new variables enacted. Once you see logs for Docker Containers like Tor, Nodejs, and Bitcoind begin appearing in your terminal window, you can `CTRL+C` to exit the process. Dojo will continue running.

##### Next create and load a wallet.
```
./dojo.sh bitcoin-cli createwallet "satsale"
```
- Note: If you want to create more than one wallet (i.e. one for regular use and a separate wallet for donations) that is fine. You would simply create another wallet with a different specified name, as in `./dojo.sh bitcoin-cli createwallet "personal"`, which just distinguishes which wallet satsale will look for later when you adjust configuration.


### Installing satsale
##### Make sure Python3 and Pip are installed.
```
sudo apt-get update
sudo apt install python3
sudo apt install python3-pip
```
##### Clone and install dependencies
```
git clone https://github.com/nickfarrow/SatSale
cd SatSale/
pip3 install -r requirements.txt
```

### Connect to your Bitcoin Node
##### Edit these `config.py` configurations to point to your Dojo:
```
host = "127.0.0.1"
rpcport = "28256"
username = "bitcoinrpc"
password = "RPCPASSWORD"
wallet = "satsale"
```
(You can find these in `~/dojo/samourai-dojo-v1.9/docker/my-dojo/conf/docker-bitcoind.conf`). If your node is remote to your server, you can specify an SSH `tunnel_host = "pi@192.168.0.252"` that will forward `rpcport`. You may also need to set `rpcallowip=YOUR_SERVER_IP` in your `~/dojo/samourai-dojo-v1.9/docker/my-dojo/bitcoin/restart.sh`. If you want to use lightning network payments, see [Lightning instructions](docs/lightning.md)].

### Run satsale
##### Run satsale with
```
gunicorn -w 1 -b 0.0.0.0:8000 satsale:app
```

That's it! You should now be able to view your SatSale server at `http://YOUR_SERVER_IP:8000/`. If running locally, this will be `127.0.0.1:8000`.

If running on a Raspberry Pi, you will want to [forward port 8000 in your router settings](https://user-images.githubusercontent.com/24557779/105681219-f0f5fd80-5f44-11eb-942d-b574367a161f.png) so that SatSale is also visible at your external IP address. You might have to allow gunicorn through your firewall with `sudo ufw allow 8000`.

## You will want to run gunicorn with nohup so it continues serving in the background. In the terminal window currently running satsale, first `CTRL+C`, then:
```
nohup gunicorn -w 1 0.0.0.0:8000 satsale:app > log.txt 2>&1 &
tail -f log.txt
```

### Embed a Donation Button
Now embed the donation button into your website HTML:
```
<iframe src="http://YOUR_SERVER_IP:8000/" style="margin: 0 auto;display:block;width:600px;height:480px;border:none;overflow:hidden;" scrolling="yes"></iframe>
```
Changing `YOUR_SERVER_IP` to the IP address of the machine you're running satsale on. Optionally, you can redirect a domain to that IP and use that instead, removing the port `:8000` from the end of `YOUR_DOMAIN_NAME`.

### Using HTTPS & Domains
Embedded iframes are easy if your site only uses HTTP. But if your site uses HTTPS, then you can see your donation button at `http://YOUR_SERVER_IP:8000/` but will not be able to see it in an embedded iframe. See [HTTPS instructions](docs/HTTPS.md).

# Payment Gateway (Woocommerce)
Currently we have a plugin for Woocommerce in Wordpress that makes Bitcoin webstores extremely easy, [please click here for installation instructions](docs/woocommerce.md). SatSale acts as a custom payment gateway for Woocommerce via the php plugin found in `/gateways`. We have plans to extend to other web stores in the future.

# Contributions welcomed
### You only need a little python!
The main code can be found in [satsale.py](satsale.py). The client-side logic for the donation button sits in [static/server_connection.js](static/server_connection.js), invoice structure and bitcoind interface in [invoice/](invoice/), button appearance in [templates/index.html](templates/index.html), and Woocommerce plugin in [gateways/woo_satsale.php](gateways/woo_satsale.php). Please have ago at implementing some of the things below!

![docs/diagram.png](docs/diagram.png)

# Coming soon:
* **Better UI** with more variety of size and theme.
    * Add a currency toggle between BTC/USD on donation html.
* Handle unconfirmed payments. What is the best course of action?
* More readily customisable donation button (text/color/QR code)
* Database integration for payment invoices
* Variety or easily customisable price feeds

# Disclaimer
SatSale is in very early development. As such, we are not responsible for any loss of funds, vulnerabilities with software, or any other grievances which may arise. Always confirm large payments manually.

# Sponsor
Please consider [supporting me](https://btcpyment.nickfarrow.com) via my own instance of SatSale :). Corporate/whale support would greatly assist my ability to give 100% of my attention to SatSale and other Bitcoin projects, please email `baseddepartment@nickfarrow.com`.
