# inadequate

import requests
import sys

args = sys.argv
if len(args) <= 1:
    SATSALE_API = "http://127.0.0.1:8000/api"
else:
    SATSALE_API = args[1]


def get_request_api(endpoint, payload={}):
    try:
        print("Calling {} with data {}".format(SATSALE_API + "/" + endpoint, payload))
        r = requests.get(SATSALE_API + "/" + endpoint, params=payload)
        if not r.ok:
            print(r)
            return False
        else:
            print(r.json())
            return r.json()

    except Exception as e:
        print(e)
        return False


def compare_json(checking_json, comparison_json):
    for key in comparison_json.keys():
        if key not in checking_json.keys():
            print("Missing key from response {}".format(key))
            return False
        if checking_json[key] != checking_json[key]:
            print(
                "Unexpected response mismatch {} expected {}".format(
                    checking_json, comparison_json
                )
            )
            return False

    return True


def check_createpayment():
    return get_request_api("createpayment", payload={"amount": 1}) != False


def check_checkpayment():
    pay_response = get_request_api("createpayment", payload={"amount": 2})
    print(pay_response)
    if pay_response == False:
        return False

    return (
        get_request_api(
            "checkpayment", payload={"uuid": pay_response["invoice"]["uuid"]}
        )
        != False
    )


if __name__ == "__main__":
    check_checkpayment()
    print("Sucessfully generated invoice and checked payment")
