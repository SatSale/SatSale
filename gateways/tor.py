import requests
import time
import logging

import config

time.sleep(3)

if config.tor_proxy is None:
    config.tor_proxy = "127.0.0.1:9050"

logging.info("Using tor proxies {}".format(config.tor_proxy))
session = requests.session()
session.proxies = {
    "http": "socks5h://{}".format(config.tor_proxy),
    "https": "socks5h://{}".format(config.tor_proxy),
}

logging.info(
    "Checking tor circuit IP address... You should check this is different to your IP."
)
r = session.get("http://httpbin.org/ip")
logging.info(r.text)
