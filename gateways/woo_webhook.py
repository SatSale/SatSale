import hmac
import hashlib
import json
import codecs
import time
import requests

def hook(secret, payload):
    paid_time = int(time.time())
    params = {"wc-api":"wc_btcpyment_gateway", 'id' : payload['id'], 'time' : str(paid_time)}
    message = (str(paid_time) + '.' + json.dumps(params, separators=(',', ':'))).encode('utf-8')

    key = codecs.decode(secret, 'hex')
    hash = hmac.new(key, message, hashlib.sha256).hexdigest()
    headers={'Content-Type': 'application/json', 'X-Signature' : hash}

    response = requests.get(
        payload['w_url'], params=params, headers=headers)

    return response
