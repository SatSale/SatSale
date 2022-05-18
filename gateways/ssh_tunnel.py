import subprocess
import os
import logging

import config


def open_tunnel(host, port):
    # If tunnel is required (might make things easier)
    try:
        command = [
            "ssh",
            "-q",
            "-N",
            "-L",
            "{}:localhost:{}".format(port, port),
            config.tunnel_host,
            "-p {}".format(config.tunnel_port),
        ]
        logging.info("Opening tunnel to {}.".format(" ".join(command)))
        return subprocess.Popen(command)

    except Exception as e:
        logging.error("FAILED TO OPEN TUNNEL. Exception: {}".format(e))

    return None


def clightning_unix_domain_socket_ssh(rpc_file, rpc_store_dir=None):
    if rpc_store_dir is None:
        rpc_store_dir = os.getcwd()

    local_file = rpc_store_dir + "/lightning-rpc"

    # ssh -nNT -L lightning-rpc:~/.lightning/lightning-rpc config.tunnel_host -p config.tunnel_port
    try:
        command = [
            "ssh",
            "-nNT",
            "-L",
            "{}:{}".format(local_file, rpc_file),
            "{}".format(config.tunnel_host),
            "-p {}".format(config.tunnel_port),
            ]
        logging.info("Opening tunnel to {}.".format(" ".join(command)))
        tunnel_proc = subprocess.Popen(command)
        return tunnel_proc

    except Exception as e:
        logging.error(
            "FAILED TO OPEN UNIX DOMAIN SOCKET OVER SSH. Exception: {}".format(e)
        )

    return None


def rm_lightning_rpc_file():
    if os.path.exists("lightning-rpc"):
        os.remove("lightning-rpc")
    return


def close_tunnels(ssh_processes):
    if ssh_processes is not None:
        for proc in ssh_processes:
            try:
                proc.kill()
            except Exception:
                continue

    if "clightning" in config.payment_methods:
        rm_lightning_rpc_file()
    return


# Open tunnel
def open_tunnels():
    ssh_tunnel_processes = []
    if config.tunnel_host is not None:
        for method in config.payment_methods:
            if method['name'] == "bitcoind":
                ssh_tunnel_processes.append(open_tunnel(config.tunnel_host, method['rpcport']))

            # Also for lnd if enabled
            if method['name'] == "lnd":
                ssh_tunnel_processes.append(open_tunnel(config.tunnel_host, method['lnd_rpcport']))

            # And if clightning is enabled
            if method['name'] == "clightning":
                rm_lightning_rpc_file()
                ssh_tunnel_processes.append(clightning_unix_domain_socket_ssh(method['clightning_rpc_file']))

    return [proc for proc in ssh_tunnel_processes if proc is not None]
