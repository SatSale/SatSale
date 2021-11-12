import subprocess
import time
import os

import config
from node import bitcoind


def open_tunnel(host, port):
    # If tunnel is required (might make things easier)
    try:
        if config.tunnel_host is not None:
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

def clightning_unix_domain_socket_ssh(rpc_store_dir=None):
    if rpc_store_dir is None:
        rpc_store_dir = os.getcwd()

    # ssh -nNT -L lightning-rpc:~/.lightning/lightning-rpc config.tunnel_host
    if config.tunnel_host is not None:
        try:
            command = [
                "ssh",
                "-nNT",
                "-L",
                "lightning-rpc:{}".format(config.clightning_rpc_file),
                "{}".format(config.tunnel_host),
            ]
            print("Opening tunnel to {}.".format(" ".join(command)))
            tunnel_proc = subprocess.Popen(command)
            return tunnel_proc

        except Exception as e:
            print("FAILED TO OPEN UNIX DOMAIN SOCKET OVER SSH. Exception: {}".format(e))
            tunnel_proc = None
            pass

    else:
        tunnel_proc = None

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
    if "lnd_rpcport" in config.__dict__.keys():
        open_tunnel(config.tunnel_host, config.lnd_rpcport)

    # And if clightning is enabled
    if "clightning_rpc_file" in config.__dict__.keys():
        clightning_unix_domain_socket_ssh()

    time.sleep(2)
else:
    tunnel_proc = None
