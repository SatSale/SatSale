import hmac
import hashlib
import json
import codecs
import time
import socket
import ipaddress
from urllib.parse import urlparse
import requests


def validate_webhook_url(url):
    # Reject webhook URLs that could be used for SSRF. Only public http/https
    # hosts are allowed; raises ValueError if the URL uses another scheme or
    # resolves to a private/loopback/link-local/reserved address (including
    # cloud metadata endpoints such as 169.254.169.254).
    if not url:
        return
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Webhook URL must use http or https")
    host = parsed.hostname
    if not host:
        raise ValueError("Webhook URL has no host")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        addrinfo = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        raise ValueError("Webhook URL host could not be resolved")
    for res in addrinfo:
        ip = ipaddress.ip_address(res[4][0])
        if not ip.is_global:
            raise ValueError("Webhook URL resolves to a non-public address")


def hook(satsale_secret, invoice, order_id):
    key = codecs.decode(satsale_secret, "hex")

    # Calculate a secret that is required to send back to the
    # woocommerce gateway, proving we did not modify id nor amount.
    secret_seed = str(int(100 * float(invoice["base_value"]))).encode("utf-8")
    secret = hmac.new(key, secret_seed, hashlib.sha256).hexdigest()

    # The main signature  which proves we have paid, and very recently!
    paid_time = int(time.time())
    params = {"wc-api": "wc_satsale_gateway", "time": str(paid_time), "id": order_id}
    message = (str(paid_time) + "." + json.dumps(params, separators=(",", ":"))).encode(
        "utf-8"
    )

    # Calculate the hash
    hash = hmac.new(key, message, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Signature": hash,
        "X-Secret": secret,
    }

    # Send the webhook response, confirming the payment with woocommerce.
    response = requests.get(
        invoice["webhook"], params=params, headers=headers,
        timeout=10, allow_redirects=False,
    )

    return response
