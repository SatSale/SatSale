import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gateways.woo_webhook import validate_webhook_url


# URLs that must be rejected as potential SSRF targets. IP literals are used so
# the test does not depend on external DNS.
BLOCKED = [
    "http://127.0.0.1:8332",       # loopback (bitcoind rpc)
    "http://localhost:5000",       # loopback via hosts file
    "http://169.254.169.254/",     # link-local / cloud metadata
    "http://10.0.0.5/admin",       # private
    "http://172.16.0.1/",          # private
    "http://192.168.1.1/",         # private
    "http://100.64.0.1/",          # shared address space
    "http://0.0.0.0/",             # unspecified
    "http://[::1]/",               # ipv6 loopback
    "http://[fd00::1]/",           # ipv6 unique-local
    "ftp://example.com/",          # disallowed scheme
    "file:///etc/passwd",          # disallowed scheme
    "gopher://127.0.0.1/",         # disallowed scheme
    "http:///no-host",             # missing host
]

# URLs that must be allowed. Public IP literals avoid a DNS lookup.
ALLOWED = [
    "https://8.8.8.8/webhook",
    "http://1.1.1.1/notify?wc-api=x",
    "https://[2606:4700:4700::1111]/",
]


def test_validate_webhook_url_blocks_ssrf() -> None:
    for url in BLOCKED:
        with pytest.raises(ValueError):
            validate_webhook_url(url)


def test_validate_webhook_url_allows_public() -> None:
    for url in ALLOWED:
        validate_webhook_url(url)


def test_validate_webhook_url_empty_is_noop() -> None:
    validate_webhook_url(None)
    validate_webhook_url("")
