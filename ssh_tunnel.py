import config
import invoice
from pay import bitcoind

import time
import subprocess


# If tunnel is required (might make things easier)
try:
    if config.tunnel_host is not None:
        command = ['ssh', config.tunnel_host, '-q', '-N', '-L', '{}:localhost:{}'.format(config.rpcport, config.rpcport)]
        print("Opening tunnel to {}.".format(' '.join(command)))
        tunnel_proc = subprocess.Popen(command)
    else:
        tunnel_proc = None
except Exception as e:
    print("FAILED TO OPEN TUNNEL. Exception: {}".format(e))
    tunnel_proc = None
    pass


def close_tunnel():
    if tunnel_proc is not None:
        tunnel_proc.kill()
        print("Tunnel closed.")
    return
