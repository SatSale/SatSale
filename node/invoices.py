import qrcode
import os
from enum import Enum

from node.bip21 import encode_bip21_uri
from utils import btc_amount_format


class InvoiceType(Enum):
    BIP21 = 1,
    BOLT11 = 2


def encode_bitcoin_invoice(uuid: str, invoice: dict,
                           invtype: InvoiceType) -> str:

    if invtype == InvoiceType.BIP21:
        assert (invoice["address"])
        assert (invoice["btc_value"])
        bip21_params = {
            "amount": btc_amount_format(invoice["btc_value"]),
            "label": uuid
        }
        if "message" in invoice:
            bip21_params["message"] = invoice["message"]
        if "bolt11_invoice" in invoice and invoice["bolt11_invoice"]:
            bip21_params["lightning"] = invoice["bolt11_invoice"]
        return encode_bip21_uri(invoice["address"], bip21_params)

    elif invtype == InvoiceType.BOLT11:
        assert (invoice["bolt11_invoice"])
        return invoice["bolt11_invoice"]

    else:
        raise NotImplementedError(
            "Unsupported Bitcoin invoice type {}".format(invtype))


def create_qr(uuid: str, qr_str: str, base_path: str = ".") -> None:
    img = qrcode.make(qr_str)
    img.save(os.path.join(
        base_path, "static", "qr_codes", "{}.png".format(uuid)))
    return
