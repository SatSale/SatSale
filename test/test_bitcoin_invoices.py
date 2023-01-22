import os
import pytest
import sys
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from node.invoices import create_qr, encode_bitcoin_invoice, InvoiceType

tempdir = tempfile.TemporaryDirectory().name
qr_base_path = os.path.join(tempdir, "static", "qr_codes")
os.makedirs(qr_base_path, exist_ok=True)


@pytest.mark.parametrize(
    "invoice_data",
    [
        {
            "uuid": "Luke-Jr",
            "invoice": {
                "address": "175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W",
                "btc_value": 20.3
            },
            "invoice_type": InvoiceType.BIP21,
            "invoice_str": "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=20.3&label=Luke-Jr"
        },
        {
            "uuid": "Luke-Jr",
            "invoice": {
                "address": "175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W",
                "btc_value": 50,
                "message": "Donation for project xyz"
            },
            "invoice_type": InvoiceType.BIP21,
            "invoice_str": "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=50&label=Luke-Jr&message=Donation%20for%20project%20xyz"
        },
        {
            "uuid": "bolt11_example",
            "invoice": {
                "bolt11_invoice": "lnbc2500u1pvjluezsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygspp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdpquwpc4curk03c9wlrswe78q4eyqc7d8d0xqzpu9qrsgqhtjpauu9ur7fw2thcl4y9vfvh4m9wlfyz2gem29g5ghe2aak2pm3ps8fdhtceqsaagty2vph7utlgj48u0ged6a337aewvraedendscp573dxr"
            },
            "invoice_type": InvoiceType.BOLT11,
            "invoice_str": "lnbc2500u1pvjluezsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygspp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdpquwpc4curk03c9wlrswe78q4eyqc7d8d0xqzpu9qrsgqhtjpauu9ur7fw2thcl4y9vfvh4m9wlfyz2gem29g5ghe2aak2pm3ps8fdhtceqsaagty2vph7utlgj48u0ged6a337aewvraedendscp573dxr"
        },
        {
            "uuid": "bolt11_example",
            "invoice": {
                "address": "mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP",
                "btc_value": 0.02,
                "bolt11_invoice": "lntb20m1pvjluezsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygshp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqspp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3x9et2e20v6pu37c5d9vax37wxq72un989qrsgqdj545axuxtnfemtpwkc45hx9d2ft7x04mt8q7y6t0k2dge9e7h8kpy9p34ytyslj3yu569aalz2xdk8xkd7ltxqld94u8h2esmsmacgpghe9k8"
            },
            "invoice_type": InvoiceType.BOLT11,
            "invoice_str": "lntb20m1pvjluezsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygshp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqspp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3x9et2e20v6pu37c5d9vax37wxq72un989qrsgqdj545axuxtnfemtpwkc45hx9d2ft7x04mt8q7y6t0k2dge9e7h8kpy9p34ytyslj3yu569aalz2xdk8xkd7ltxqld94u8h2esmsmacgpghe9k8"
        },
        {
            "uuid": "bolt11_example",
            "invoice": {
                "address": "mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP",
                "btc_value": 0.02,
                "bolt11_invoice": "lntb20m1pvjluezsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygshp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqspp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3x9et2e20v6pu37c5d9vax37wxq72un989qrsgqdj545axuxtnfemtpwkc45hx9d2ft7x04mt8q7y6t0k2dge9e7h8kpy9p34ytyslj3yu569aalz2xdk8xkd7ltxqld94u8h2esmsmacgpghe9k8"
            },
            "invoice_type": InvoiceType.BIP21,
            "invoice_str": "bitcoin:mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP?amount=0.02&label=bolt11_example&lightning=lntb20m1pvjluezsp5zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygshp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqspp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3x9et2e20v6pu37c5d9vax37wxq72un989qrsgqdj545axuxtnfemtpwkc45hx9d2ft7x04mt8q7y6t0k2dge9e7h8kpy9p34ytyslj3yu569aalz2xdk8xkd7ltxqld94u8h2esmsmacgpghe9k8"
        },
    ]
    )
def test_bitcoin_invoice(invoice_data: list) -> None:
    assert (
        encode_bitcoin_invoice(
            invoice_data["uuid"], invoice_data["invoice"],
            invoice_data["invoice_type"]) == invoice_data["invoice_str"])
    create_qr(invoice_data["uuid"], invoice_data["invoice_str"], tempdir)
    qr_filename = os.path.join(qr_base_path,
                               "{}.png".format(invoice_data["uuid"]))
    assert (os.path.exists(qr_filename))
