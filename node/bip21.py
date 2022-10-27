# https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki
# bitcoin:<address>[?amount=<amount>][?label=<label>][?message=<message>]

from typing import Union
from urllib.parse import quote, urlencode
import re


def _is_bip21_amount_str(amount: str) -> bool:
    return re.compile(r"^[0-9]{1,8}(\.[0-9]{1,8})?$").match(
        amount) is not None


def _validate_bip21_amount(amount: Union[float, int, str]) -> None:
    if not _is_bip21_amount_str(str(amount)):
        raise ValueError("Invalid BTC amount " + str(amount))


def encode_bip21_uri(address: str, params: Union[dict, list]) -> str:
    uri = "bitcoin:{}".format(address)
    if len(params) > 0:
        if "amount" in params:
            _validate_bip21_amount(params["amount"])
        uri += "?" + urlencode(params, quote_via=quote)
    return uri
