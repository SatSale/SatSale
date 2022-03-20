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
        print("Opening tunnel to {}.".format(" ".join(command)))
        return subprocess.Popen(command)

    except Exception as e:
        print("FAILED TO OPEN TUNNEL. Exception: {}".format(e))

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
        print("Opening tunnel to {}.".format(" ".join(command)))
        tunnel_proc = subprocess.Popen(command)
        return tunnel_proc

    except Exception as e:
        print(
            "FAILED TO OPEN UNIX DOMAIN SOCKET OVER SSH. Exception: {}".format(e)
        )

    return None


def rm_lightning_rpc_file():
    if os.path.exists("lightning-rpc"):
        os.remove("lightning-rpc")
    return

def close_tunnels(ssh_processes):
    for proc in ssh_processes:
        try:
            proc.kill()
        except Exception as e:
            continue

    if config.clightning_rpc_file is not None:
        rm_lightning_rpc_file()
    return


# Open tunnel
def open_tunnels():
    # global ssh_tunnel_processes
    ssh_tunnel_processes = []
    if config.tunnel_host is not None:
        ssh_tunnel_processes.append(open_tunnel(config.tunnel_host, config.rpcport))

        # Also for lnd if enabled
        if config.lnd_rpcport is not None:
            ssh_tunnel_processes.append(open_tunnel(config.tunnel_host, config.lnd_rpcport))

        # And if clightning is enabled
        if config.clightning_rpc_file is not None:
            ssh_tunnel_processes.append(clightning_unix_domain_socket_ssh())

    return [proc for proc in ssh_tunnel_processes if proc is not None]
