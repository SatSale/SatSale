import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from node.bip21 import encode_bip21_uri


def test_bip21_encode() -> None:
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {}) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W"
    )
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "label": "Luke-Jr"
        }) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?label=Luke-Jr"
    )
    # Both dictionary and list of tuples should work
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("label", "Luke-Jr")
        ]) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?label=Luke-Jr"
    )
    # Use list of tuples version for multiple parameter tests, as dicts don't
    # have guaranteed ordering.
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("amount", 20.3),
            ("label", "Luke-Jr")
        ]) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=20.3&label=Luke-Jr"
    )
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("amount", 50),
            ("label", "Luke-Jr"),
            ("message", "Donation for project xyz")
        ]) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=50&label=Luke-Jr&message=Donation%20for%20project%20xyz"
    )
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("req-somethingyoudontunderstand", 50),
            ("req-somethingelseyoudontget", 999)
        ]) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?req-somethingyoudontunderstand=50&req-somethingelseyoudontget=999"
    )
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("somethingyoudontunderstand", 50),
            ("somethingelseyoudontget", 999)
        ]) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?somethingyoudontunderstand=50&somethingelseyoudontget=999"
    )
    # Test removal of trailing zeros after decimal point for amounts
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "50.00000000"
        }) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=50"
    )
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "20.30000000"
        }) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=20.3"
    )
    # Test that zeros from the right side of integers aren't removed
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "5000.00000000"
        }) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=5000"
    )
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "5000"
        }) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=5000"
    )
    # Test very small amounts
    assert (
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "0.00000001"
        }) ==
        "bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=0.00000001"
    )
    # Invalid amounts must raise ValueError
    with pytest.raises(ValueError):
        # test dicts
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": ""
        })
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "XYZ"
        })
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "100'000"
        })
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "100,000"
        })
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", {
            "amount": "100000000"
        })
        # test list of tuples
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("amount", "")
        ])
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("amount", "XYZ")
        ])
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("amount", "100'000")
        ])
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("amount", "100,000")
        ])
        encode_bip21_uri("175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W", [
            ("amount", "100000000")
        ])
