import subprocess
import time
import os
import logging

import config
from node import bitcoind


def open_tunnel(host, port):
    # If tunnel is required (might make things easier)
    try:
        command = [
            "ssh",
            config.tunnel_host,
            "-q",
            "-N",
            "-L",
            "{}:localhost:{}".format(port, port),
        ]
        logging.info("Opening tunnel to {}.".format(" ".join(command)))
        return subprocess.Popen(command)

    except Exception as e:
        logging.error("FAILED TO OPEN TUNNEL. Exception: {}".format(e))

    return None


def clightning_unix_domain_socket_ssh(rpc_store_dir=None):
    if rpc_store_dir is None:
        rpc_store_dir = os.getcwd()

    local_file = rpc_store_dir + "/lightning-rpc"

    # ssh -nNT -L lightning-rpc:~/.lightning/lightning-rpc config.tunnel_host
    try:
        command = [
            "ssh",
            "-nNT",
            "-L",
            "{}:{}".format(local_file, config.clightning_rpc_file),
            "{}".format(config.tunnel_host),
        ]
        logging.info("Opening tunnel to {}.".format(" ".join(command)))
        tunnel_proc = subprocess.Popen(command)
        return tunnel_proc

    except Exception as e:
        logging.error(
            "FAILED TO OPEN UNIX DOMAIN SOCKET OVER SSH. Exception: {}".format(e)
        )
        return None

    return None


def close_tunnel():
    if tunnel_proc is not None:
        tunnel_proc.kill()
        logging.info("Tunnel closed.")
    return


# Open tunnel
if config.tunnel_host is not None:
    tunnel_proc = open_tunnel(config.tunnel_host, config.rpcport)

    # Also for lnd if enabled
    if config.lnd_rpcport is not None:
        open_tunnel(config.tunnel_host, config.lnd_rpcport)

    # And if clightning is enabled
    if config.clightning_rpc_file is not None:
        clightning_unix_domain_socket_ssh()

    time.sleep(2)
else:
    tunnel_proc = None
