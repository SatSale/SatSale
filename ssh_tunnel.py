import subprocess

import config
import invoice
from pay import bitcoind

def open_tunnel(host, port):
    # If tunnel is required (might make things easier)
    try:
        if host is not None:
            command = [
                "ssh",
                config.tunnel_host,
                "-q",
                "-N",
                "-L",
                "{}:localhost:{}".format(port, port),
            ]
            print("Opening tunnel to {}.".format(" ".join(command)))
            tunnel_proc = subprocess.Popen(command)
            return tunnel_proc

        else:
            tunnel_proc = None
    except Exception as e:
        print("FAILED TO OPEN TUNNEL. Exception: {}".format(e))
        tunnel_proc = None
        pass
    return

def close_tunnel():
    if tunnel_proc is not None:
        tunnel_proc.kill()
        print("Tunnel closed.")
    return

# Open tunnel
if config.tunnel_host is not None:
    tunnel_proc = open_tunnel(config.tunnel_host, config.rpcport)

    # Also for lnd if enabled
    if 'lnd_rpcport' in config.__dict__.keys():
        open_tunnel(config.tunnel_host, config.lnd_rpcport)

else:
    tunnel_proc = None
