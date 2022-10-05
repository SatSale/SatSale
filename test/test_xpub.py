import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from node.xpub import xpub


def test_xpub():
    # Account 0, root = m/84'/0'/0'
    test_zpub = "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
    pseudonode = xpub({"xpub": test_zpub, "bip": "BIP84"})
    assert (
        pseudonode.get_address_at_index(0)
        == "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"
    )
    assert (
        pseudonode.get_address_at_index(1)
        == "bc1qnjg0jd8228aq7egyzacy8cys3knf9xvrerkf9g"
    )

    test_xpub = "xpub6C5uh2bEhmF8ck3LSnNsj261dt24wrJHMcsXcV25MjrYNo3ZiduE3pS2Xs7nKKTR6kGPDa8jemxCQPw6zX2LMEA6VG2sypt2LUJRHb8G63i"
    pseudonode2 = xpub({"xpub": test_xpub, "bip": "BIP44"})
    assert pseudonode2.get_address_at_index(0) == "1LLNwhAMsS3J9tZR2T4fFg2ibuZyRSxFZg"
    assert pseudonode2.get_address_at_index(1) == "1EaEuwMRVKdWBoKeJZzJ8abUzVbWNhGhtC"
