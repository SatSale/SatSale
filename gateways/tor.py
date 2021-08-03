import socks
import json
import requests
import time

import config

time.sleep(3)

print("Using tor proxies {}:{}".format("localhost", 9050))
session = requests.session()
session.proxies = {
    "http": "socks5h://localhost:9050",
    "https": "socks5h://localhost:9050",
}

print(
    "Checking tor circuit IP address... You should check this is different to your IP."
)
r = session.get("http://httpbin.org/ip")
print(r.text)
