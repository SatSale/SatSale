import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from node.xpub import xpub


@pytest.mark.parametrize(
    "wallet",
    [
        {
            "xpub": "xpub6C5uh2bEhmF8ck3LSnNsj261dt24wrJHMcsXcV25MjrYNo3ZiduE3pS2Xs7nKKTR6kGPDa8jemxCQPw6zX2LMEA6VG2sypt2LUJRHb8G63i",
            "bip": "BIP44",
            "addresses": [
                "1LLNwhAMsS3J9tZR2T4fFg2ibuZyRSxFZg",
                "1EaEuwMRVKdWBoKeJZzJ8abUzVbWNhGhtC"
            ]
        },
        {
            "xpub": "tpubDC5FSnBiZDMmhiuCmWAYsLwgLYrrT9rAqvTySfuCCrgsWz8wxMXUS9Tb9iVMvcRbvFcAHGkMD5Kx8koh4GquNGNTfohfk7pgjhaPCdXpoba",
            "bip": "BIP44",
            "addresses": [
                "mkpZhYtJu2r87Js3pDiWJDmPte2NRZ8bJV",
                "mzpbWabUQm1w8ijuJnAof5eiSTep27deVH"
            ]
        },
        # https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki
        {
            "xpub": "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs",
            "bip": "BIP84",
            "addresses": [
                "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu",
                "bc1qnjg0jd8228aq7egyzacy8cys3knf9xvrerkf9g"
            ]
        },
        {
            "xpub": "vpub5YZPoYDnSnoNXpRcCV7LhGagEYMcLQVHKbdDGAi3HRQ1mBuVQsVBvJBW8sKpuyNYwyUyNVQFfTmdsErvpePTNhpdoN8syxojcuHv4uQyRZY",
            "bip": "BIP84",
            "addresses": [
                "tb1qjwg87jdkl52rv0djjqxa5fmaawdsssfjmx3sj5",
                "tb1qv3fngl0tlhensu6rr3n8wwrskpxx7wweq4ypj4"
            ]
        },
        {
            "xpub": "xpub6CatWdiZiodmUeTDp8LT5or8nmbKNcuyvz7WyksVFkKB4RHwCD3XyuvPEbvqAQY3rAPshWcMLoP2fMFMKHPJ4ZeZXYVUhLv1VMrjPC7PW6V",
            "bip": "BIP84",
            "addresses": [
                "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu",
                "bc1qnjg0jd8228aq7egyzacy8cys3knf9xvrerkf9g"
            ]
        },
        {
            "xpub": "tpubDCbYw7PJTRqnWCzhKPfgKN73ubkAD2yLhTFxBWYxPLufcgCezQfQJsAcRKKnSHddZAFVV27F7tJnKzafeu4irce8beH2qK6wkK1cc4DJ9nb",
            "bip": "BIP84",
            "addresses": [
                "tb1qjwg87jdkl52rv0djjqxa5fmaawdsssfjmx3sj5",
                "tb1qv3fngl0tlhensu6rr3n8wwrskpxx7wweq4ypj4"
            ]
        },
        # https://github.com/bitcoin/bips/blob/master/bip-0086.mediawiki
        {
            "xpub": "xpub6BgBgsespWvERF3LHQu6CnqdvfEvtMcQjYrcRzx53QJjSxarj2afYWcLteoGVky7D3UKDP9QyrLprQ3VCECoY49yfdDEHGCtMMj92pReUsQ",
            "bip": "BIP86",
            "addresses": [
                "bc1p5cyxnuxmeuwuvkwfem96lqzszd02n6xdcjrs20cac6yqjjwudpxqkedrcr",
                "bc1p4qhjn9zdvkux4e44uhx8tc55attvtyu358kutcqkudyccelu0was9fqzwh"
            ]
        },
        {
            "xpub": "tpubDDfvzhdVV4unsoKt5aE6dcsNsfeWbTgmLZPi8LQDYU2xixrYemMfWJ3BaVneH3u7DBQePdTwhpybaKRU95pi6PMUtLPBJLVQRpzEnjfjZzX",
            "bip": "BIP86",
            "addresses": [
                "tb1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqlqt9zj",
                "tb1p90h6z3p36n9hrzy7580h5l429uwchyg8uc9sz4jwzhdtuhqdl5eqmpwq6n"
            ]
        }
    ])
def test_xpub(wallet: dict) -> None:
    pseudonode = xpub({"xpub": wallet["xpub"], "bip": wallet["bip"]})
    for i in range(len(wallet["addresses"])):
        assert (pseudonode.get_address_at_index(i) == wallet["addresses"][i])
